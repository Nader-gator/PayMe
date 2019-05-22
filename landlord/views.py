from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


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
    return render(request, 'landlord/new_charge.html')
