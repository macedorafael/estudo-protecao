import os
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, User
from app.schemas import StudentCreate, StudentUpdate, StudentOut, StudentDetail
from app.auth import require_professor, require_any, get_current_user
from app.services.face_service import encode_face_from_bytes

router = APIRouter(prefix="/api/students", tags=["students"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.get("", response_model=list[StudentOut])
def list_students(
    active: bool = True,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    return db.query(Student).filter(Student.active == active).order_by(Student.name).all()


@router.post("", response_model=StudentOut)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentDetail)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")

    # Aluno só pode ver o próprio perfil
    if current_user.role.value == "aluno":
        if not current_user.student or current_user.student.id != student_id:
            raise HTTPException(403, "Acesso não autorizado")

    result = StudentDetail.model_validate(student)
    result.attendance_count = len(student.attendance)
    result.belt_history = student.belt_history
    return result


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")
    student.active = False
    db.commit()


@router.post("/{student_id}/photo", response_model=StudentOut)
async def upload_student_photo(
    student_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")

    contents = await file.read()
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename or '.jpg')[1]}"
    photo_dir = os.path.join(UPLOAD_DIR, "photos")
    os.makedirs(photo_dir, exist_ok=True)
    photo_path = os.path.join(photo_dir, filename)

    with open(photo_path, "wb") as f:
        f.write(contents)

    encoding = encode_face_from_bytes(contents)
    if encoding is None:
        os.remove(photo_path)
        raise HTTPException(400, "Nenhum rosto detectado na foto. Use uma foto com o rosto bem visível.")

    student.photo_path = photo_path
    student.face_encoding = json.dumps(encoding)
    db.commit()
    db.refresh(student)
    return student
