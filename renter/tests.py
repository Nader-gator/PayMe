from django.test import TestCase, Client
from landlord.models import Charge, Rent
from datetime import datetime
from dateutil.relativedelta import relativedelta
from users.models import User


class RenterTestCase(TestCase):
    def setUp(self):
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

        self.renter.set_password('starwars')
        self.renter.save()
        self.landlord.set_password('starwars')
        self.landlord.save()

        self.rent = Rent.objects.create(landlord=self.landlord_profile,
                                        name='main_rent')

        self.renter_profile.rent = self.rent
        self.renter_profile.save()

        self.recurring_charge = Charge.objects.create(
            rent=self.rent,
            title='recurring_charge',
            due_date=datetime.now() + relativedelta(days=10),
            recurring=True,
            recurring_until=datetime.now() + relativedelta(years=1),
            amount=2000,
        )
        self.one_time_charge = Charge.objects.create(rent=self.rent,
                                                     title='onetime_charge',
                                                     due_date=datetime.now() +
                                                     relativedelta(days=10),
                                                     amount=200)

    def test_dashboard(self):
        c = self.client
        login = c.login(username='test@test.com', password='starwars')
        response = c.get('/renter/')
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        c = self.client
        login = c.login(username='test@test.com', password='starwars')
        response = c.get('/renter/')
        self.assertTrue(login)
        self.assertIn(self.recurring_charge,
                      response.context['recurring_charges'])
        self.assertIn(self.one_time_charge,
                      response.context['one_time_charges'])

    def test_wrong_dashboard(self):
        c = self.client
        c.login(username='test@test.com', password='starwars')
        response = c.get('/landlord/')
        self.assertEqual(response.context['wrong_person'], 'renter')
        c.login(username='test2@test.com', password='starwars')
        response = c.get('/renter/')
        self.assertEqual(response.context['wrong_person'], 'landlord')
