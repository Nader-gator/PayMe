from django.urls import path
from .views import dashboard, pay, success, failed

urlpatterns = [
    path('', dashboard, name='renter-dashboard'),
    path('pay/<int:charge_id>/', pay, name='pay-charge'),
    path('pay/<int:charge_id>/success/<int:amount>/<int:token>/',
         success,
         name='payment-success'),
    path('pay/<int:charge_id>/failed/<int:token>/',
         failed,
         name='payment-failed'),
]
