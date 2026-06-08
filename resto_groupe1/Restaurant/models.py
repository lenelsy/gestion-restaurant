"""
models.py — Modèles Django pour l'application RestaurantPro
Basé sur la base de données MySQL : Base_Restaurant.sql
ENSPY - 2025-2026
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


# ══════════════════════════════════════════════════════════════
# MODULE 5.1 — GESTION DES UTILISATEURS / RÔLES
# ══════════════════════════════════════════════════════════════

ROLE_CHOICES = [
    ('administrateur', 'Administrateur'),
    ('directeur',      'Directeur'),
    ('chef_cuisinier', 'Chef Cuisinier'),
    ('cuisinier',      'Cuisinier'),
    ('serveur',        'Serveur'),
    ('gestionnaire_stock', 'Gestionnaire de Stock'),
]

class Profil(models.Model):
    """Extension du User Django pour gérer les rôles métier."""
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role       = models.CharField(max_length=30, choices=ROLE_CHOICES, default='serveur')
    employe    = models.OneToOneField('Employe', on_delete=models.SET_NULL, null=True, blank=True)
    telephone  = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.get_role_display()}"

    # ── Helpers de permission ──────────────────────────────────
    @property
    def is_admin(self):
        return self.role == 'administrateur' or self.user.is_superuser

    @property
    def is_directeur_or_above(self):
        return self.role in ('administrateur', 'directeur') or self.user.is_superuser

    @property
    def can_manage_stock(self):
        return self.role in ('administrateur', 'directeur', 'gestionnaire_stock')

    @property
    def can_manage_orders(self):
        return self.role in ('administrateur', 'directeur', 'serveur')

    @property
    def can_manage_products(self):
        return self.role in ('administrateur', 'directeur', 'chef_cuisinier')


# ══════════════════════════════════════════════════════════════
# MODULE 5.3 — GESTION DES PRODUITS
# ══════════════════════════════════════════════════════════════

class Ingredient(models.Model):
    """Ingrédients utilisés dans la composition des plats."""
    id_Ingredient   = models.AutoField(primary_key=True)
    Nom             = models.CharField(max_length=45, verbose_name='Nom')
    Unite_de_Mesure = models.CharField(max_length=45, blank=True, null=True, verbose_name='Unité de mesure')
    Type            = models.CharField(max_length=30, blank=True, null=True, verbose_name='Type')

    class Meta:
        db_table = 'Ingredient'
        verbose_name = 'Ingrédient'
        verbose_name_plural = 'Ingrédients'
        ordering = ['Nom']

    def __str__(self):
        return f"{self.Nom} ({self.Unite_de_Mesure})"


class Employe(models.Model):
    """Table des employés du Restaurant."""
    id_Employe    = models.AutoField(primary_key=True)
    Nom           = models.CharField(max_length=20, verbose_name='Nom')
    Prenom        = models.CharField(max_length=20, verbose_name='Prénom')
    Tel           = models.CharField(max_length=15, blank=True, null=True, verbose_name='Téléphone')
    Salaire       = models.IntegerField(blank=True, null=True,
                                        validators=[MinValueValidator(0)],
                                        verbose_name='Salaire (FCFA)')
    Date_Embauche = models.DateField(blank=True, null=True, verbose_name="Date d'embauche")

    class Meta:
        db_table = 'Employe'
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
        ordering = ['Nom', 'Prenom']

    def __str__(self):
        return f"{self.Prenom} {self.Nom}"


class Produit(models.Model):
    """Plats / boissons du menu — 5.3 : catalogue, catégorisation, prix dynamique."""
    CATEGORIE_CHOICES = [
        ('Plat',    'Plat principal'),
        ('Entrée',  'Entrée'),
        ('Dessert', 'Dessert'),
        ('Boisson', 'Boisson'),
        ('Autre',   'Autre'),
    ]
    id_Produit       = models.AutoField(primary_key=True)
    id_Createur      = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True, blank=True,
                                         db_column='id_Createur', verbose_name='Chef en charge')
    Nom              = models.CharField(max_length=30, verbose_name='Nom du plat')
    Description      = models.CharField(max_length=45, blank=True, null=True, verbose_name='Catégorie',
                                        choices=CATEGORIE_CHOICES)
    Duree_Cuisson    = models.CharField(max_length=20, blank=True, null=True, verbose_name='Durée de cuisson')
    Nombre_Personnes = models.IntegerField(blank=True, null=True, verbose_name='Nombre de personnes')
    # Tarification dynamique
    Prix             = models.IntegerField(default=0, validators=[MinValueValidator(0)],
                                           verbose_name='Prix (FCFA)')
    Disponible       = models.BooleanField(default=True, verbose_name='Disponible au menu')

    class Meta:
        db_table = 'Produit'
        verbose_name = 'Produit / Plat'
        verbose_name_plural = 'Produits / Plats'
        ordering = ['Description', 'Nom']

    def __str__(self):
        return self.Nom

    def get_ingredients(self):
        return Composition_Produit.objects.filter(id_Produit=self).select_related('id_Ingredient')


class Composition_Produit(models.Model):
    """Association plat–ingrédient avec quantité requise."""
    id_Produit       = models.ForeignKey(Produit,    on_delete=models.CASCADE, db_column='id_Produit',
                                          verbose_name='Plat')
    id_Ingredient    = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column='id_Ingredient',
                                          verbose_name='Ingrédient')
    Quantite_Utilisee = models.DecimalField(max_digits=10, decimal_places=2,
                                             validators=[MinValueValidator(Decimal('0.01'))],
                                             verbose_name='Quantité utilisée')

    class Meta:
        db_table = 'Composition_Produit'
        unique_together = (('id_Produit', 'id_Ingredient'),)
        verbose_name = 'Composition du produit'
        verbose_name_plural = 'Compositions des produits'

    def __str__(self):
        return f"{self.id_Produit} ← {self.id_Ingredient} ({self.Quantite_Utilisee})"


# ══════════════════════════════════════════════════════════════
# MODULE 5.4 — GESTION DES COMMANDES
# ══════════════════════════════════════════════════════════════

class Client(models.Model):
    """Clients du Restaurant."""
    TYPE_CHOICES = [('Particulier', 'Particulier'), ('Entreprise', 'Entreprise')]
    id_Client      = models.AutoField(primary_key=True)
    Nom            = models.CharField(max_length=20, blank=True, default='')
    Prenom         = models.CharField(max_length=20, blank=True, default='')
    Tel            = models.CharField(max_length=15, blank=True, null=True, verbose_name='Téléphone')
    Email          = models.EmailField(max_length=45, blank=True, null=True, verbose_name='Email')
    Type_de_Client = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                       default='Particulier')

    class Meta:
        db_table = 'Client'

    def __str__(self):
        return f"{self.Prenom} {self.Nom}"


class Table(models.Model):
    """Tables physiques du Restaurant."""
    id_Table      = models.AutoField(primary_key=True)
    Numero_Table  = models.CharField(max_length=3, unique=True, verbose_name='Numéro')
    Capacite      = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Capacité')
    Commentaire   = models.TextField(blank=True, null=True, verbose_name='Commentaire')

    class Meta:
        db_table = 'Table'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['Numero_Table']

    def __str__(self):
        return f"Table {self.Numero_Table} ({self.Capacite} places)"


class Commande(models.Model):
    """Commande client — sur place, livraison ou à emporter."""
    TYPE_CHOICES = [
        ('Sur place',  'Sur place'),
        ('À livrer',   'À livrer'),
        ('À emporter', 'À emporter'),
    ]
    PAIEMENT_CHOICES = [
        ('Espèces',       'Espèces'),
        ('Orange Money',  'Orange Money'),
        ('MTN MoMo',      'MTN MoMo'),
        ('Carte Bancaire','Carte Bancaire'),
    ]
    STATUT_CHOICES = [
        ('en_cours',  'En cours'),
        ('prête',     'Prête'),
        ('livrée',    'Livrée / Servie'),
        ('annulée',   'Annulée'),
    ]
    id_Commande       = models.AutoField(primary_key=True)
    id_Client         = models.ForeignKey(Client, on_delete=models.CASCADE,
                                           db_column='id_Client', verbose_name='Client')
    Date              = models.DateTimeField(auto_now_add=True, verbose_name='Date', null=True)
    Type              = models.CharField(max_length=30, choices=TYPE_CHOICES, default='Sur place', verbose_name='Type')
    Montant_Total     = models.IntegerField(default=0, verbose_name='Montant total (FCFA)')
    Mode_de_Paiement  = models.CharField(max_length=45, choices=PAIEMENT_CHOICES,
                                         default='Espèces',
                                          verbose_name='Mode de paiement')
    Statut            = models.CharField(max_length=20, choices=STATUT_CHOICES,
                                          default='en_cours', verbose_name='Statut')
    prise_par         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                           verbose_name='Prise par')

    class Meta:
        db_table = 'Commande'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-Date']

    def __str__(self):
        return f"Commande #{self.id_Commande} — {self.id_Client}"

    def recalculer_total(self):
        """Recalcule et sauvegarde le montant total depuis les lignes."""
        from django.db.models import Sum, F, ExpressionWrapper, IntegerField
        result = self.lignes.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('Prix_Unitaire') * F('Quantite'),
                    output_field=IntegerField()
                )
            )
        )
        self.Montant_Total = result['total'] or 0
        self.save(update_fields=['Montant_Total'])


class Ligne_Commande(models.Model):
    """Détail d'une commande : quel plat, quelle quantité, quel prix."""
    id_Commande   = models.ForeignKey(Commande, on_delete=models.CASCADE,
                                       db_column='id_Commande', related_name='lignes',
                                       verbose_name='Commande')
    id_Produit    = models.ForeignKey(Produit, on_delete=models.CASCADE,
                                       db_column='id_Produit', verbose_name='Plat')
    Quantite      = models.DecimalField(max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(Decimal('0.01'))],
                                         verbose_name='Quantité')
    Prix_Unitaire = models.IntegerField(verbose_name='Prix unitaire (FCFA)')

    class Meta:
        db_table = 'Ligne_Commande'
        unique_together = (('id_Commande', 'id_Produit'),)
        verbose_name = 'Ligne de commande'
        verbose_name_plural = 'Lignes de commande'

    def __str__(self):
        return f"Cmd#{self.id_Commande_id} — {self.id_Produit}"

    @property
    def sous_total(self):
        return int(self.Quantite * self.Prix_Unitaire)

    def save(self, *args, **kwargs):
        """Pré-remplit le prix depuis le produit si non renseigné."""
        if not self.Prix_Unitaire and self.id_Produit_id:
            self.Prix_Unitaire = Produit.objects.get(pk=self.id_Produit_id).Prix
        super().save(*args, **kwargs)
        # Recalcul automatique du total commande
        self.id_Commande.recalculer_total()


