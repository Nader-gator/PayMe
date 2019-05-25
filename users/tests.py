from django.test import TestCase, Client
from .models import User
from datetime import datetime
from django.db.utils import IntegrityError
from dateutil.relativedelta import relativedelta


class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        user_1 = User.objects.create(
            first_name='jonny',
            last_name='john',
            email='test@test.com',
            date_of_birth=datetime.now() - relativedelta(years=19),
        )

        user_2 = User.objects.create(first_name='landlord',
                                     last_name='johnson',
                                     email='test2@test.com',
                                     date_of_birth=datetime.now() -
                                     relativedelta(years=19),
                                     is_landlord=True,
                                     phone_number=123456789)

        user_1.set_password('starwars')
        user_1.save()

    def test_landlord(self):
        user = User.objects.get(first_name='jonny')
        self.assertEqual(user.is_landlord, False,
                         "new user defaults to landlord")
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_active, True)

    def test_userProfile(self):
        user_1 = User.objects.get(first_name='jonny')
        user_2 = User.objects.get(first_name='landlord')
        self.assertTrue(user_1.renter_profile, "a renter profile is created")
        renter_profile = user_1.renter_profile
        self.assertEqual(renter_profile.profile, user_1)

        landlord_profile = user_2.landlord_profile
        self.assertEqual(landlord_profile.profile, user_2)

    def test_emailUnique_check(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(first_name='landlord',
                                last_name='johnson',
                                email='test2@test.com',
                                date_of_birth=datetime.now() -
                                relativedelta(years=19),
                                is_landlord=True)

    def test_birthday(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(
                first_name='landlord',
                last_name='johnson',
                email='test2@test.com',
                date_of_birth=datetime.now(),
            )

    def test_phone_number(self):
        with self.assertRaises(IntegrityError):
            User.objects.create(first_name='landlord',
                                last_name='johnson',
                                email='test2@test.com',
                                date_of_birth=datetime.now() -
                                relativedelta(years=19),
                                phone_number=1234567891)

    def test_login(self):
        login = self.client.login(username='test@test.com',
                                  password='starwars')
        self.assertTrue(login)
