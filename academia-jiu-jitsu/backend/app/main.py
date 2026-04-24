import logging
import os
from contextlib import asynccontextmanager
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.models import Base, FeePayment, FeeStatus, Student, FeePlan, User
from app.routers import auth, students, attendance, belts, fees
from app.services.notification_service import notify_overdue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def check_overdue_fees():
    """Daily job: mark overdue fees and send notifications."""
    db: Session = SessionLocal()
    try:
        today = date.today()
        current_month = today.strftime("%Y-%m")

        # Get all active fee plans
        plans = db.query(FeePlan).filter(FeePlan.active == True).all()
        for plan in plans:
            student: Student = plan.student
            if not student.active:
                continue

            # Check if payment exists for current month
            payment = db.query(FeePayment).filter(
                FeePayment.fee_plan_id == plan.id,
                FeePayment.month_reference == current_month,
            ).first()

            if not payment:
                # Create pending/overdue record
                is_overdue = today.day > plan.due_day
                status = FeeStatus.overdue if is_overdue else FeeStatus.pending
                payment = FeePayment(
                    fee_plan_id=plan.id,
                    student_id=student.id,
                    month_reference=current_month,
                    status=status,
                )
                db.add(payment)
            elif payment.status == FeeStatus.pending and today.day > plan.due_day:
                payment.status = FeeStatus.overdue

            if payment.status == FeeStatus.overdue:
                user: User | None = student.user
                email = user.email if user else None
                notify_overdue(student.name, email, student.phone, current_month, plan.amount)

        db.commit()
    except Exception as e:
        logger.error("Erro no job de inadimplência: %s", e)
        db.rollback()
    finally:
        db.close()


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    scheduler.add_job(check_overdue_fees, "cron", hour=8, minute=0)
    scheduler.start()
    logger.info("Scheduler iniciado")

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Academia Jiu-Jitsu API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(belts.router)
app.include_router(fees.router)


@app.get("/")
def health():
    return {"status": "ok", "service": "Academia Jiu-Jitsu API"}
