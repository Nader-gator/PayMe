from django.urls import path
from .views import home, dashboard
urlpatterns = [
    path('', home, name='homepage'),
    path('dashboard/', dashboard, name='homepage-dashboard')
]
