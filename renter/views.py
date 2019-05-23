from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from renter.common.util.rent_structure import calculate_rent_structure
from django.conf import settings
from django.contrib import messages
from landlord.models import Charge
import stripe


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
    context = {
        'charge': charge,
    }

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
            success_url=absolute_uri[:-1] +
            reverse('payment-success', args=[charge_id, amount]),
            cancel_url=absolute_uri[:-1] +
            reverse('payment-failed', args=[charge_id]),
        )
        context['id'] = session.id
        context['key'] = settings.STRIPE_PUBLIC_KEY
    return render(request, 'renter/pay.html', context)


@login_required
def success(request, charge_id, amount):
    charge = Charge.objects.get(id=charge_id)
    charge.due_now = charge.amount - charge.amount_paid
    amount = amount // 100
    messages.success(
        request,
        'payment successful',
    )
    charge.amount_paid += amount
    if charge.amount_paid >= charge.amount:
        if charge.recurring:
            charge.num_months_paid += 1
        else:
            charge.paid = True
    charge.save()
    return render(request, 'renter/pay.html', {'charge': charge})


@login_required
def failed(request, charge_id):
    charge = Charge.objects.get(id=charge_id)
    messages.error(request, 'payment failed')
    return render(request, 'renter/pay.html', {'charge': charge})