class Reservation(models.Model):
    """Réservation de table."""
    STATUT_CHOICES = [
        ('Confirmée',  'Confirmée'),
        ('Annulée',    'Annulée'),
        ('En attente', 'En attente'),
    ]
    id_Reservation = models.AutoField(primary_key=True)
    id_Client      = models.ForeignKey(Client, on_delete=models.CASCADE,
                                        db_column='id_Client', verbose_name='Client')
    id_Table       = models.ForeignKey(Table, on_delete=models.CASCADE,
                                        db_column='id_Table', verbose_name='Table')
    Date           = models.DateField(verbose_name='Date')
    Heure          = models.TimeField(verbose_name='Heure')
    Statut         = models.CharField(max_length=45, choices=STATUT_CHOICES,
                                       default='En attente', verbose_name='Statut')

    class Meta:
        db_table = 'Reservation'
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-Date', 'Heure']

    def __str__(self):
        return f"Résa #{self.id_Reservation} — {self.id_Client} le {self.Date}"


# ══════════════════════════════════════════════════════════════
# MODULE 5.5 — GESTION DES STOCKS / INVENTAIRE
# ══════════════════════════════════════════════════════════════

class Stock(models.Model):
    """Quantité actuelle en stock pour chaque ingrédient."""
    id_Ingredient      = models.OneToOneField(Ingredient, on_delete=models.CASCADE,
                                               primary_key=True, db_column='id_Ingredient',
                                               verbose_name='Ingrédient')
    Quantite_Actuelle  = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                              verbose_name='Quantité actuelle')
    Seuil_Alerte       = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                              verbose_name="Seuil d'alerte")

    class Meta:
        db_table = 'Stock'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'

    def __str__(self):
        return f"Stock — {self.id_Ingredient.Nom}: {self.Quantite_Actuelle}"

    @property
    def en_alerte(self):
        """Retourne True si la quantité est sous le seuil critique."""
        return self.Quantite_Actuelle <= self.Seuil_Alerte

    @property
    def pourcentage(self):
        """Pourcentage du stock par rapport au double du seuil."""
        if self.Seuil_Alerte <= 0:
            return 100
        ref = self.Seuil_Alerte * 4
        return min(100, int((self.Quantite_Actuelle / ref) * 100))


