from landlord.models import Rent
from django.urls import reverse
from users.tests import GlobalSetup
from users.models import User
from datetime import datetime
from dateutil.relativedelta import relativedelta
from landlord.models import Charge


class LandlordTestCase(GlobalSetup):
    def test_dashboard(self):
        c = self.client
        login = c.login(username=self.landlord.email, password=self.password)
        response = c.get(self.landlord_url)
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        c = self.client
        login = c.login(username=self.landlord.email, password=self.password)
        response = c.get(self.landlord_url)
        self.assertTrue(login)
        self.assertIn(self.rent, response.context.get('rents'))

    def test_new_rent(self):
        c = self.client
        c.login(username=self.landlord.email, password=self.password)
        response = c.post(reverse('new-rent'), data={'name': 'rent2'})
        self.assertRedirects(response, self.landlord_url)
        new_rent = Rent.objects.get(name='rent2')
        self.assertIsNotNone(new_rent)
        self.assertEqual(new_rent.landlord.profile, self.landlord)

    def test_show_rent(self):
        c = self.client
        c.login(username=self.landlord.email, password=self.password)
        context = c.post(reverse('show-rent', args=[self.rent.id])).context
        self.assertEqual(context.get('rent'), self.rent)
        self.assertIn(self.renter.renter_profile, context.get('renters'))
        self.assertIn(self.one_time_charge, context.get('one_time_charges'))
        self.assertIn(self.recurring_charge, context.get('recurring_charges'))

    def test_add_renter(self):
        c = self.client
        c.login(username=self.landlord.email, password=self.password)
        new_user = User.objects.create(
            first_name='jack',
            last_name='johnson',
            email='test3@test.com',
            date_of_birth=datetime.now() - relativedelta(years=19),
        )
        response = c.post(reverse('show-rent', args=[self.rent.id]),
                          data={'email': new_user.email})
        self.assertIn(self.renter.renter_profile,
                      response.context.get('renters'))
        self.assertIn(new_user.renter_profile, response.context.get('renters'))
        new_landlord_user = User.objects.create(first_name='bojack',
                                                last_name='johnson',
                                                email='test4@test.com',
                                                date_of_birth=datetime.now() -
                                                relativedelta(years=19),
                                                is_landlord=True)
        response = c.post(reverse('show-rent', args=[self.rent.id]),
                          data={'email': new_landlord_user.email})
        self.assertNotIn(new_landlord_user.landlord_profile,
                         response.context.get('renters'))

    def test_new_charge(self):
        c = self.client
        c.login(username=self.landlord.email, password=self.password)
        response = c.get(reverse('new-charge', args=[self.rent.id]))
        self.assertEqual(response.context.get('rent'), self.rent)
        post_response = c.post(reverse('new-charge', args=[self.rent.id]),
                               data={
                                   'amount':
                                   200,
                                   'title':
                                   'test_charge_1',
                                   'due_date':
                                   datetime.now().date() +
                                   relativedelta(days=20)
                               })
        self.assertRedirects(post_response,
                             reverse('show-rent', args=[self.rent.id]))
        new_charge = Charge.objects.get(title='test_charge_1')
        self.assertIsNotNone(new_charge)
        self.assertFalse(new_charge.recurring)

    def test_new_recurring_charge(self):
        c = self.client
        c.login(username=self.landlord.email, password=self.password)
        response = c.get(reverse('new-charge', args=[self.rent.id]))
        self.assertEqual(response.context.get('rent'), self.rent)
        post_response = c.post(
            reverse('new-charge', args=[self.rent.id]),
            data={
                'amount':
                200,
                'title':
                'test_charge_2',
                'due_date':
                datetime.now().date() + relativedelta(days=20),
                'recurring':
                True,
                'recurring_until': (datetime.now().date() +
                                    relativedelta(years=1)).strftime("%m/%Y")
            })
        self.assertRedirects(post_response,
                             reverse('show-rent', args=[self.rent.id]))
        new_charge = Charge.objects.get(title='test_charge_2')
        self.assertIsNotNone(new_charge)
        self.assertTrue(new_charge.recurring)
