from django.urls import path
from .views import dashboard, create_new_rent

urlpatterns = [
    path('', dashboard, name='landlord-dashboard'),
    path('new_rent/', create_new_rent, name='new-rent'),
]
