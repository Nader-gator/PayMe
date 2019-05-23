from django.shortcuts import render, redirect


def home(request):
    return render(request, 'homepage/home.html')


def dashboard(request):
    if request.user.is_landlord:
        return redirect(to='landlord-dashboard')
    elif not request.user.is_landlord:
        return redirect(to='renter-dashboard')
    return render(request, 'homepage/home.html')
