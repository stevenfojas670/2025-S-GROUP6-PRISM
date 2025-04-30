from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User  # your custom User model


class Command(BaseCommand):
    help = "Fix user passwords that were added directly to the database without hashing"

    def handle(self, *args, **options):
        users = User.objects.all()
        fixed_count = 0

        for user in users:
            if not user.password.startswith("pbkdf2_"):
                self.stdout.write(f"Fixing password for: {user.email}")
                user.password = make_password(
                    "password123!"
                )  # Set your default password
                user.save()
                fixed_count += 1

        self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} user(s)"))