class Variation_Stock(models.Model):
    """Historique des entrées/sorties de stock."""
    TYPE_CHOICES = [('entrée', 'Entrée'), ('sortie', 'Sortie')]
    id_Variation  = models.AutoField(primary_key=True)
    id_Ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                       db_column='id_Ingredient', verbose_name='Ingrédient')
    Date          = models.DateField(verbose_name='Date')
    Type          = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Type')
    Quantite      = models.DecimalField(max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(Decimal('0.01'))],
                                         verbose_name='Quantité')
    enregistre_par = models.ForeignKey(User, on_delete=models.SET_NULL,
                                        null=True, blank=True, verbose_name='Enregistré par')

    class Meta:
        db_table = 'Variation_Stock'
        verbose_name = 'Variation de stock'
        verbose_name_plural = 'Variations de stock'
        ordering = ['-Date']

    def __str__(self):
        return f"{self.Type} — {self.id_Ingredient} ({self.Quantite}) le {self.Date}"

    def save(self, *args, **kwargs):
        """Met à jour automatiquement la quantité en stock."""
        super().save(*args, **kwargs)
        stock, _ = Stock.objects.get_or_create(id_Ingredient=self.id_Ingredient)
        if self.Type == 'entrée':
            stock.Quantite_Actuelle += self.Quantite
        else:
            stock.Quantite_Actuelle = max(0, stock.Quantite_Actuelle - self.Quantite)
        stock.save()


