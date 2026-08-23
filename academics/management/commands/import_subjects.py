import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from academics.models import Department, Subject


class Command(BaseCommand):

    help = "Import subjects from Engineering CSV file"

    def handle(self, *args, **kwargs):

        # =====================================================
        # CSV FILE PATH
        # =====================================================

        csv_path = os.path.join(
            settings.BASE_DIR,
            "Engineering_All_Subjects_Year_Semester_Branch.csv"
        )

        # =====================================================
        # CHECK CSV EXISTS
        # =====================================================

        if not os.path.exists(csv_path):

            self.stdout.write(
                self.style.ERROR(
                    f"CSV file not found:\n{csv_path}"
                )
            )

            return

        # =====================================================
        # COUNTERS
        # =====================================================

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # =====================================================
        # OPEN CSV
        # =====================================================

        with open(
            csv_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            # =================================================
            # CHECK CSV COLUMNS
            # =================================================

            required_columns = {
                "year",
                "semester",
                "department_code",
                "subject_code",
                "subject_name",
            }

            if not required_columns.issubset(reader.fieldnames):

                self.stdout.write(
                    self.style.ERROR(
                        "CSV columns are incorrect."
                    )
                )

                self.stdout.write(
                    f"Found columns: {reader.fieldnames}"
                )

                return

            # =================================================
            # READ EACH ROW
            # =================================================

            for row in reader:

                year = row["year"].strip()
                semester = row["semester"].strip()
                department_code = row[
                    "department_code"
                ].strip()
                subject_code = row[
                    "subject_code"
                ].strip()
                subject_name = row[
                    "subject_name"
                ].strip()

                # =============================================
                # CHECK EMPTY VALUES
                # =============================================

                if not (
                    year
                    and semester
                    and department_code
                    and subject_code
                    and subject_name
                ):

                    skipped_count += 1

                    self.stdout.write(
                        self.style.WARNING(
                            "Skipped row because "
                            "some values are empty."
                        )
                    )

                    continue

                # =============================================
                # FIND DEPARTMENT
                # =============================================

                try:

                    department = Department.objects.get(
                        code=department_code
                    )

                except Department.DoesNotExist:

                    skipped_count += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Department not found: "
                            f"{department_code} "
                            f"for subject "
                            f"{subject_code}"
                        )
                    )

                    continue

                # =============================================
                # CREATE OR UPDATE SUBJECT
                # =============================================

                subject, created = (
                    Subject.objects.update_or_create(

                        code=subject_code,

                        defaults={
                            "department": department,
                            "year": int(year),
                            "semester": int(semester),
                            "name": subject_name,
                        }
                    )
                )

                # =============================================
                # COUNT RESULT
                # =============================================

                if created:

                    created_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added: "
                            f"{subject_code} - "
                            f"{subject_name}"
                        )
                    )

                else:

                    updated_count += 1

        # =====================================================
        # FINAL RESULT
        # =====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "       SUBJECT IMPORT COMPLETED"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            f"Created : {created_count}"
        )

        self.stdout.write(
            f"Updated : {updated_count}"
        )

        self.stdout.write(
            f"Skipped : {skipped_count}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )