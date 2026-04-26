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