# ══════════════════════════════════════════════════════════════
# MODULE 5.6 — GESTION RH
# ══════════════════════════════════════════════════════════════

class Poste(models.Model):
    """Postes occupés dans le Restaurant."""
    id_Poste      = models.AutoField(primary_key=True)
    Libelle_Poste = models.CharField(max_length=45, verbose_name='Libellé du poste')

    class Meta:
        db_table = 'Poste'
        verbose_name = 'Poste'
        verbose_name_plural = 'Postes'

    def __str__(self):
        return self.Libelle_Poste


class Affectation(models.Model):
    """Affectation d'un employé à un poste."""
    id_Employe = models.ForeignKey(Employe, on_delete=models.CASCADE,
                                    db_column='id_Employe', verbose_name='Employé')
    id_Poste   = models.ForeignKey(Poste, on_delete=models.CASCADE,
                                    db_column='id_Poste', verbose_name='Poste')
    Date_debut = models.DateField(verbose_name='Date de début')
    Date_fin   = models.DateField(blank=True, null=True, verbose_name='Date de fin')

    class Meta:
        db_table = 'Affectation'
        unique_together = (('id_Employe', 'id_Poste'),)
        verbose_name = 'Affectation'
        verbose_name_plural = 'Affectations'

    def __str__(self):
        return f"{self.id_Employe} → {self.id_Poste}"

    @property
    def est_active(self):
        return self.Date_fin is None


