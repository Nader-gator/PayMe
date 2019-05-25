from django.test import TestCase, Client
from django.utils.http import urlencode
from landlord.models import Charge, Rent
from datetime import datetime
from dateutil.relativedelta import relativedelta
from users.models import User
from django.urls import reverse


class RenterTestCase(TestCase):
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
        login = c.login(username=self.renter.email, password=self.password)
        response = c.get(self.renter_url)
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        c = self.client
        login = c.login(username=self.renter.email, password=self.password)
        response = c.get(self.renter_url)
        self.assertTrue(login)
        self.assertIn(self.recurring_charge,
                      response.context['recurring_charges'])
        self.assertIn(self.one_time_charge,
                      response.context['one_time_charges'])

    def test_wrong_dashboard(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        response = c.get(self.landlord_url)
        self.assertEqual(response.context['wrong_person'], 'renter')
        c.login(username=self.landlord.email, password=self.password)
        response = c.get(self.renter_url)
        self.assertEqual(response.context['wrong_person'], 'landlord')

    def test_pay_page_info(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.one_time_charge.id])
        context = c.get(url).context
        context_charge = context['charge']
        self.assertEqual(context_charge, self.one_time_charge)
        due_now = self.one_time_charge.amount - self.one_time_charge.amount_paid
        self.assertEqual(context_charge.due_now, due_now)
        self.assertIsNone(context.get('key'))
        self.assertIsNone(context.get('id'))

    def test_pay_page_post(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.one_time_charge.id])
        context = c.post(url, data={'payment-amount': 200}).context
        self.assertIsNotNone(context.get('key'))
        self.assertIsNotNone(context.get('id'))
        self.one_time_charge.refresh_from_db()
        self.assertIsNotNone(self.one_time_charge.payment_token)

    def test_pay_success(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.one_time_charge.id])
        c.post(url, data={'payment-amount': 200})
        self.one_time_charge.refresh_from_db()
        data = {
            'token': self.one_time_charge.payment_token,
            'charge_id': self.one_time_charge.id,
            'amount': 200 * 100  #cents
        }
        url = reverse('payment-success') + f"?{urlencode(data)}"
        response = c.get(url, follow=True)
        context = response.context
        self.assertRedirects(response, self.renter_url)
        self.one_time_charge.refresh_from_db()
        self.assertEqual(self.one_time_charge.amount_paid, 200)
        self.assertTrue(self.one_time_charge.paid)

    def test_pay_failiure(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        charge_url = reverse('pay-charge', args=[self.one_time_charge.id])
        c.post(charge_url, data={'payment-amount': 200})
        self.one_time_charge.refresh_from_db()
        data = {
            'charge_id': self.one_time_charge.id,
        }
        fail_url = reverse('payment-failed') + f"?{urlencode(data)}"
        response = c.get(fail_url, follow=True)
        context = response.context
        self.assertRedirects(response, charge_url)
        self.one_time_charge.refresh_from_db()
        self.assertEqual(self.one_time_charge.amount_paid, 0)
        self.assertFalse(self.one_time_charge.paid)
