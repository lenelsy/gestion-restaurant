# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


# ==========================================
# MODULE : PRODUCT MANAGEMENT
# ==========================================

class Ingredient(models.Model):
    # PK Id_Ingredient est gérée automatiquement par Django (id)
    nom = models.CharField(max_length=255)
    unite_de_mesure = models.CharField(max_length=50)

    def get_stock(self):
        # Logique pour vérifier le stock
        pass

    def __str__(self):
        return self.nom


class Produit(models.Model):
    # FK Id_Ingredient
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, null=True)
    nom = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    duree_cuisson = models.CharField(max_length=50)
    nombre_personnes = models.IntegerField()
    quantite_utilisee = models.DecimalField(max_digits=10, decimal_places=2)

    def calculer_cout(self):
        pass

    def verifier_ingredient(self):
        pass

    def __str__(self):
        return self.nom


# ==========================================
# MODULE : ORDER MANAGEMENT
# ==========================================

class Client(models.Model):
    # FK Id_Table (Intégré comme attribut selon ton schéma)
    id_table = models.IntegerField()
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    type_de_client = models.CharField(max_length=50)
    table_capacite = models.IntegerField()
    table_statut = models.CharField(max_length=50)
    commentaire = models.TextField(blank=True, null=True)

    def passer_commande(self):
        pass

    def faire_reservation(self):
        pass

    def __str__(self):
        return f"commande {self.id} - {self.produit.nom}"


class Reservation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    id_table = models.IntegerField()
    date = models.DateField()
    heure = models.TimeField()
    nombre_personnes = models.IntegerField()
    statut = models.CharField(max_length=50)


class Commande(models.Model):
    # Les relations (Clés étrangères)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, null=True)

    # Les attributs
    id_table = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mode_paiement = models.CharField(max_length=50)
    mode_livraison = models.CharField(max_length=50)
    adresse_livraison = models.CharField(max_length=255, blank=True, null=True)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    # La méthode de calcul demandée
    def calculer_total(self):
        self.montant_total = self.quantite * self.prix_unitaire
        return self.montant_total

    def save(self, *args, **kwargs):
        self.calculer_total()
        super().save(*args, **kwargs)

    def generer_facture(self):
        pass

    def __str__(self):
        return f"Commande {self.id} - {self.produit.nom}"
    
    # ==========================================
# MODULE : USER MANAGEMENT
# ==========================================

# On importe le modèle User intégré de Django
# Django a déjà une table User avec username, password, email
from django.contrib.auth.models import User

# UserProfile étend le User Django avec un rôle spécifique
# Chaque utilisateur du restaurant aura un profil avec son rôle
class UserProfile(models.Model):
    
    # Liste des rôles possibles dans le restaurant
    # Format : ('valeur_en_base', 'Affichage à l écran')
    ROLES = [
        ('admin', 'Administrateur'),          # Gère tout le système
        ('directeur', 'Directeur'),            # Supervise le restaurant
        ('chef_cuisinier', 'Chef Cuisinier'),  # Gère la cuisine
        ('cuisinier', 'Cuisinier'),            # Prépare les plats
        ('serveur', 'Serveur'),                # Gère les commandes
        ('gestionnaire_stock', 'Gestionnaire de Stock'), # Gère les stocks
    ]
    
    # Lien vers le User Django — un profil = un seul utilisateur
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Le rôle de cet utilisateur dans le restaurant
    role = models.CharField(max_length=50, choices=ROLES)
    
    # Numéro de téléphone (optionnel)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    
    # Affichage lisible dans l'interface admin
    def __str__(self):
        return f"{self.user.username} - {self.role}"