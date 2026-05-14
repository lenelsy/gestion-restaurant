# On importe le module admin de Django
# C'est lui qui gère l'interface /admin/
from django.contrib import admin

# On importe tous les modèles de notre fichier models.py
# Chaque modèle = une table dans la base de données MySQL
from .models import Ingredient, Produit, Client, Reservation, Commande, UserProfile

# ==========================================
# ENREGISTREMENT DES MODELES DANS L'ADMIN
# ==========================================

# Rend la table Ingredient visible et gérable dans /admin/
admin.site.register(Ingredient)

# Rend la table Produit visible et gérable dans /admin/
admin.site.register(Produit)

# Rend la table Client visible et gérable dans /admin/
admin.site.register(Client)

# Rend la table Reservation visible et gérable dans /admin/
admin.site.register(Reservation)

# Rend la table Commande visible et gérable dans /admin/
admin.site.register(Commande)

# Rend la table UserProfile visible et gérable dans /admin/
# C'est notre nouveau modèle du module User Management
admin.site.register(UserProfile)