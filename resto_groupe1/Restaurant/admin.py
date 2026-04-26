from django.contrib import admin
from .models import Ingredient, Produit, Client, Reservation, Commande

# Enregistrement simple et sécurisé
admin.site.register(Ingredient)
admin.site.register(Produit)
admin.site.register(Client)
admin.site.register(Reservation)
admin.site.register(Commande)