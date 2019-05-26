from django.test import TestCase, Client
from .models import User
from datetime import datetime
from django.db.utils import IntegrityError
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from landlord.models import Rent, Charge


class GlobalSetup(TestCase):
    def setUp(self):
        self.landlord_url = reverse('landlord-dashboard')
        self.renter_url = reverse('renter-dashboard')
        self.password = 'starwars'
        self.client = Client()
        self.renter = User.objects.create(
            first_name='jonny',
            last_name='john',
            email='test@test.com',
            date_of_birth=datetime.now() - relativedelta(years=19),
        )

        self.landlord = User.objects.create(first_name='landlord',
                                            last_name='johnson',
                                            email='test2@test.com',
                                            date_of_birth=datetime.now() -
                                            relativedelta(years=19),
                                            is_landlord=True,
                                            phone_number=123456789)
        self.renter_profile = self.renter.renter_profile
        self.landlord_profile = self.landlord.landlord_profile

        self.renter.set_password(self.password)
        self.renter.save()
        self.landlord.set_password(self.password)
        self.landlord.save()

        self.rent = Rent.objects.create(landlord=self.landlord_profile,
                                        name='main_rent')

        self.renter_profile.rent = self.rent
        self.renter_profile.save()

        self.recurring_charge = Charge.objects.create(
            rent=self.rent,
            title='recurring_charge',
            due_date=datetime.now().date() + relativedelta(days=10),
            recurring=True,
            recurring_until=datetime.now().date() + relativedelta(years=1),
            amount=2000,
        )
        self.one_time_charge = Charge.objects.create(rent=self.rent,
                                                     title='onetime_charge',
                                                     due_date=datetime.now() +
                                                     relativedelta(days=10),
                                                     amount=200)


class UserTestCase(GlobalSetup):
    def test_home_page(self):
        c = self.client
        response = c.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirect(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        response = c.get(reverse('homepage-dashboard'), follow=True)
        self.assertRedirects(response, reverse('renter-dashboard'))
        c.login(username=self.landlord.email, password=self.password)
        response = c.get(reverse('homepage-dashboard'), follow=True)
        self.assertRedirects(response, reverse('landlord-dashboard'))

    def test_user_creation(self):
        c = self.client
        c.post(reverse('register'),
               data={
                   'first_name': 'homer',
                   'last_name': 'simpson',
                   'email': 'homer@simpson.com',
                   'date_of_birth':
                   datetime.now().date() - relativedelta(years=19),
                   'password1': 'starwars',
                   'password2': 'starwars'
               })
        self.assertIsNotNone(User.objects.get(email='homer@simpson.com'))

    def test_user_update(self):
        c = self.client
        login = self.client.login(username=self.renter.email,
                                  password=self.password)
        response = c.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        c.post(reverse('profile'),
               data={
                   'first_name':
                   'jonny',
                   'last_name':
                   'john',
                   'email':
                   'fresh@test.com',
                   'date_of_birth':
                   datetime.now().date() - relativedelta(years=19),
               })
        self.renter.refresh_from_db()
        self.assertEqual(self.renter.email, 'fresh@test.com')

    def test_landlord(self):
        user = self.renter
        self.assertEqual(user.is_landlord, False,
                         "new user defaults to landlord")
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_active, True)

    def test_userProfile(self):
        user_1 = self.renter
        user_2 = self.landlord
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
        login = self.client.login(username=self.renter.email,
                                  password=self.password)
        self.assertTrue(login)
