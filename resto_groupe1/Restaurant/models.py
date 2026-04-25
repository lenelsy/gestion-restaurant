# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Table(models.Model):
    id_table = models.AutoField(primary_key=True)
    numero_table = models.IntegerField(unique=True)
    nb_places = models.IntegerField()

    def str(self):
        return f"Table {self.numero_table}"


class Employe(models.Model):
    id_employe = models.AutoField(primary_key=True)
    nom_emp = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default="Serveur")

    def str(self):
        return f"{self.nom_emp} ({self.role})"


class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    nom_prod = models.CharField(max_length=100)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def str(self):
        return self.nom_prod


class Commande(models.Model):
    TYPES = [('SUR_PLACE', 'Sur place'), ('LIVRAISON', 'Livraison')]

    id_commande = models.AutoField(primary_key=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    type_commande = models.CharField(max_length=20, choices=TYPES, default='SUR_PLACE')

    # Relations
    id_table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    id_employe = models.ForeignKey(Employe, on_delete=models.CASCADE)

    def str(self):
        return f"Commande {self.id_commande} ({self.type_commande})"


class LigneCommande(models.Model):
    id_commande = models.ForeignKey(Commande, related_name='lignes', on_delete=models.CASCADE)
    id_produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def sous_total(self):
        return self.id_produit.prix_unitaire * self.quantite