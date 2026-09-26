import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from delivery.models import Customer


class Command(BaseCommand):
    help = (
        'Idempotently create admin accounts from environment variables, '
        'so a shell is never needed. Skips anything that is not configured.'
    )

    def handle(self, *args, **options):
        self.ensure_django_superuser()
        self.ensure_app_admin()

    def ensure_django_superuser(self):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
        if not username:
            self.stdout.write('DJANGO_SUPERUSER_USERNAME not set; skipping Django superuser.')
            return

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is None and not password:
            raise CommandError(
                'DJANGO_SUPERUSER_USERNAME is set but DJANGO_SUPERUSER_PASSWORD is missing; '
                'cannot create the superuser.'
            )

        if user is None:
            user = User(username=username, is_staff=True, is_superuser=True, is_active=True)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Django superuser "{username}" created.'))
            return

        changed = False
        if not user.is_superuser or not user.is_staff:
            user.is_superuser = True
            user.is_staff = True
            changed = True
        if password and not user.check_password(password):
            user.set_password(password)
            changed = True
        if changed:
            user.save()
        self.stdout.write(self.style.SUCCESS(f'Django superuser "{username}" ready.'))

    def ensure_app_admin(self):
        username = os.environ.get('APP_ADMIN_USERNAME', '').strip()
        password = os.environ.get('APP_ADMIN_PASSWORD', '')
        if not username:
            self.stdout.write('APP_ADMIN_USERNAME not set; skipping app admin.')
            return

        user = Customer.objects.filter(username__iexact=username).first()
        if user is None:
            if not password:
                raise CommandError(
                    'APP_ADMIN_USERNAME is set but APP_ADMIN_PASSWORD is missing; '
                    'cannot create the app admin.'
                )
            user = Customer(username=username, is_admin=True)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'App admin "{username}" created.'))
            return

        changed = False
        if not user.is_admin:
            user.is_admin = True
            changed = True
        if password and not user.check_password(password):
            user.set_password(password)
            changed = True
        if changed:
            user.save()
        self.stdout.write(self.style.SUCCESS(f'App admin "{username}" ready.'))
