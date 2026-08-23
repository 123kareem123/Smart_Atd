from django.conf import settings
from django.db import models

from academics.models import TeachingAssignment


class AttendanceSession(models.Model):
    teaching_assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.PROTECT,
        related_name='attendance_sessions'
    )

    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='attendance_sessions'
    )

    date = models.DateField(auto_now_add=True)

    period = models.PositiveIntegerField()

    otp = models.CharField(
        max_length=6
    )

    otp_created_at = models.DateTimeField(
        auto_now_add=True
    )

    otp_expires_at = models.DateTimeField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.teaching_assignment.subject.code} - "
            f"Period {self.period} - "
            f"{self.date}"
        )

class AttendanceRecord(models.Model):
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    student = models.ForeignKey(
        'profiles.StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PRESENT'
    )

    marked_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'student'],
                name='unique_student_attendance_per_session'
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"