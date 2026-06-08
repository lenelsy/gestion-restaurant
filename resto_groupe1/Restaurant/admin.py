"""
admin.py — Interface d'administration Django personnalisée
Permet à l'administrateur de tout gérer depuis /admin/
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    Profil, Client, Table, Reservation, Ingredient, Employe, Produit,
    Composition_Produit, Stock, Variation_Stock, Fournisseur, Poste,
    Affectation, Supervision, Vehicule, Deplacement, Approvisionnement,
    Equipement, Maintenance, Action_Marketing, Commande, Ligne_Commande,
    Livraison, Facture
)

# ── Personnalisation du site admin ────────────────────────────
admin.site.site_header  = "🍽️ RestaurantPro — Administration"
admin.site.site_title   = "RestaurantPro Admin"
admin.site.index_title  = "Tableau de bord administrateur"


# ══════════════════════════════════════════════════════════════
# PROFILS UTILISATEURS — intégré dans UserAdmin
# ══════════════════════════════════════════════════════════════

class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    verbose_name_plural = 'Profil & Rôle'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfilInline,)
    list_display  = ('username', 'get_full_name', 'email', 'get_role', 'is_active', 'date_joined')
    list_filter   = ('is_active', 'is_staff', 'profil__role')

    def get_role(self, obj):
        try:
            return obj.profil.get_role_display()
        except Exception:
            return '—'
    get_role.short_description = 'Rôle'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ══════════════════════════════════════════════════════════════
# PRODUITS & MENU
# ══════════════════════════════════════════════════════════════

class CompositionInline(admin.TabularInline):
    model = Composition_Produit
    extra = 1
    verbose_name = "Ingrédient"
    verbose_name_plural = "Composition (Ingrédients requis)"

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display   = ('id_Produit', 'Nom', 'Description', 'Prix','Disponible', 'id_Createur', 'Nombre_Personnes')
    list_filter    = ('Description', 'Disponible')
    search_fields  = ('Nom', 'Description')
    list_editable  = ('Prix', 'Disponible')          # Édition directe du prix depuis la liste
    inlines        = [CompositionInline]
    fieldsets = (
        ('Informations du plat', {
            'fields': ('Nom', 'Description', 'id_Createur', 'Nombre_Personnes', 'Duree_Cuisson')
        }),
        ('Tarification', {
            'fields': ('Prix', 'Disponible'),
            'classes': ('collapse',),
        }),
    )

    def disponibilite(self, obj):
        if obj.Disponible:
            return format_html('<span style="color:green;font-weight:bold">✓ Disponible</span>')
        return format_html('<span style="color:red;font-weight:bold">✗ Indisponible</span>')
    disponibilite.short_description = 'Disponibilité'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display  = ('id_Ingredient', 'Nom', 'Unite_de_Mesure', 'Type', 'stock_actuel')
    search_fields = ('Nom', 'Type')
    list_filter   = ('Type',)

    def stock_actuel(self, obj):
        try:
            s = obj.stock
            color = 'red' if s.en_alerte else 'green'
            return format_html('<span style="color:{};font-weight:bold">{} {}</span>',
                               color, s.Quantite_Actuelle, obj.Unite_de_Mesure)
        except Stock.DoesNotExist:
            return '—'
    stock_actuel.short_description = 'Stock actuel'


# ══════════════════════════════════════════════════════════════
# COMMANDES
# ══════════════════════════════════════════════════════════════

class LigneCommandeInline(admin.TabularInline):
    model   = Ligne_Commande
    extra   = 1
    readonly_fields = ('sous_total_affiche',)

    def sous_total_affiche(self, obj):
        return f"{obj.sous_total} FCFA" if obj.pk else '—'
    sous_total_affiche.short_description = 'Sous-total'

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display   = ('id_Commande', 'id_Client', 'Date', 'Type', 'montant_affiche', 'Mode_de_Paiement', 'statut_badge', 'prise_par')
    list_filter    = ('Type', 'Mode_de_Paiement', 'Statut')
    search_fields  = ('id_Client__Nom', 'id_Client__Prenom')
    readonly_fields = ('Montant_Total', 'Date')
    date_hierarchy = 'Date'
    inlines        = [LigneCommandeInline]

    def montant_affiche(self, obj):
        return f"{obj.Montant_Total:,} FCFA".replace(',', ' ')
    montant_affiche.short_description = 'Montant total'

    def statut_badge(self, obj):
        colors = {'en_cours': '#ffc107', 'prête': '#17a2b8', 'livrée': '#28a745', 'annulée': '#dc3545'}
        color = colors.get(obj.Statut, '#6c757d')
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:.8em">{}</span>',
                           color, obj.get_Statut_display())
    statut_badge.short_description = 'Statut'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('id_Client', 'Nom', 'Prenom', 'Tel', 'Email', 'Type_de_Client', 'nb_commandes')
    search_fields = ('Nom', 'Prenom', 'Email', 'Tel')
    list_filter   = ('Type_de_Client',)

    def nb_commandes(self, obj):
        return obj.commande_set.count()
    nb_commandes.short_description = 'Commandes'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display  = ('id_Reservation', 'id_Client', 'id_Table', 'Date', 'Heure', 'statut_badge')
    list_filter   = ('Statut', 'Date')
    date_hierarchy = 'Date'

    def statut_badge(self, obj):
        colors = {'Confirmée': 'green', 'Annulée': 'red', 'En attente': 'orange'}
        return format_html('<span style="color:{};font-weight:bold">{}</span>',
                           colors.get(obj.Statut, 'black'), obj.Statut)
    statut_badge.short_description = 'Statut'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id_Table', 'Numero_Table', 'Capacite', 'Commentaire')


# ══════════════════════════════════════════════════════════════
# STOCKS
# ══════════════════════════════════════════════════════════════

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id_Ingredient', 'Quantite_Actuelle', 'Seuil_Alerte', 'indicateur')
    list_editable = ('Seuil_Alerte',)

    def indicateur(self, obj):
        if obj.en_alerte:
            return format_html('<span style="color:red;font-weight:bold">⚠ ALERTE</span>')
        return format_html('<span style="color:green">✓ OK</span>')
    indicateur.short_description = 'Statut stock'

@admin.register(Variation_Stock)
class VariationStockAdmin(admin.ModelAdmin):
    list_display  = ('id_Variation', 'id_Ingredient', 'Date', 'type_badge', 'Quantite')
    list_filter   = ('Type', 'Date')
    date_hierarchy = 'Date'

    def type_badge(self, obj):
        color = 'green' if obj.Type == 'entrée' else 'red'
        label = '⬆ Entrée' if obj.Type == 'entrée' else '⬇ Sortie'
        return format_html('<span style="color:{};font-weight:bold">{}</span>', color, label)
    type_badge.short_description = 'Type'

@admin.register(Approvisionnement)
class ApprovisionnementAdmin(admin.ModelAdmin):
    list_display = ('id_Approvisionnement', 'id_Ingredient', 'id_Fournisseur', 'Date', 'Quantite', 'Prix_Unitaire', 'total')
    list_filter  = ('id_Fournisseur', 'Date')
    date_hierarchy = 'Date'

    def total(self, obj):
        return f"{obj.montant_total:,} FCFA".replace(',', ' ')
    total.short_description = 'Total'


# ══════════════════════════════════════════════════════════════
# RH
# ══════════════════════════════════════════════════════════════

class AffectationInline(admin.TabularInline):
    model = Affectation
    extra = 1

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('id_Employe', 'Nom', 'Prenom', 'Tel', 'salaire_formate', 'Date_Embauche', 'poste_actuel')
    search_fields = ('Nom', 'Prenom')
    inlines      = [AffectationInline]

    def salaire_formate(self, obj):
        return f"{obj.Salaire:,} FCFA".replace(',', ' ') if obj.Salaire else '—'
    salaire_formate.short_description = 'Salaire'

    def poste_actuel(self, obj):
        aff = Affectation.objects.filter(id_Employe=obj, Date_fin__isnull=True).first()
        return str(aff.id_Poste) if aff else '—'
    poste_actuel.short_description = 'Poste actuel'

@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ('id_Poste', 'Libelle_Poste', 'nb_employes')

    def nb_employes(self, obj):
        return Affectation.objects.filter(id_Poste=obj, Date_fin__isnull=True).count()
    nb_employes.short_description = 'Effectif actuel'

@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = ('id_Employe', 'id_Poste', 'Date_debut', 'Date_fin', 'actif')

    def actif(self, obj):
        if obj.est_active:
            return format_html('<span style="color:green;font-weight:bold">✓ En poste</span>')
        return '—'
    actif.short_description = 'Statut'


# ══════════════════════════════════════════════════════════════
# ÉQUIPEMENTS
# ══════════════════════════════════════════════════════════════

@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display  = ('id_Equipement', 'Nom', 'etat_badge', 'Date_Achat')
    list_filter   = ('Etat',)
    list_editable = ()

    def etat_badge(self, obj):
        colors = {'Fonctionnel': 'green', 'En panne': 'red', 'En maintenance': 'orange', 'Hors service': '#6c757d'}
        return format_html('<span style="color:{};font-weight:bold">{}</span>',
                           colors.get(obj.Etat, 'black'), obj.Etat)
    etat_badge.short_description = 'État'

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('id_Maintenance', 'id_Equipement', 'id_Technicien', 'Date', 'Type', 'Commentaire')
    list_filter  = ('Type', 'Date')
    date_hierarchy = 'Date'


# ══════════════════════════════════════════════════════════════
# FINANCE & MARKETING
# ══════════════════════════════════════════════════════════════

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('id_Facture', 'Date', 'type_et_montant', 'Type')
    list_filter  = ('Type',)
    date_hierarchy = 'Date'

    def type_et_montant(self, obj):
        color = 'green' if 'Client' in obj.Type else 'red'
        signe = '+' if 'Client' in obj.Type else '-'
        return format_html('<span style="color:{};font-weight:bold">{}{:,} FCFA</span>',
                           color, signe, obj.Montant)
    type_et_montant.short_description = 'Montant'

@admin.register(Action_Marketing)
class ActionMarketingAdmin(admin.ModelAdmin):
    list_display = ('id_Action', 'Type_Action', 'Description', 'Date_debut', 'Date_fin', 'budget_formate', 'id_Responsable')
    list_filter  = ('Type_Action',)
    date_hierarchy = 'Date_debut'

    def budget_formate(self, obj):
        return f"{obj.Budget:,} FCFA".replace(',', ' ') if obj.Budget else '—'
    budget_formate.short_description = 'Budget'


# ── Enregistrement des modèles simples ─────────────────────────
admin.site.register(Fournisseur)
admin.site.register(Vehicule)
admin.site.register(Deplacement)
admin.site.register(Livraison)
admin.site.register(Supervision)
