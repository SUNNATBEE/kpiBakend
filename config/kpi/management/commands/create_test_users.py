"""
Django management command to create test users for development.
Usage: python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test users for development and testing'

    def handle(self, *args, **options):
        # Test user 1: sunnatbek
        user1, created1 = User.objects.get_or_create(
            username='sunnatbek',
            defaults={
                'email': 'sunnatbek@gmail.com',
                'first_name': 'Sunnatbek',
                'last_name': 'Toshmatov',
                'is_active': True,
                'is_manager': False,
            }
        )
        if created1:
            user1.set_password('sunnatbek123')
            user1.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ User "{user1.username}" yaratildi')
            )
        else:
            user1.set_password('sunnatbek123')
            user1.save()
            self.stdout.write(
                self.style.WARNING(f'⚠️  User "{user1.username}" allaqachon mavjud, parol yangilandi')
            )

        # Test user 2: akmal
        user2, created2 = User.objects.get_or_create(
            username='akmal',
            defaults={
                'email': 'akmal@gmail.com',
                'first_name': 'Akmal',
                'last_name': 'Karimov',
                'is_active': True,
                'is_manager': False,
            }
        )
        if created2:
            user2.set_password('akmal123')
            user2.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ User "{user2.username}" yaratildi')
            )
        else:
            user2.set_password('akmal123')
            user2.save()
            self.stdout.write(
                self.style.WARNING(f'⚠️  User "{user2.username}" allaqachon mavjud, parol yangilandi')
            )

        # Test user 3: validator (manager)
        user3, created3 = User.objects.get_or_create(
            username='validator',
            defaults={
                'email': 'validator@gmail.com',
                'first_name': 'Validator',
                'last_name': 'User',
                'is_active': True,
                'is_manager': True,  # Validator bo'lishi uchun
            }
        )
        if created3:
            user3.set_password('validator123')
            user3.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ User "{user3.username}" (Validator) yaratildi')
            )
        else:
            user3.set_password('validator123')
            user3.save()
            self.stdout.write(
                self.style.WARNING(f'⚠️  User "{user3.username}" allaqachon mavjud, parol yangilandi')
            )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Barcha test userlar tayyor!')
        )
        self.stdout.write('\n📋 Test userlar:')
        self.stdout.write('   1. Username: sunnatbek | Password: sunnatbek123')
        self.stdout.write('   2. Username: akmal | Password: akmal123')
        self.stdout.write('   3. Username: validator | Password: validator123 (Validator)')

