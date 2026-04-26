from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('catalogue/', views.liste_produits, name='liste_produits'),
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('login/', auth_views.LoginView.as_view(
        template_name='Restaurant/login.html'
    ), name='login'),
    path('commander/<int:produit_id>/', views.commander, name='commander'),
    path('', views.accueil, name='accueil'),
]
