from django.urls import path
from .views import dashboard, pay, success, failed

urlpatterns = [
    path('', dashboard, name='renter-dashboard'),
    path('pay/<int:charge_id>/', pay, name='pay-charge'),
    path('pay/success/', success, name='payment-success'),
    path('pay/failed/', failed, name='payment-failed'),
]
