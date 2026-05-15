# On importe les outils de routage Django
from django.urls import path

# On importe toutes nos vues depuis views.py
from . import views

# On importe les vues d'authentification intégrées de Django
from django.contrib.auth import views as auth_views

# Liste de toutes les URLs de l'application Restaurant
urlpatterns = [

    # ==========================================
    # MODULE : PRODUCT MANAGEMENT
    # ==========================================

    # Page catalogue des plats — accessible à /restaurant/catalogue/
    path('catalogue/', views.liste_produits, name='liste_produits'),

    # ==========================================
    # MODULE : ORDER MANAGEMENT
    # ==========================================

    # Page liste des commandes — accessible à /restaurant/commandes/
    path('commandes/', views.liste_commandes, name='liste_commandes'),

    # Formulaire pour passer une commande sur un plat spécifique
    # produit_id est l'identifiant du plat choisi
    path('commander/<int:produit_id>/', views.commander, name='commander'),

    # ==========================================
    # MODULE : USER MANAGEMENT
    # ==========================================

    # Page de connexion — accessible à /restaurant/login/
    path('login/', auth_views.LoginView.as_view(
        template_name='Restaurant/login.html'
    ), name='login'),

    # Page de déconnexion — accessible à /restaurant/logout/
    path('logout/', views.deconnexion, name='logout'),

    # Page liste de tous les utilisateurs
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),

    # Page pour créer un nouvel utilisateur
    path('utilisateurs/creer/', views.creer_utilisateur, name='creer_utilisateur'),

    # Page pour modifier un utilisateur existant
    # user_id est l'identifiant de l'utilisateur à modifier
    path('utilisateurs/modifier/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),

    # Page pour supprimer un utilisateur
    path('utilisateurs/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),

    # ==========================================
    # PAGE D'ACCUEIL
    # ==========================================

    # Page d'accueil — accessible à /restaurant/
    path('', views.accueil, name='accueil'),
]
