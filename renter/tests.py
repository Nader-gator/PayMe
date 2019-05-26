from django.utils.http import urlencode
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from users.tests import GlobalSetup


class RenterTestCase(GlobalSetup):
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
        self.assertRedirects(response, self.renter_url)
        self.one_time_charge.refresh_from_db()
        self.assertEqual(self.one_time_charge.amount_paid, 200)
        self.assertTrue(self.one_time_charge.paid)

    def test_pay_success_with_balance(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.one_time_charge.id])
        c.post(url, data={'payment-amount': 200})
        self.one_time_charge.refresh_from_db()
        data = {
            'token': self.one_time_charge.payment_token,
            'charge_id': self.one_time_charge.id,
            'amount': 100 * 100  #cents
        }
        url = reverse('payment-success') + f"?{urlencode(data)}"
        response = c.get(url, follow=True)
        context = response.context
        pay_url = reverse('pay-charge', args=[self.one_time_charge.id])
        self.assertRedirects(response, pay_url)
        self.one_time_charge.refresh_from_db()
        self.assertEqual(self.one_time_charge.amount_paid, 100)
        self.assertFalse(self.one_time_charge.paid)
        self.assertEqual(context.get('charge').due_now, 100)

    def test_pay_failure(self):
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
        self.assertRedirects(response, charge_url)
        self.one_time_charge.refresh_from_db()
        self.assertEqual(self.one_time_charge.amount_paid, 0)
        self.assertFalse(self.one_time_charge.paid)

    def test_pay_success_recurring(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.recurring_charge.id])
        c.post(url, data={'payment-amount': 2000})
        self.recurring_charge.refresh_from_db()
        data = {
            'token': self.recurring_charge.payment_token,
            'charge_id': self.recurring_charge.id,
            'amount': 2000 * 100  #cents
        }
        url = reverse('payment-success') + f"?{urlencode(data)}"
        response = c.get(url, follow=True)
        self.assertRedirects(response, self.renter_url)
        new_due_date = self.recurring_charge.due_date + relativedelta(months=1)
        self.recurring_charge.refresh_from_db()
        self.assertEqual(self.recurring_charge.due_date, new_due_date)
        self.assertEqual(self.recurring_charge.amount_paid, 0)
        self.assertFalse(self.one_time_charge.paid)

    def test_pay_success_recurring_with_balance(self):
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.recurring_charge.id])
        c.post(url, data={'payment-amount': 1800})
        self.recurring_charge.refresh_from_db()
        data = {
            'token': self.recurring_charge.payment_token,
            'charge_id': self.recurring_charge.id,
            'amount': 1800 * 100  #cents
        }
        url = reverse('payment-success') + f"?{urlencode(data)}"
        response = c.get(url, follow=True)
        pay_url = reverse('pay-charge', args=[self.recurring_charge.id])
        self.assertRedirects(response, pay_url)
        old_due_date = self.recurring_charge.due_date
        self.recurring_charge.refresh_from_db()
        self.assertEqual(self.recurring_charge.due_date, old_due_date)
        self.assertEqual(self.recurring_charge.amount_paid, 1800)
        self.assertFalse(self.one_time_charge.paid)

    def test_pay_success_recurring_last_month(self):
        self.recurring_charge.due_date += relativedelta(months=10)
        self.recurring_charge.save()
        c = self.client
        c.login(username=self.renter.email, password=self.password)
        url = reverse('pay-charge', args=[self.recurring_charge.id])
        c.post(url, data={'payment-amount': 2000})
        self.recurring_charge.refresh_from_db()
        data = {
            'token': self.recurring_charge.payment_token,
            'charge_id': self.recurring_charge.id,
            'amount': 2000 * 100  #cents
        }
        url = reverse('payment-success') + f"?{urlencode(data)}"
        response = c.get(url, follow=True)
        self.assertRedirects(response, self.renter_url)
        self.recurring_charge.refresh_from_db()
        self.assertTrue(self.recurring_charge.paid)
