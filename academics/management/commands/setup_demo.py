from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from academics.models import (
    Department,
    ClassSection,
    Subject,
    TeachingAssignment,
)

from profiles.models import (
    StudentProfile,
    FacultyProfile,
)


User = get_user_model()


class Command(BaseCommand):

    help = "Create SmartAttend demo users and demo academic data"

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "\nSetting up SmartAttend demo data...\n"
            )
        )

        # ============================================================
        # 1. GET CSE DEPARTMENT
        # ============================================================

        try:

            cse = Department.objects.get(
                code="CSE"
            )

        except Department.DoesNotExist:

            self.stdout.write(
                self.style.ERROR(
                    "CSE department not found."
                )
            )

            self.stdout.write(
                "Please import/create departments first."
            )

            return


        self.stdout.write(
            self.style.SUCCESS(
                f"CSE found: {cse.name}"
            )
        )


        # ============================================================
        # 2. GET / CREATE CSE YEAR 3 SECTION C
        # ============================================================

        class_section, created = (
            ClassSection.objects.get_or_create(

                department=cse,

                year=3,

                section="C"

            )
        )


        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "Created CSE Year 3 Section C"
                )
            )

        else:

            self.stdout.write(
                "CSE Year 3 Section C already exists."
            )


        # ============================================================
        # 3. CREATE DEMO STUDENT USER
        # ============================================================

        student_user, created = (
            User.objects.get_or_create(

                username="demo_student",

                defaults={
                    "first_name": "Demo",
                    "last_name": "Student",
                    "role": User.Role.STUDENT,
                }

            )
        )


        student_user.first_name = "Demo"

        student_user.last_name = "Student"

        student_user.role = User.Role.STUDENT

        student_user.set_password(
            "Demo@12345"
        )

        student_user.save()


        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "Created demo_student"
                )
            )

        else:

            self.stdout.write(
                "demo_student already exists."
            )


        # ============================================================
        # 4. CREATE / UPDATE STUDENT PROFILE
        # ============================================================

        student_profile, created = (
            StudentProfile.objects.get_or_create(

                user=student_user,

                defaults={
                    "student_id": "DEMO-STU-001",
                    "department": cse,
                    "class_section": class_section,
                    "year": 3,
                }

            )
        )


        student_profile.student_id = (
            "DEMO-STU-001"
        )

        student_profile.department = cse

        student_profile.class_section = class_section

        student_profile.year = 3

        student_profile.save()


        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "Created Demo Student Profile"
                )
            )

        else:

            self.stdout.write(
                "Demo Student Profile already exists."
            )


        # ============================================================
        # 5. CREATE DEMO FACULTY USER
        # ============================================================

        faculty_user, created = (
            User.objects.get_or_create(

                username="demo_faculty",

                defaults={
                    "first_name": "Demo",
                    "last_name": "Faculty",
                    "role": User.Role.FACULTY,
                }

            )
        )


        faculty_user.first_name = "Demo"

        faculty_user.last_name = "Faculty"

        faculty_user.role = User.Role.FACULTY

        faculty_user.set_password(
            "Demo@12345"
        )

        faculty_user.save()


        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "Created demo_faculty"
                )
            )

        else:

            self.stdout.write(
                "demo_faculty already exists."
            )


        # ============================================================
        # 6. CREATE / UPDATE FACULTY PROFILE
        # ============================================================

        faculty_profile, created = (
            FacultyProfile.objects.get_or_create(

                user=faculty_user,

                defaults={
                    "faculty_id": "DEMO-FAC-001",
                    "department": cse,
                }

            )
        )


        faculty_profile.faculty_id = (
            "DEMO-FAC-001"
        )

        faculty_profile.department = cse

        faculty_profile.save()


        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "Created Demo Faculty Profile"
                )
            )

        else:

            self.stdout.write(
                "Demo Faculty Profile already exists."
            )


        # ============================================================
        # 7. GET YEAR 3 SEMESTER 5 SUBJECTS
        # ============================================================

        subjects = Subject.objects.filter(

            department=cse,

            year=3,

            semester=5

        ).order_by("code")


        self.stdout.write(
            f"\nCSE Year 3 Semester 5 subjects: "
            f"{subjects.count()}"
        )


        # ============================================================
        # 8. CREATE TEACHING ASSIGNMENTS
        # ============================================================

        assignment_count = 0


        for subject in subjects:

            assignment, created = (
                TeachingAssignment.objects.get_or_create(

                    faculty=faculty_profile,

                    subject=subject,

                    class_section=class_section,

                    semester=5,

                    defaults={
                        "academic_year": "2026-27"
                    }

                )
            )


            if created:

                assignment_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned {subject.code} - "
                        f"{subject.name}"
                    )
                )

            else:

                self.stdout.write(
                    f"Assignment already exists: "
                    f"{subject.code}"
                )


        # ============================================================
        # 9. CREATE DEMO ADMIN
        # ============================================================

        admin_user, created = (
            User.objects.get_or_create(

                username="demo_admin",

                defaults={
                    "first_name": "Demo",
                    "last_name": "Admin",
                    "role": User.Role.ADMIN,
                    "is_staff": True,
                    "is_superuser": True,
                }

            )
        )


        admin_user.first_name = "Demo"

        admin_user.last_name = "Admin"

        admin_user.role = User.Role.ADMIN

        admin_user.is_staff = True

        admin_user.is_superuser = True

        admin_user.set_password(
            "Demo@12345"
        )

        admin_user.save()


        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "Created demo_admin"
                )
            )

        else:

            self.stdout.write(
                "demo_admin already exists."
            )


        # ============================================================
        # 10. FINAL MESSAGE
        # ============================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "SMARTATTEND DEMO SETUP COMPLETE"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            "Student Demo:"
        )

        self.stdout.write(
            "  Username: demo_student"
        )

        self.stdout.write(
            "  Password: Demo@12345"
        )

        self.stdout.write("")

        self.stdout.write(
            "Faculty Demo:"
        )

        self.stdout.write(
            "  Username: demo_faculty"
        )

        self.stdout.write(
            "  Password: Demo@12345"
        )

        self.stdout.write("")

        self.stdout.write(
            "Admin Demo:"
        )

        self.stdout.write(
            "  Username: demo_admin"
        )

        self.stdout.write(
            "  Password: Demo@12345"
        )

        self.stdout.write("")

        self.stdout.write(
            f"Teaching assignments created: "
            f"{assignment_count}"
        )