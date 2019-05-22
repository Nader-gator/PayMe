from django.urls import path
from .views import dashboard, create_new_rent, create_new_charge, show_rent

urlpatterns = [
    path('', dashboard, name='landlord-dashboard'),
    path('new_rent/', create_new_rent, name='new-rent'),
    path('rents/<int:rent_id>/', show_rent, name='show-rent'),
    path('rents/<int:rent_id>/new_charge',
         create_new_charge,
         name='new-charge'),
]
