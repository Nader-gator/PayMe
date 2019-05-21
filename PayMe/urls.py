from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth
from users.views import create_new_user, edit_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',
         auth.LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('logout/',
         auth.LogoutView.as_view(template_name='users/logout.html'),
         name='logout'),
    path('register/', create_new_user, name='register'),
    path('profile/', edit_user, name='profile'),
    path('', include('homepage.urls')),
    path('renter', include('renter.urls')),
    # path('landlord', include('landlord.urls'))
]
