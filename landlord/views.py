from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import NewRentForm, NewChargeForm
from django.contrib import messages
from .models import Rent
from users.models import User
from datetime import datetime
from renter.common.util.rent_structure import landlord_rent_structure


@login_required
def dashboard(request):
    if not request.user.is_landlord:
        return render(request, 'homepage/wrong_page.html',
                      {'wrong_person': 'renter'})
    landlord = request.user.landlord_profile
    context = {'rents': landlord.rent_set.all()}
    return render(request, 'landlord/dashboard.html', context)


@login_required
def create_new_rent(request):
    if request.method == 'POST':
        form = NewRentForm(request.POST)
        if form.is_valid():
            rent = form.save(commit=False)
            rent.landlord = request.user.landlord_profile
            rent.save()
            messages.success(request, 'rent created')
            return redirect(to='landlord-dashboard')
    else:
        form = NewRentForm()
    return render(request, 'landlord/new_rent.html', {'form': form})


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


@login_required
def create_new_charge(request, rent_id):
    rent = Rent.objects.get(id=rent_id)
    if request.method == 'POST':
        request_params = request.POST.copy()
        if request_params.get('recurring'):
            try:
                date = datetime.strptime(request_params.get('recurring_until'),
                                         '%m/%Y')
            except ValueError:
                date = datetime.now().date()
            request_params.update({'recurring_until': date})
        form = NewChargeForm(request_params)
        if form.is_valid():
            charge = form.save(commit=False)
            charge.rent = rent
            charge.save()
            messages.success(request, 'charge created')
            return redirect(to='show-rent', rent_id=rent_id)
    else:
        form = NewChargeForm()
    context = {'form': form, 'rent': rent}
    return render(request, 'landlord/new_charge.html', context)
