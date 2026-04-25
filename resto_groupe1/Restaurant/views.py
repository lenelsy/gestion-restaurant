from django.shortcuts import render
from .models import Produit

def catalogue_produits(request):
    # Récupère tous les plats (Poulet DG, Ndolé, etc.) de ta base SQL
    plats = Produit.objects.all()
    return render(request, 'Restaurant/catalogue.html', {'plats': plats})
