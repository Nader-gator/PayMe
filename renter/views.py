from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from renter.common.util.rent_structure import calculate_rent_structure


@login_required
def dashboard(request):
    if request.user.is_landlord:
        #TODO: make this landlords dashboard when the links are made
        return redirect('homepage')
    renter = request.user.renter_profile
    if renter.rent:
        context = calculate_rent_structure(renter.rent.charge_field.all())
    else:
        context = {}
    return render(request, 'renter/dashboard.html', context)
