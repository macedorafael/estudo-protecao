from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

from app.models import UserRole, Belt, FeeStatus


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.aluno


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Students ──────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str
    belt: Belt = Belt.white
    degree: int = 0
    enrollment_date: Optional[date] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    user_id: Optional[int] = None

    @field_validator("degree")
    @classmethod
    def degree_range(cls, v: int) -> int:
        if not 0 <= v <= 4:
            raise ValueError("Grau deve ser entre 0 e 4")
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    belt: Optional[Belt] = None
    degree: Optional[int] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    active: Optional[bool] = None


class StudentOut(BaseModel):
    id: int
    name: str
    belt: Belt
    degree: int
    enrollment_date: date
    birth_date: Optional[date]
    phone: Optional[str]
    photo_path: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentDetail(StudentOut):
    belt_history: list["BeltHistoryOut"] = []
    attendance_count: int = 0


# ── Belt History ──────────────────────────────────────────────────────────────

class BeltPromote(BaseModel):
    belt: Belt
    degree: int
    awarded_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("degree")
    @classmethod
    def degree_range(cls, v: int) -> int:
        if not 0 <= v <= 4:
            raise ValueError("Grau deve ser entre 0 e 4")
        return v


class BeltHistoryOut(BaseModel):
    id: int
    belt: Belt
    degree: int
    awarded_date: date
    notes: Optional[str]
    professor_id: int

    model_config = {"from_attributes": True}


# ── Training Sessions ─────────────────────────────────────────────────────────

class AttendanceOut(BaseModel):
    student_id: int
    student_name: str
    confidence_score: Optional[float]

    model_config = {"from_attributes": True}


class UnidentifiedFaceOut(BaseModel):
    id: int
    face_image_path: str

    model_config = {"from_attributes": True}


class SessionResult(BaseModel):
    session_id: int
    date: date
    recognized: list[AttendanceOut]
    unidentified: list[UnidentifiedFaceOut]


class IdentifyFaceRequest(BaseModel):
    face_id: int
    student_id: int


class SessionOut(BaseModel):
    id: int
    professor_id: int
    date: date
    notes: Optional[str]
    created_at: datetime
    attendance_count: int = 0

    model_config = {"from_attributes": True}


# ── Fees ──────────────────────────────────────────────────────────────────────

class FeePlanCreate(BaseModel):
    amount: float
    due_day: int
    payment_method: Optional[str] = None

    @field_validator("due_day")
    @classmethod
    def due_day_range(cls, v: int) -> int:
        if not 1 <= v <= 31:
            raise ValueError("Dia de vencimento deve ser entre 1 e 31")
        return v


class FeePlanOut(BaseModel):
    id: int
    student_id: int
    amount: float
    due_day: int
    payment_method: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    fee_plan_id: int
    student_id: int
    month_reference: str  # YYYY-MM
    amount_paid: float
    payment_date: Optional[date] = None


class PaymentOut(BaseModel):
    id: int
    fee_plan_id: int
    student_id: int
    month_reference: str
    amount_paid: Optional[float]
    payment_date: Optional[date]
    status: FeeStatus

    model_config = {"from_attributes": True}
