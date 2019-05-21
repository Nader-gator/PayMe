from django.shortcuts import render
from .admin import UserCreationForm


def create_new_user(request):
    context = {'form': UserCreationForm}
    return render(request, 'new_user.html', context)
