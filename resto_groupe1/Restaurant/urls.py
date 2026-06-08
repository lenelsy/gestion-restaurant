"""
urls.py — Routes de l'application Restaurant
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard & Rapports ──────────────────────────────────
    path('dashboard/',                        views.dashboard,         name='dashboard'),
    path('rapport/',                views.rapport_financier, name='rapport_financier'),

    # ── Clients ──────────────────────────────────────────────
    path('clients/',                    views.client_list,   name='client_list'),
    path('clients/nouveau/',            views.client_create, name='client_create'),
    path('clients/<int:pk>/modifier/',  views.client_update, name='client_update'),
    path('clients/<int:pk>/supprimer/', views.client_delete, name='client_delete'),

    # ── Tables ───────────────────────────────────────────────
    path('tables/',                    views.table_list,   name='table_list'),
    path('tables/nouvelle/',           views.table_create, name='table_create'),
    path('tables/<int:pk>/modifier/',  views.table_update, name='table_update'),
    path('tables/<int:pk>/supprimer/', views.table_delete, name='table_delete'),

    # ── Réservations ─────────────────────────────────────────
    path('reservations/',                    views.reservation_list,   name='reservation_list'),
    path('reservations/nouvelle/',           views.reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/modifier/',  views.reservation_update, name='reservation_update'),
    path('reservations/<int:pk>/supprimer/', views.reservation_delete, name='reservation_delete'),

    # ── Commandes ────────────────────────────────────────────
    path('commandes/',                     views.commande_list,    name='commande_list'),
    path('commandes/nouvelle/',            views.commande_create,  name='commande_create'),
    path('commandes/<int:pk>/',            views.commande_detail,  name='commande_detail'),
    path('commandes/<int:pk>/modifier/',   views.commande_update,  name='commande_update'),
    path('commandes/<int:pk>/supprimer/',  views.commande_delete,  name='commande_delete'),
    path('commandes/<int:pk>/facture/',    views.facture_commande, name='facture_commande'),
    path('lignes/<int:pk>/supprimer/',     views.ligne_delete,     name='ligne_delete'),

    # ── Produits / Menu ──────────────────────────────────────
    path('produits/',                    views.produit_list,       name='produit_list'),
    path('produits/nouveau/',            views.produit_create,     name='produit_create'),
    path('produits/<int:pk>/modifier/',  views.produit_update,     name='produit_update'),
    path('produits/<int:pk>/supprimer/', views.produit_delete,     name='produit_delete'),
    path('compositions/<int:pk>/suppr/', views.composition_delete, name='composition_delete'),

    # ── Ingrédients ──────────────────────────────────────────
    path('ingredients/',                    views.ingredient_list,   name='ingredient_list'),
    path('ingredients/nouveau/',            views.ingredient_create, name='ingredient_create'),
    path('ingredients/<int:pk>/modifier/',  views.ingredient_update, name='ingredient_update'),
    path('ingredients/<int:pk>/supprimer/', views.ingredient_delete, name='ingredient_delete'),

    # ── Stocks ───────────────────────────────────────────────
    path('stocks/',                       views.stock_list,              name='stock_list'),
    path('stocks/<int:pk>/modifier/',     views.stock_update,            name='stock_update'),
    path('stocks/variations/',            views.variation_stock_list,    name='variation_stock_list'),
    path('stocks/variations/nouvelle/',   views.variation_stock_create,  name='variation_stock_create'),

    # ── Employés ─────────────────────────────────────────────
    path('employes/',                    views.employe_list,   name='employe_list'),
    path('employes/nouveau/',            views.employe_create, name='employe_create'),
    path('employes/<int:pk>/modifier/',  views.employe_update, name='employe_update'),
    path('employes/<int:pk>/supprimer/', views.employe_delete, name='employe_delete'),

    path('postes/',          views.poste_list,       name='poste_list'),
    path('postes/nouveau/',  views.poste_create,     name='poste_create'),
    path('affectations/',          views.affectation_list,   name='affectation_list'),
    path('affectations/nouvelle/', views.affectation_create, name='affectation_create'),

    # ── Fournisseurs ─────────────────────────────────────────
    path('fournisseurs/',                    views.fournisseur_list,   name='fournisseur_list'),
    path('fournisseurs/nouveau/',            views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/',  views.fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),

    path('approvisionnements/',                    views.approvisionnement_list,   name='approvisionnement_list'),
    path('approvisionnements/nouveau/',            views.approvisionnement_create, name='approvisionnement_create'),
    path('approvisionnements/<int:pk>/supprimer/', views.approvisionnement_delete, name='approvisionnement_delete'),

    # ── Équipements ──────────────────────────────────────────
    path('equipements/',                    views.equipement_list,   name='equipement_list'),
    path('equipements/nouveau/',            views.equipement_create, name='equipement_create'),
    path('equipements/<int:pk>/modifier/',  views.equipement_update, name='equipement_update'),
    path('equipements/<int:pk>/supprimer/', views.equipement_delete, name='equipement_delete'),

    path('maintenances/',                    views.maintenance_list,   name='maintenance_list'),
    path('maintenances/nouvelle/',           views.maintenance_create, name='maintenance_create'),
    path('maintenances/<int:pk>/supprimer/', views.maintenance_delete, name='maintenance_delete'),

    # ── Marketing & Finance ──────────────────────────────────
    path('marketing/',                    views.marketing_list,   name='marketing_list'),
    path('marketing/nouveau/',            views.marketing_create, name='marketing_create'),
    path('marketing/<int:pk>/modifier/',  views.marketing_update, name='marketing_update'),
    path('marketing/<int:pk>/supprimer/', views.marketing_delete, name='marketing_delete'),

    path('factures/',                    views.facture_list,   name='facture_list'),
    path('factures/nouvelle/',           views.facture_create, name='facture_create'),
    path('factures/<int:pk>/supprimer/', views.facture_delete, name='facture_delete'),

    # ── Véhicules ────────────────────────────────────────────
    path('vehicules/',                    views.vehicule_list,   name='vehicule_list'),
    path('vehicules/nouveau/',            views.vehicule_create, name='vehicule_create'),
    path('vehicules/<int:pk>/modifier/',  views.vehicule_update, name='vehicule_update'),
    path('vehicules/<int:pk>/supprimer/', views.vehicule_delete, name='vehicule_delete'),

    # ── Pages publiques & Panier ──────────────────────────────
    path('',                   views.accueil,          name='accueil'),
    path('menu/',                      views.menu_public,      name='menu_public'),
    path('panier/',                    views.panier_voir,      name='panier_voir'),
    path('panier/ajouter/<int:pk>/',   views.panier_ajouter,   name='panier_ajouter'),
    path('panier/retirer/<int:pk>/',   views.panier_retirer,   name='panier_retirer'),
    path('panier/supprimer/<int:pk>/', views.panier_supprimer, name='panier_supprimer'),
    path('panier/vider/',              views.panier_vider,     name='panier_vider'),
    path('commander/',                 views.valider_commande, name='valider_commande'),
    path('facture-client/<int:pk>/',   views.facture_publique, name='facture_publique'),
]
