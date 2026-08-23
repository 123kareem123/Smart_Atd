import secrets

from datetime import timedelta

from django.utils import timezone

from .models import AttendanceSession


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"


def create_attendance_session(teaching_assignment, faculty, period):
    otp = generate_otp()

    now = timezone.now()

    session = AttendanceSession.objects.create(
        teaching_assignment=teaching_assignment,
        faculty=faculty,
        period=period,
        otp=otp,
        otp_created_at=now,
        otp_expires_at=now + timedelta(minutes=5),
        is_active=True,
    )

    return session