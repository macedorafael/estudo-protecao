from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student, BeltHistory, User
from app.schemas import BeltPromote, BeltHistoryOut
from app.auth import require_professor

router = APIRouter(prefix="/api/students", tags=["belts"])


@router.get("/{student_id}/belts", response_model=list[BeltHistoryOut])
def get_belt_history(
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_professor),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")
    return sorted(student.belt_history, key=lambda h: h.awarded_date, reverse=True)


@router.post("/{student_id}/belts", response_model=BeltHistoryOut)
def promote_belt(
    student_id: int,
    data: BeltPromote,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_professor),
):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Aluno não encontrado")

    awarded = data.awarded_date or date.today()

    history = BeltHistory(
        student_id=student_id,
        belt=data.belt,
        degree=data.degree,
        awarded_date=awarded,
        professor_id=current_user.id,
        notes=data.notes,
    )
    db.add(history)

    # Update current belt/degree on student
    student.belt = data.belt
    student.degree = data.degree
    db.commit()
    db.refresh(history)
    return history
