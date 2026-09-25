from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

USERNAME = "gui.admin"
PASSWORD = "123456"


class Command(BaseCommand):
    help = "Create the admin user gui.admin."

    def handle(self, *args, **options):
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
