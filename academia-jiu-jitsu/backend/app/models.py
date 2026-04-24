from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    professor = "professor"
    aluno = "aluno"


class Belt(str, enum.Enum):
    white = "white"
    grey = "grey"
    yellow = "yellow"
    orange = "orange"
    green = "green"
    blue = "blue"
    purple = "purple"
    brown = "brown"
    black = "black"


class FeeStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.aluno)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    sessions: Mapped[list["TrainingSession"]] = relationship("TrainingSession", back_populates="professor")
    belt_promotions: Mapped[list["BeltHistory"]] = relationship("BeltHistory", back_populates="professor")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    belt: Mapped[Belt] = mapped_column(SAEnum(Belt), default=Belt.white)
    degree: Mapped[int] = mapped_column(Integer, default=0)
    enrollment_date: Mapped[date] = mapped_column(Date, default=date.today)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    face_encoding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of floats
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[Optional[User]] = relationship("User", back_populates="student")
    attendance: Mapped[list["Attendance"]] = relationship("Attendance", back_populates="student")
    belt_history: Mapped[list["BeltHistory"]] = relationship("BeltHistory", back_populates="student")
    fee_plans: Mapped[list["FeePlan"]] = relationship("FeePlan", back_populates="student")
    fee_payments: Mapped[list["FeePayment"]] = relationship("FeePayment", back_populates="student")
    identified_faces: Mapped[list["UnidentifiedFace"]] = relationship(
        "UnidentifiedFace", back_populates="identified_as", foreign_keys="UnidentifiedFace.identified_as_student_id"
    )


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    professor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    training_photo_path: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    professor: Mapped[User] = relationship("User", back_populates="sessions")
    attendance: Mapped[list["Attendance"]] = relationship("Attendance", back_populates="session")
    unidentified_faces: Mapped[list["UnidentifiedFace"]] = relationship("UnidentifiedFace", back_populates="session")


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[TrainingSession] = relationship("TrainingSession", back_populates="attendance")
    student: Mapped[Student] = relationship("Student", back_populates="attendance")


class UnidentifiedFace(Base):
    __tablename__ = "unidentified_faces"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("training_sessions.id"))
    face_image_path: Mapped[str] = mapped_column(String(300))
    identified_as_student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[TrainingSession] = relationship("TrainingSession", back_populates="unidentified_faces")
    identified_as: Mapped[Optional[Student]] = relationship(
        "Student", back_populates="identified_faces", foreign_keys=[identified_as_student_id]
    )


class BeltHistory(Base):
    __tablename__ = "belt_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    belt: Mapped[Belt] = mapped_column(SAEnum(Belt))
    degree: Mapped[int] = mapped_column(Integer)
    awarded_date: Mapped[date] = mapped_column(Date, default=date.today)
    professor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    student: Mapped[Student] = relationship("Student", back_populates="belt_history")
    professor: Mapped[User] = relationship("User", back_populates="belt_promotions")


class FeePlan(Base):
    __tablename__ = "fee_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    amount: Mapped[float] = mapped_column(Float)
    due_day: Mapped[int] = mapped_column(Integer)  # 1-31
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped[Student] = relationship("Student", back_populates="fee_plans")
    payments: Mapped[list["FeePayment"]] = relationship("FeePayment", back_populates="fee_plan")


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    fee_plan_id: Mapped[int] = mapped_column(ForeignKey("fee_plans.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    month_reference: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    amount_paid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[FeeStatus] = mapped_column(SAEnum(FeeStatus), default=FeeStatus.pending)

    fee_plan: Mapped[FeePlan] = relationship("FeePlan", back_populates="payments")
    student: Mapped[Student] = relationship("Student", back_populates="fee_payments")
