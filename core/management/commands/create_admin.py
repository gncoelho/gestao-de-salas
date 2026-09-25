import os
import dotenv
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

USERNAME = "gui.admin"
PASSWORD = "123456"


class Command(BaseCommand):
    help = "Create the admin user gui.admin."

    def handle(self, *args, **options):
        dotenv.load_dotenv()
        env = os.getenv("ENVIRONMENT") or os.getenv("DJANGO_ENV") or os.getenv("ENV")
        if not env or env.lower() not in ("development", "dev"):
            raise CommandError("Superuser creation is only allowed in the development environment.")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=USERNAME,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        user.set_password(PASSWORD)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created admin user {USERNAME}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated admin user {USERNAME}"))
