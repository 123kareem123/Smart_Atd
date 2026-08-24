from django.core.management.base import BaseCommand
from academics.models import Department


class Command(BaseCommand):

    help = "Create required engineering departments"

    def handle(self, *args, **options):

        departments = [
            ("Computer Science and Engineering", "CSE"),
            ("Electronics and Communication Engineering", "ECE"),
            ("Electrical and Electronics Engineering", "EEE"),
            ("Mechanical Engineering", "MECH"),
            ("Civil Engineering", "CIVIL"),
            ("Information Technology", "IT"),
        ]

        created_count = 0

        for name, code in departments:

            department, created = Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created department: {name} ({code})"
                    )
                )
            else:
                self.stdout.write(
                    f"Department already exists: {name} ({code})"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Department setup complete. Created: {created_count}"
            )
        )