class Supervision(models.Model):
    id_Superviseur = models.ForeignKey(Employe, on_delete=models.CASCADE,
                                        related_name='superviseur', db_column='id_Superviseur',
                                        verbose_name='Superviseur')
    id_Employe     = models.ForeignKey(Employe, on_delete=models.CASCADE,
                                        related_name='supervise', db_column='id_Employe',
                                        verbose_name='Employé supervisé')
    Date_debut     = models.DateField()
    Date_fin       = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'Supervision'
        unique_together = (('id_Superviseur', 'id_Employe'),)
        verbose_name = 'Supervision'
        verbose_name_plural = 'Supervisions'

    def __str__(self):
        return f"{self.id_Superviseur} supervise {self.id_Employe}"


# ══════════════════════════════════════════════════════════════
# APPROVISIONNEMENT & LOGISTIQUE
# ══════════════════════════════════════════════════════════════

class Fournisseur(models.Model):
    id_Fournisseur = models.AutoField(primary_key=True)
    Nom            = models.CharField(max_length=45, verbose_name='Nom')
    Tel            = models.CharField(max_length=15, blank=True, null=True)
    Adresse        = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        db_table = 'Fournisseur'
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'

    def __str__(self):
        return self.Nom


class Vehicule(models.Model):
    id_Vehicule      = models.AutoField(primary_key=True)
    Immatriculation  = models.CharField(max_length=15)
    Modele           = models.CharField(max_length=20, blank=True, null=True)
    Marque           = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'Vehicule'
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'

    def __str__(self):
        return f"{self.Marque} {self.Modele} ({self.Immatriculation})"


class Deplacement(models.Model):
    id_Deplacement  = models.AutoField(primary_key=True)
    id_Chauffeur    = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True,
                                         db_column='id_Chauffeur', verbose_name='Chauffeur')
    id_Vehicule     = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True,
                                         db_column='id_Vehicule', verbose_name='Véhicule')
    Date_depart     = models.DateTimeField(verbose_name='Date de départ')
    Destination     = models.TextField(blank=True, null=True)
    Distance_totale = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'Deplacement'
        verbose_name = 'Déplacement'
        verbose_name_plural = 'Déplacements'

    def __str__(self):
        return f"Déplacement #{self.id_Deplacement} → {self.Destination}"


class Approvisionnement(models.Model):
    id_Approvisionnement = models.AutoField(primary_key=True)
    id_Ingredient        = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                              db_column='id_Ingredient', verbose_name='Ingrédient')
    id_Fournisseur       = models.ForeignKey(Fournisseur, on_delete=models.CASCADE,
                                              db_column='id_Fournisseur', verbose_name='Fournisseur')
    id_Deplacement       = models.ForeignKey(Deplacement, on_delete=models.SET_NULL,
                                              null=True, blank=True, db_column='id_Deplacement')
    Date                 = models.DateField(verbose_name='Date')
    Quantite             = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Quantité')
    Prix_Unitaire        = models.IntegerField(verbose_name='Prix unitaire (FCFA)')

    class Meta:
        db_table = 'Approvisionnement'
        verbose_name = 'Approvisionnement'
        verbose_name_plural = 'Approvisionnements'
        ordering = ['-Date']

    def __str__(self):
        return f"Appro #{self.id_Approvisionnement} — {self.id_Ingredient}"

    @property
    def montant_total(self):
        return int(self.Quantite * self.Prix_Unitaire)


