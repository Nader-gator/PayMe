from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from renter.common.util.rent_structure import calculate_rent_structure


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
