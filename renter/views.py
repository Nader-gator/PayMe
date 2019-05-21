from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    if request.user.is_landlord:
        #TODO: make this landlords dashboard when the links are made
        return redirect('homepage')
    return render(request, 'renter/dashboard.html')