# ══════════════════════════════════════════════════════════════
# ÉQUIPEMENTS & MAINTENANCE
# ══════════════════════════════════════════════════════════════

class Equipement(models.Model):
    ETAT_CHOICES = [
        ('Fonctionnel',    'Fonctionnel'),
        ('En panne',       'En panne'),
        ('En maintenance', 'En maintenance'),
        ('Hors service',   'Hors service'),
    ]
    id_Equipement = models.AutoField(primary_key=True)
    Nom           = models.CharField(max_length=45)
    Etat          = models.CharField(max_length=45, choices=ETAT_CHOICES, default='Fonctionnel')
    Date_Achat    = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'Equipement'
        verbose_name = 'Équipement'
        verbose_name_plural = 'Équipements'

    def __str__(self):
        return f"{self.Nom} ({self.Etat})"


class Maintenance(models.Model):
    TYPE_CHOICES = [('Corrective', 'Corrective'), ('Préventive', 'Préventive')]
    id_Maintenance = models.AutoField(primary_key=True)
    id_Technicien  = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True,
                                        db_column='id_Technicien', verbose_name='Technicien')
    id_Equipement  = models.ForeignKey(Equipement, on_delete=models.CASCADE,
                                        db_column='id_Equipement', verbose_name='Équipement')
    Date           = models.DateField()
    Type           = models.CharField(max_length=45, choices=TYPE_CHOICES)
    Commentaire    = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Maintenance'
        verbose_name = 'Maintenance'
        verbose_name_plural = 'Maintenances'
        ordering = ['-Date']

    def __str__(self):
        return f"Maintenance {self.id_Equipement} — {self.Date}"


# ══════════════════════════════════════════════════════════════
# FINANCE — FACTURES & MARKETING
# ══════════════════════════════════════════════════════════════

class Facture(models.Model):
    id_Facture = models.AutoField(primary_key=True)
    Date       = models.DateField()
    Montant    = models.IntegerField()
    Type       = models.CharField(max_length=60)

    class Meta:
        db_table = 'Facture'
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-Date']

    def __str__(self):
        return f"Facture #{self.id_Facture} — {self.Type} ({self.Montant} FCFA)"


class Livraison(models.Model):
    id_Livraison   = models.AutoField(primary_key=True)
    id_Commande    = models.OneToOneField(Commande, on_delete=models.CASCADE,
                                           db_column='id_Commande', verbose_name='Commande')
    id_Deplacement = models.ForeignKey(Deplacement, on_delete=models.SET_NULL,
                                        null=True, db_column='id_Deplacement')

    class Meta:
        db_table = 'Livraison'
        verbose_name = 'Livraison'
        verbose_name_plural = 'Livraisons'

    def __str__(self):
        return f"Livraison #{self.id_Livraison}"


class Action_Marketing(models.Model):
    id_Action      = models.AutoField(primary_key=True)
    id_Responsable = models.ForeignKey(Employe, on_delete=models.SET_NULL,
                                        null=True, db_column='id_Responsable',
                                        verbose_name='Responsable')
    Type_Action    = models.CharField(max_length=20, verbose_name="Type d'action")
    Description    = models.TextField(blank=True, null=True)
    Date_debut     = models.DateField(verbose_name='Date de début')
    Date_fin       = models.DateField(blank=True, null=True, verbose_name='Date de fin')
    Budget         = models.IntegerField(blank=True, null=True, verbose_name='Budget (FCFA)')

    class Meta:
        db_table = 'Action_Marketing'
        verbose_name = 'Action Marketing'
        verbose_name_plural = 'Actions Marketing'
        ordering = ['-Date_debut']

    def __str__(self):
        return f"{self.Type_Action} — {self.Description}"

