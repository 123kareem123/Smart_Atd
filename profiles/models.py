from django.conf import settings
from django.db import models

from academics.models import Department, ClassSection


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    student_id = models.CharField(
        max_length=30,
        unique=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='students'
    )

    class_section = models.ForeignKey(
        ClassSection,
        on_delete=models.PROTECT,
        related_name='students'
    )

    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class FacultyProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )

    faculty_id = models.CharField(
        max_length=30,
        unique=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='faculty'
    )

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name()}"