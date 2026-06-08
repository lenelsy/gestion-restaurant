"""
urls.py — Configuration des URLs principales
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from Restaurant import views as rv

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Authentification
    path('login/',  rv.login_view,  name='login'),
    path('logout/', rv.logout_view, name='logout'),

    # Application principale
    path('', include('Restaurant.urls')),
]
