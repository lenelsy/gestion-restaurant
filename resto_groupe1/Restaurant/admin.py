from django.contrib import admin
from .models import Table, Employe, Produit, Commande, LigneCommande

admin.site.register(Produit)
admin.site.register(Table)
admin.site.register(Employe)
admin.site.register(Commande)
admin.site.register(LigneCommande)