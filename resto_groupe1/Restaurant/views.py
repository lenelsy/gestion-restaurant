from django.shortcuts import render, redirect
from .models import Produit, Ingredient, Client, Commande, Reservation
# --- MODULE : PRODUCT MANAGEMENT ---

def liste_produits(request):
    """Affiche le catalogue des plats"""
    produits = Produit.objects.all()
    return render(request, 'Restaurant/catalogue.html', {'produits': produits})

# --- MODULE : ORDER MANAGEMENT ---

def liste_commandes(request):
    """Affiche l'historique des commandes"""
    # Tri par date la plus récente
    commandes = Commande.objects.all().order_by('-date')
    return render(request, 'Restaurant/commandes.html', {'commandes': commandes})

def liste_reservations(request):
    """Affiche la liste des réservations de tables"""
    # Cette fonction corrige ton erreur 'module has no attribute liste_reservations'
    reservations = Reservation.objects.all().order_by('-date')
    return render(request, 'Restaurant/reservations.html', {'reservations': reservations})

def creer_commande(request):
    """Gère la création d'une nouvelle commande"""
    if request.method == "POST":
        # La logique de validation sera ajoutée ici plus tard
        pass

    # On récupère les données pour remplir les listes déroulantes du formulaire
    produits = Produit.objects.all()
    clients = Client.objects.all()

    context = {
        'produits': produits,
        'clients': clients

    }
    return render(request, 'Restaurant/form_commande.html', context)


def commander(request, produit_id):
    produit = Produit.objects.get(id=produit_id)
    if request.method == 'POST':
        nom_client = request.POST.get('nom_client')
        quantite = int(request.POST.get('quantite'))

        # Créer la commande en base
        Commande.objects.create(
            produit=produit,
            quantite=quantite,
            prix_unitaire=produit.prix,
            statut='en attente',
            mode_paiement='sur place',
            mode_livraison='sur place',
            id_table = 1,
        )
        return redirect('/restaurant/catalogue/')
    return render(request, 'Restaurant/commander.html', {'produit': produit})
def accueil(request):
    return render(request, 'Restaurant/accueil.html')
# ==========================================
# MODULE : USER MANAGEMENT
# ==========================================

# On importe les outils nécessaires pour gérer les utilisateurs
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile

# Vue pour afficher la liste de tous les utilisateurs
@login_required
def liste_utilisateurs(request):
    # On récupère tous les profils utilisateurs
    profils = UserProfile.objects.all()
    return render(request, 'Restaurant/liste_utilisateurs.html', {'profils': profils})

# Vue pour créer un nouvel utilisateur avec un rôle
@login_required
def creer_utilisateur(request):
    if request.method == 'POST':
        # On récupère les données du formulaire
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        telephone = request.POST.get('telephone')

        # On crée l'utilisateur Django
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # On crée son profil avec le rôle
        UserProfile.objects.create(
            user=user,
            role=role,
            telephone=telephone
        )
        # On redirige vers la liste après création
        return redirect('/restaurant/utilisateurs/')

    return render(request, 'Restaurant/creer_utilisateur.html')

# Vue pour modifier le rôle d'un utilisateur
@login_required
def modifier_utilisateur(request, user_id):
    # On cherche le profil de l'utilisateur
    profil = UserProfile.objects.get(id=user_id)

    if request.method == 'POST':
        # On met à jour le rôle et le téléphone
        profil.role = request.POST.get('role')
        profil.telephone = request.POST.get('telephone')
        profil.save()
        return redirect('/restaurant/utilisateurs/')

    return render(request, 'Restaurant/modifier_utilisateur.html', {'profil': profil})

# Vue pour supprimer un utilisateur
@login_required
def supprimer_utilisateur(request, user_id):
    # On cherche et supprime le profil
    profil = UserProfile.objects.get(id=user_id)
    profil.user.delete()
    return redirect('/restaurant/utilisateurs/')

# Vue pour déconnecter un utilisateur
def deconnexion(request):
    # On déconnecte l'utilisateur et on redirige vers l'accueil
    logout(request)
    return redirect('/restaurant/')