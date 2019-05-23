from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import NewRentForm, NewChargeForm
from django.contrib import messages
from .models import Rent
from users.models import User


@login_required
def dashboard(request):
    if not request.user.is_landlord:
        return redirect(to='renter-dashboard')
    landlord = request.user.landlord_profile
    if len(landlord.rent_set.all()) > 0:
        context = {'rents': landlord.rent_set.all()}
    else:
        context = {}

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
    if request.method == 'POST':
        requested_user = User.objects.filter(
            email=request.POST.get('email', '')).first()

        if requested_user and not requested_user.is_landlord:
            if requested_user.renter_profile.rent:
                messages.error(request, 'user already added to a rent')
            else:
                #avoiding extra db quesry
                requested_user.renter_profile.rent_id = rent_id
                messages.success(request, 'user added to rent')
                requested_user.renter_profile.save()
        elif requested_user is not None and requested_user.is_landlord:
            messages.error(request, 'requested user is a landlord')
        else:
            messages.error(request, 'user does not exist')

    rent = Rent.objects.get(id=rent_id)
    charges = rent.charge_set.all()
    context = {'charges': charges, 'rent': rent}
    return render(request, 'landlord/rent_show.html', context)


@login_required
def create_new_charge(request, rent_id):
    rent = Rent.objects.get(id=rent_id)
    if request.method == 'POST':
        form = NewChargeForm(request.POST)
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
