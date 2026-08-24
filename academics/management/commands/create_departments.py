from django.core.management.base import BaseCommand
from academics.models import Department, ClassSection


class Command(BaseCommand):

    help = "Create departments and class sections"

    def handle(self, *args, **options):

        departments = [
            ("Computer Science and Engineering", "CSE"),
            ("Electronics and Communication Engineering", "ECE"),
            ("Electrical and Electronics Engineering", "EEE"),
            ("Mechanical Engineering", "MECH"),
            ("Civil Engineering", "CIV"),
            ("Chemical Engineering", "CHEM"),
            ("Metallurgical Engineering", "MET"),
        ]

        created_departments = 0
        created_sections = 0

        # =====================================================
        # CREATE DEPARTMENTS
        # =====================================================

        for name, code in departments:

            department, created = Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name
                }
            )

            if created:
                created_departments += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created department: {name} ({code})"
                    )
                )

            else:
                self.stdout.write(
                    f"Department already exists: {name} ({code})"
                )

            # =================================================
            # CREATE SECTIONS A, B, C FOR YEARS 1-4
            # =================================================

            for year in range(1, 5):

                for section in ["A", "B", "C"]:

                    class_section, created = (
                        ClassSection.objects.get_or_create(
                            department=department,
                            year=year,
                            section=section
                        )
                    )

                    if created:
                        created_sections += 1

        # =====================================================
        # RESULT
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "ACADEMIC DATA SETUP COMPLETE"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            f"Departments created : {created_departments}"
        )

        self.stdout.write(
            f"Sections created    : {created_sections}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )