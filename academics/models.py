from django.db import models


# ============================================================
# DEPARTMENT
# ============================================================

class Department(models.Model):

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    def __str__(self):

        return f"{self.name} ({self.code})"


# ============================================================
# CLASS SECTION
# ============================================================

class ClassSection(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='classes'
    )

    year = models.PositiveIntegerField()

    section = models.CharField(
        max_length=10
    )

    def __str__(self):

        return (
            f"{self.department.code} - "
            f"Year {self.year} - "
            f"Section {self.section}"
        )


# ============================================================
# SUBJECT
# ============================================================

class Subject(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='subjects'
    )

    year = models.PositiveIntegerField(
        default=1
    )

    semester = models.PositiveIntegerField(
        default=1
    )

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    def __str__(self):

        return (
            f"{self.code} - "
            f"{self.name}"
        )


# ============================================================
# TEACHING ASSIGNMENT
# ============================================================

class TeachingAssignment(models.Model):

    faculty = models.ForeignKey(
        'profiles.FacultyProfile',
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )

    class_section = models.ForeignKey(
        ClassSection,
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )

    academic_year = models.CharField(
        max_length=20
    )

    semester = models.PositiveIntegerField()

    def __str__(self):

        return (
            f"{self.faculty.faculty_id} - "
            f"{self.subject.code} - "
            f"{self.class_section}"
        )