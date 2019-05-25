from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from renter.common.util.rent_structure import calculate_rent_structure
from django.conf import settings
from django.contrib import messages
from landlord.models import Charge
import stripe
import secrets


@login_required
def dashboard(request):
    if request.user.is_landlord:
        return render(request, 'homepage/wrong_page.html',
                      {'wrong_person': 'landlord'})
    renter = request.user.renter_profile
    if renter.rent:
        context = calculate_rent_structure(renter.rent.charge_set.all())
    else:
        context = {}
    return render(request, 'renter/dashboard.html', context)


@login_required
def pay(request, charge_id):
    charge = Charge.objects.get(id=charge_id)
    charge.due_now = charge.amount - charge.amount_paid
    context = {'charge': charge}
    payment_token = secrets.randbelow(10000)
    charge.payment_token = payment_token

    if request.method == 'POST':
        absolute_uri = request.build_absolute_uri('/')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = request.POST.get('payment-amount') + "00"

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
            f"?token={payment_token}&charge_id={charge_id}&amount={amount}",
            cancel_url=absolute_uri[:-1] + reverse('payment-failed') +
            f"&charge_id={charge_id}",
        )
        context['id'] = session.id
        context['key'] = settings.STRIPE_PUBLIC_KEY
        charge.save()

    return render(request, 'renter/pay.html', context)


@login_required
def success(request):
    parameters = request.GET
    charge = Charge.objects.get(id=parameters['charge_id'])
    amount = int(parameters['amount']) // 100
    messages.success(
        request,
        'payment successful',
    )
    if charge.payment_token == int(parameters['token']):
        charge.amount_paid += amount
        if charge.amount_paid >= charge.amount:
            if charge.recurring:
                charge.num_months_paid += 1
            else:
                charge.paid = True
        else:
            charge.due_now = charge.amount - charge.amount_paid
        charge.payment_token = None
        charge.save()
    if charge.paid:
        return redirect('renter-dashboard')
    else:
        charge.due_now = charge.amount - charge.amount_paid

    return redirect('pay-charge', charge_id=charge.id)


@login_required
def failed(request):
    parameters = request.GET
    charge = Charge.objects.get(id=parameters['charge_id'])
    charge.payment_token = None
    charge.save()
    messages.error(request, 'payment failed')
    return redirect('pay-charge', charge_id=charge.id)
