[![Build Status](https://travis-ci.org/Nader-gator/PayMe.svg?branch=master)](https://travis-ci.org/Nader-gator/PayMe)
[![codecov](https://codecov.io/gh/Nader-gator/PayMe/branch/master/graph/badge.svg)](https://codecov.io/gh/Nader-gator/PayMe)

# PayMe

This is a quick walkthrough of the code snippets and the creation process.

Before I start, a few things:

- I went ahead and uploaded the project on Heroku, the database is seeded and ready for use
  [here](https://paymepls.herokuapp.com/)
  - I have already created two users with the following credentials, one landlord and one renter with some charges already in place
    if you want to jump right into playing around with everything, otherwise feel free to create your own users.
    - Landlord user: landlord@gmail.com, password: starwars
    - Renter user: renter@gmail.com, password: starwars
  - Also note, if you want to test Stripe functionality, simply input 424242... As your credit card number (the rest doesn't matter)
    and it should behave as if you put in a real card

* The tests I've written for this project are for backend only using Django's built in TestCase. To run the tests, clone the repo and
  run `pip install -r requirements.txt`, then run `./manage.py test`

  - please note: this will not work on your computer as two keys, Django's secret key and strip secret key are passed as environment
    variables for security reasons. You can check out the test results on [codecove](https://codecov.io/gh/Nader-gator/PayMe) or the
    build logs on [travis CI](https://travis-ci.org/nader-gator/payme). If you need to run them ask me and I can email you the keys directly

* as mentioned above, I have set up continuous integration for this project with Travis CI that automatically tests and deploys new builds

* If you wish to run the server locally, begin with `pip install -r requirements.txt`, (do this in a virtual environment), then `python manage.py migrate` and finally `python manage.py runserver`
  - again, note that the server will not run if the environment variables are not provided

## Apps

There are four apps in this project. Please note I structured most of the apps with encapsulation and expandability in mind
which is mainly why I split everything up

- [Homepage app](#homepage-app)

  - This app doesn't do much other than taking care of the routing and displaying the homepage before users log in. I created this because
    usually I like to separate the 'Face' of the website (the pretty static pages) from the functioning parts of the website. In
    a real world app, this would be the section a frontend designer or an outside contractor could work on creating the advertising and front
    sections of the website without having to see the codebase or worrying about breaking functionality of the website.

- [Users app](#users-app)

  - This app handles all the user(and superuser) creation, updating, and authentication. I believe that the models in an app that handle
    basic user creation and Auth should not do anything else to avoid complicating matters if the functionality of the website changes
    and also it ensures better security the less we mess around with the Auth models. The models that handle the functionality of the
    are created in the Landlord and Renter apps and linked to the User model with a OneToOne relationship.

- [Landlord app](#landlord-app)

  - This app handles all the Rent and charge creation. After logging in(as a landlord) user lands on a dashboard defined in this app and
    has the ability to create new rents and view rents he has created. The user can enter these rents and view the charges he has created
    add also add new charge. At the bottom of the page, the user can see what renters are on this rent and also add new renters to
    the rent by email. Finally, the landlord can add charges to the rent. He must give the charge a title and an amount, and finally a
    due date. The landlord can also check a box indicating that the charge is recurring, and indicate the date the charge will be
    recurring until.

- [Renter app](#renter-app)
  - This app handles all the Renter functions, mainly viewing the rent a user is on, and all the Stripe payment functions. After the
    renter logs in he lands in the dashboard where he can see both his recurring and non recurring charges. He can click on any charge
    and he's taken to a page where he is informed how much of the charge is due. The renter can input however much he wants and then he is
    taken to an external Stripe page where he can input payment information, and then redirected back to the app.

### Homepage App

This app as I discussed earlier handles static parts of the website, which really is just a page asking the user if they are a landlord or
a renter. It also handles redirecting users from the `/dashboard/` url to the appropriate dashboard if they are logged in.

### User App

This app handles all the authentication and user models, which holds all the personal information of the user.

##### Design

As per the specifications, the users have to be able to log in using their email, and certain other fields such as birthday are required.
Because of this that means the default user model in Django is not sufficient, also Django documentations recommends using custom
user models,so I decided to
extend their `AbstractUser` model, which means I can have a modifiable user model I like, and user Django's built in Auth and Admin
system(even though I don't really use the Admin features, I think its good to include it just in case I need it later). To make the
Admin user work I simply followed the instructions of the docs creating all the necessary class methods to ensure functionality.

Finally, I created custom new user and update user forms extending the built in `ModelForm` in the `Admin.py` folder and registered the
user model with the site Admin to make the model work in the Admin page.

Also note that I set `AUTH_USER_MODEL = 'users.User'` in `settings.py`. This means throughout the project when defining relationship to the User model I will import `AUTH_USER_MODEL`
from the `settings` module for added security and also making it easier to change the Auth user model if the project ends up using a
different user model in the future. This was recommended by the Django docs as well.

#### Logging in and out

Since the user model extends `AbstractUser`, this means logging in an out is a breeze, I simply imported the Auth class views and indicated
what template name to user. The built in login view provides the login form in the context for the HTML page.

```python
from django.contrib.auth import views as auth

#...
    path('login/',
         auth.LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('logout/',
         auth.LogoutView.as_view(template_name='users/logout.html'),
         name='logout'),
```

#### Signals

As I mentioned earlier in the overview, The `User` model itself will not be involved in functionality of the app, instead, `Landlord` and
`Renter` models will be doing those. That means every user that is created triggers the creation of either a `Landlord` or `Renter` in the
database.

```python
@receiver(post_save, sender=User)
def create_relation(sender, instance, created, **kwargs):
    if created:
        if instance.is_landlord:
            Landlord.objects.create(profile=instance)
        else:
            Renter.objects.create(profile=instance)
```

---

### Landlord App

This app handles all the landlord side of things. The urls for this app route to the dashboard show, rent show, and a new charge form show
since a charge is connected to a rent, the new charge url takes `rent_id` as an argument

```python
    path('', dashboard, name='landlord-dashboard'),
    path('new_rent/', create_new_rent, name='new-rent'),
    path('rents/<int:rent_id>/', show_rent, name='show-rent'),
    path('rents/<int:rent_id>/new_charge', create_new_charge, name='new-charge'),
```

---

#### Models

Since I wanted the landlord app to encapsulate all the action related to rents and charges, I defined three models here

- Landlord
  - This is the model that OneToOne connects to the User model. All the rents are then connected to this model by foreign keys
- Rent
  - This is the model for Rents, It only has a name and renters are connected to this model by foreign keys every renter only belongs to
    one Rent and a Rent can have many renters. Many Charges are also belong to a rent through foreign keys
- Charge
  - This models handles charges. A charge model keeps track of the amount of charge, due date, if its recurring or not, and recurring
    until date. It also has a field that specifics if the charge is paid.
  - since the specifications noted that users can pay any amount they desire, the model has an amount_paid field that defaults to 0
    that keeps tracks of the amount paid.
  - The models also has a `num_months_paid` which keeps track of how many months have been paid in a recurring charge
    - I wanted to reuse the database field as much as possible(to avoid repeating code and unnecessary complexity), so recurring charges and
      one time charges share most fields.
    - the `num_months_paid` can be used to calculate how many months of balance has been paid for a recurring charge ( example: charge's
      first due date was Jan 1st, recurring until Dec, 3 months are paid therefore the next due date is April 1st)
  - Design note: I designed the database with an `active` field which I didn't really user. The purpose of this field is to enable
    deleting a charge without actually removing it from the database. I believe that data such as these should never be deleted from the
    database (or at least be set up this way) so that history of activity is easily accessible.

---

#### New Charge forms

Django's while Django's forms generally do a good job of checking form data that they are correct, I had to add a few more rules regarding
dates into a custom form. Mainly, I wanted to make it so that a landlord cannot set a charge due today or no due date before today. I
also wanted to set some restrictions on recurring until dates (it has to be at least a month from now, after today, etc. )

I simply created a form inheriting from ModelForm. It calls `super` on the existing `clean` method (so all the built in Django restrictions
do what they do) and then applies errors to the form according to my specifications. Here's a snippet

```python

class NewChargeForm(ModelForm):
    def clean(self):
        cleaned_data = super(NewChargeForm, self).clean()
        due_date = cleaned_data.get('due_date')
        recurring_until = cleaned_data.get('recurring_until')
        recurring = cleaned_data.get('recurring')
        if due_date and recurring_until:
            if recurring_until < (due_date + timedelta(days=31)):
                self.add_error('recurring_until',
                               ('Recurring until date must be at least '
                                '31 days after the due date'))
            if recurring_until and not recurring:
                self.add_error('recurring_until',
                               ("you can't set a recurring until "
                                "date for one time charges"))
        if due_date and due_date < (datetime.now().date() + timedelta(days=1)):
            self.add_error('due_date',
                           "please select a date at least one after today")

        if recurring and not recurring_until:
            self.add_error('recurring_until',
                           'please enter a recurring until date')
```

Most of These restrictions are enforced in the frontend at HTML level, but I think it's always good to have backend restrictions for
"curious" users.

---

#### Views

I'll try to keep this part as brief as I can, since most of the functions I use here are pretty standard, They fetch the relevant data
from the database, and render the specified HTML page passing the data in as context.

```python

@login_required
def dashboard(request):
    if not request.user.is_landlord:
        return render(request, 'homepage/wrong_page.html',
                      {'wrong_person': 'renter'})
    landlord = request.user.landlord_profile
    if len(landlord.rent_set.all()) > 0:
        context = {'rents': landlord.rent_set.all()}
    else:
        context = {}

    return render(request, 'landlord/dashboard.html', context)

```

The logic of the rest of the views is works similar to the function above. In cases of POST request, such as adding a new renter to a rent,
the logic is handled in the same function. Here is the function that adds a new user to a rent.

```python
@login_required
def show_rent(request, rent_id):
    rent = Rent.objects.get(id=rent_id)
    if request.method == 'POST':
        requested_user = User.objects.filter(
            email=request.POST.get('email', '')).first()

        if requested_user and not requested_user.is_landlord:
            if requested_user.renter_profile.rent:
                messages.error(request, 'user already added to a rent')
            else:
                requested_user.renter_profile.rent = rent
                messages.success(request, 'user added to rent')
                requested_user.renter_profile.save()
        elif requested_user is not None and requested_user.is_landlord:
            messages.error(request, 'requested user is a landlord')
        else:
            messages.error(request, 'user does not exist')

    renters = rent.renter_set.all()
    charges = landlord_rent_structure(rent.charge_set.all())
    context = {'rent': rent, 'renters': renters, **charges}
    return render(request, 'landlord/rent_show.html', context)
```

There are a few more methods that you can check out, but for the sake of keeping this short I'll leave them out as the are
fairly self explanatory.

---

#### Things I'd improve on for the Landlord app

- Few of the methods have quite a few nested if statements and don't make for the most readable function definitions, but the methods
  themselves are fairly short so I didn't make breaking them apart a big priority. Nevertheless I think the views could use some refactoring
- Most of the code is not commented, So I think the code could use a few comments in some areas to help the readability.
- The dashboard page checks for if the user is a renter trying to access the landlord dashboard. I put that in place because it is possible
  for a user to get there by accident. However the rest of the routes aren't protected against a curious user who manually inputs the routes.
  A good addition to all the functions could be a decorator that checks if the user trying to access the route is a landlord

  ***

### Renter App

This App handles user dashboard and charge payments. The routes are fairly basic, they route to dashboard, charge show (and pay), and two
landing pages for success or failure of payments. More on these two later in the views section.

---

#### Models

The model for renter is very simple. Aside being OneToOne referenced to the user, it had a foreign key that references the rent the
user belongs to

---

#### Views

This section is very similar to the landlord section. There is one thing I wanted to mention. To improve the looks of the dashboard and
have color coding (on time, late, etc.), I passed all the of the user charges to a utility method I created

```python

@login_required
def dashboard(request):
    if request.user.is_landlord:
        return render(request, 'homepage/wrong_page.html',
                      {'wrong_person': 'landlord'})
    renter = request.user.renter_profile
    if renter.rent:
        context = renter_rent_structure(renter.rent.charge_set.all())
    #.....
```

The job of `#renter_rent_structure` is to iterate through the charges, separate them into recurring and one-time mark them as late,
on time or coming up. The `status` property corresponds to the Bootstrap 4 classes

```python

def renter_rent_structure(charges):
    one_time_charges = []
    recurring_charges = []
    todays_date = datetime.now().date()
    for charge in charges:
        if charge.paid:
            continue

        if charge.due_date < todays_date:
            charge.alert = 'danger'
            charge.status = 'late'
        elif charge.due_date > (todays_date + timedelta(days=7)):
            charge.alert = 'info'
            charge.status = 'upcoming'
        else:
            charge.alert = 'warning'
            charge.status = 'due soon'

        if charge.recurring:
            if charge.recurring_until < todays_date:
                pass
            else:
                recurring_charges.append(charge)
        else:
            one_time_charges.append(charge)
        charge.save()

    return {
        'one_time_charges': one_time_charges,
        'recurring_charges': recurring_charges
    }

```

---

#### Stripe payment processing

Strip's payment system is fairly straight forward. Initially I wanted to user Stripe.js on the frontend only to handle payments. It was
the fastest way to do so but after reading the docs I learned that, while still fully supported, it's essentially the older version of
their payment processor and is essentially deprecated. So I decided to stick to their newest method.

**N.B.** Stripe has a ton of features that allow user to create customers, create a catalog of products, create charge, track due dates
on charges, and even create recurring charges. In a real world app in my opinion designing the app with these features in my to allow a
deep integration of these features is essential. While that's outside the scope of this projects, here are my thought's on how I would
integrate these features into the backend

- Offload the charge tracking to Stripe. This means every charge made by the landlord, is created in the strip system, and when
  users open their dashboard the status of their payments are all fetched from Stripe
  - One challenge with this implementation is speed. Fetching multiple charges from strip could potentially take a few seconds.
    But I don't think that's a big issue as a simple caching system/local database that updates itself based on Stripe data
    periodically could mitigate this problem
- Set up signals so that whenever a user is created, a "customer" with the same info is created on Strip and link the user to that Strip
  customer with an ID. This way the app can use all the features of Stripe such as Email notifications for late payments.

With that out of the way let's look at how the Stripe payment system was implemented. It has two parts. One part is in the backend and uses
Stripes official python library to create a one time charge. Stripe responds with a charge object, The ID of which is then passed to
Stripes JavaScript function. The function then redirects the user to the appropriate page to complete the charge.

```python
    if request.method == 'POST':
        payment_token = randbelow(10000)
        charge.payment_token = payment_token
        absolute_uri = request.build_absolute_uri('/')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = request.POST.get('payment-amount') + "00"  #cents
        success_data = {
            'token': payment_token,
            'charge_id': charge_id,
            'amount': amount
        }
        failed_data = {'charge_id': charge_id}

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'name': f"{charge.title}",
                'description': f"Payment for {charge.title}",
                'amount': amount,
                'currency': 'usd',
                'quantity': 1,
            }],
            success_url=absolute_uri[:-1] + reverse('payment-success') +
            f"?{urlencode(success_data)}",
            cancel_url=absolute_uri[:-1] + reverse('payment-failed') +
            f"?{urlencode(failed_data)}",
        )
        context['id'] = session.id
        context['key'] = settings.STRIPE_PUBLIC_KEY
        charge.save()

```

And in the HTML page:

```html
{% block bottom-section %} {% if id %}
<script>
  var stripe = Stripe("{{ key }}");
  stripe.redirectToCheckout({ sessionId: "{{ id }}" });
</script>
{% endif %} {% endblock bottom-section %}
```

---

**How successful payments are processed**

You probably noticed these two odd lines passed in as arguments to the Strip function:

```python
    success_url=absolute_uri[:-1] + reverse('payment-success') + f"?{urlencode(success_data)}",
    cancel_url=absolute_uri[:-1] + reverse('payment-failed') + f"?{urlencode(failed_data)}",
```

These two arguments specify where Stripe redirects the user upon completion or failure of the payment. Since integrating Strip into the
backend to properly confirm payments are successful, I opted for a slightly hacky way of taking care of this.

Every time a POST request comes in for payment, a random number is generated as a token, and saved to the database alongside of the charge.

```python
    payment_token = randbelow(10000)
    charge.payment_token = payment_token
    #...
    charge.save()
```

This token is then passed as data to the `success_url` of the Stripe payment system, but not to the `cancel_url`. If Stripe redirects
the user to `success_url`, The views function checks to see if the token passed in in the url data matches the one in the database,
and finally registers the payment. Here's a small snippet

```python
def success(request):
    #....
    messages.success(
        request,
        'payment successful',
    )
    if charge.payment_token == int(parameters['token']):
        charge.amount_paid += amount
        if charge.amount_paid >= charge.amount:
            if charge.recurring:
                charge.num_months_paid += 1
```

The payment token system is mainly there so the user can't just refresh the page and register a new payment every time. Essentially, a token
is only good for one request. If the user ends up on the cancel_url, The token is set to null.

```python
def failed(request):
    parameters = request.GET
    charge = Charge.objects.get(id=parameters['charge_id'])
    charge.payment_token = None
    charge.save()
```

---

**Thing I'd improve in the renter app**

- The token system is very insecure, and has room for a lot of venerabilities. Switching to using the Strip library is definitely the way
  go, however I skipped this as it was outside of the scope of this project.

- The way charges are tracked is not very robust. There is no system for tracking late payments other than simply looking at their due
  dates and weather they are paid or not. This means in future implementing email notification systems could be very challenging.

- The way recurring charges are tracked could use some improving and refactoring. I think the logic I have in place is a bit too hard to
  read and most likely there are some edge cases that it does not take into account. Breaking up the logic into smaller functions and
  implementing a very through suit of tests would be my next steps.

- Creating Transaction model and table in the database to keep track of every single Transaction would be a great improvement to this
  system as it is right now. It'll help keep track of what charges have what transactions and transaction ID connected to them.

- finally, same as the previous app, the functions have a few nested if statements and could user some refactoring.

---

---

---

A note on the tests: I have written a suit of unit tests for every app. They have a pretty decent coverage of the codebase but I think
there is a lot of edge cases that they do not test. They also do not test the frontend components and the Django generated forms.
