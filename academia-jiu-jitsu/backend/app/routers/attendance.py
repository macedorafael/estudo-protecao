import json
import os
import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, TrainingSession, Attendance, UnidentifiedFace, User
from app.schemas import SessionResult, AttendanceOut, UnidentifiedFaceOut, SessionOut, IdentifyFaceRequest
from app.auth import require_professor, get_current_user
from app.services.face_service import detect_and_crop_faces, get_face_encoding, match_face, save_face_crop

router = APIRouter(prefix="/api/sessions", tags=["attendance"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.post("", response_model=SessionResult)
async def create_session(
    file: UploadFile = File(...),
    notes: str = Form(default=""),
    session_date: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    contents = await file.read()

    # Save training photo
    photo_dir = os.path.join(UPLOAD_DIR, "sessions")
    os.makedirs(photo_dir, exist_ok=True)
    photo_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename or '.jpg')[1]}"
    photo_path = os.path.join(photo_dir, photo_filename)
    with open(photo_path, "wb") as f:
        f.write(contents)

    parsed_date = date.today()
    if session_date:
        try:
            parsed_date = date.fromisoformat(session_date)
        except ValueError:
            pass

    session = TrainingSession(
        professor_id=current_user.id,
        date=parsed_date,
        training_photo_path=photo_path,
        notes=notes or None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Load all active students with face encodings
    students = db.query(Student).filter(Student.active == True, Student.face_encoding.isnot(None)).all()
    students_encodings = [
        (s.id, json.loads(s.face_encoding)) for s in students if s.face_encoding
    ]

    # Detect faces in the training photo
    faces = detect_and_crop_faces(contents)

    recognized: list[AttendanceOut] = []
    unidentified: list[UnidentifiedFaceOut] = []
    recognized_student_ids: set[int] = set()

    for face_array, region in faces:
        encoding = get_face_encoding(face_array)
        if encoding is None:
            continue

        match = match_face(encoding, students_encodings)
        if match:
            student_id, confidence = match
            if student_id in recognized_student_ids:
                continue  # already marked present
            recognized_student_ids.add(student_id)

            att = Attendance(session_id=session.id, student_id=student_id, confidence_score=confidence)
            db.add(att)

            student = db.get(Student, student_id)
            recognized.append(AttendanceOut(
                student_id=student_id,
                student_name=student.name,
                confidence_score=confidence,
            ))
        else:
            face_path = save_face_crop(face_array, session.id)
            unid = UnidentifiedFace(session_id=session.id, face_image_path=face_path)
            db.add(unid)
            db.flush()
            unidentified.append(UnidentifiedFaceOut(id=unid.id, face_image_path=face_path))

    db.commit()

    return SessionResult(
        session_id=session.id,
        date=session.date,
        recognized=recognized,
        unidentified=unidentified,
    )


@router.get("", response_model=list[SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    sessions = db.query(TrainingSession).order_by(TrainingSession.date.desc()).all()
    result = []
    for s in sessions:
        out = SessionOut.model_validate(s)
        out.attendance_count = len(s.attendance)
        result.append(out)
    return result


@router.get("/{session_id}", response_model=SessionResult)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    session = db.get(TrainingSession, session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")

    recognized = [
        AttendanceOut(
            student_id=att.student_id,
            student_name=att.student.name,
            confidence_score=att.confidence_score,
        )
        for att in session.attendance
    ]
    unidentified = [
        UnidentifiedFaceOut(id=u.id, face_image_path=u.face_image_path)
        for u in session.unidentified_faces
        if u.identified_as_student_id is None
    ]
    return SessionResult(
        session_id=session.id,
        date=session.date,
        recognized=recognized,
        unidentified=unidentified,
    )


@router.post("/{session_id}/identify")
def identify_face(
    session_id: int,
    data: IdentifyFaceRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    """Professor identifies an unrecognized face and marks attendance."""
    session = db.get(TrainingSession, session_id)
    if not session:
        raise HTTPException(404, "Sessão não encontrada")

    face = db.get(UnidentifiedFace, data.face_id)
    if not face or face.session_id != session_id:
        raise HTTPException(404, "Face não encontrada nesta sessão")

    student = db.get(Student, data.student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")

    face.identified_as_student_id = data.student_id

    # Check if attendance already exists for this student in this session
    existing = db.query(Attendance).filter(
        Attendance.session_id == session_id,
        Attendance.student_id == data.student_id,
    ).first()
    if not existing:
        db.add(Attendance(session_id=session_id, student_id=data.student_id, confidence_score=None))

    db.commit()
    return {"ok": True, "student_name": student.name}
