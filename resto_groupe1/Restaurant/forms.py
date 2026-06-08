"""
forms.py — Formulaires Django pour toutes les entités
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Client, Table, Reservation, Ingredient, Employe, Produit,
    Composition_Produit, Stock, Variation_Stock, Fournisseur, Poste,
    Affectation, Vehicule, Deplacement, Approvisionnement, Equipement,
    Maintenance, Action_Marketing, Commande, Ligne_Commande, Facture
)

# ── Widget commun ───────────────────────────────────────────────
W_TEXT  = {'class': 'form-control'}
W_SEL   = {'class': 'form-select'}
W_DATE  = {'class': 'form-control', 'type': 'date'}
W_TIME  = {'class': 'form-control', 'type': 'time'}
W_DT    = {'class': 'form-control', 'type': 'datetime-local'}
W_NUM   = {'class': 'form-control', 'step': '1'}
W_DEC   = {'class': 'form-control', 'step': '0.01'}
W_AREA  = {'class': 'form-control', 'rows': '3'}
W_CHECK = {'class': 'form-check-input'}


# ─── AUTHENTIFICATION ──────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d_utilisateur',
        widget=forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Identifiant', 'autofocus': True})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={**W_TEXT, 'placeholder': 'Mot de passe'})
    )


# ─── CLIENTS ──────────────────────────────────────────────────
class ClientForm(forms.ModelForm):
    class Meta:
        model   = Client
        fields  = ['Nom', 'Prenom', 'Tel', 'Email', 'Type_de_Client']
        widgets = {
            'Nom':            forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Nom de famille'}),
            'Prenom':         forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Prénom'}),
            'Tel':            forms.TextInput(attrs={**W_TEXT, 'placeholder': '6XXXXXXXX'}),
            'Email':          forms.EmailInput(attrs={**W_TEXT, 'placeholder': 'exemple@email.com'}),
            'Type_de_Client': forms.Select(attrs=W_SEL),
        }


# ─── TABLES ────────────────────────────────────────────────────
class TableForm(forms.ModelForm):
    class Meta:
        model   = Table
        fields  = ['Numero_Table', 'Capacite', 'Commentaire']
        widgets = {
            'Numero_Table': forms.TextInput(attrs={**W_TEXT, 'placeholder': 'T1'}),
            'Capacite':     forms.NumberInput(attrs={**W_NUM, 'min': '1'}),
            'Commentaire':  forms.Textarea(attrs=W_AREA),
        }


# ─── RÉSERVATIONS ──────────────────────────────────────────────
class ReservationForm(forms.ModelForm):
    class Meta:
        model   = Reservation
        fields  = ['id_Client', 'id_Table', 'Date', 'Heure', 'Statut']
        widgets = {
            'id_Client': forms.Select(attrs=W_SEL),
            'id_Table':  forms.Select(attrs=W_SEL),
            'Date':      forms.DateInput(attrs=W_DATE),
            'Heure':     forms.TimeInput(attrs=W_TIME),
            'Statut':    forms.Select(attrs=W_SEL),
        }
        labels = {'id_Client': 'Client', 'id_Table': 'Table'}


# ─── COMMANDES ─────────────────────────────────────────────────
class CommandeForm(forms.ModelForm):
    class Meta:
        model   = Commande
        fields  = ['id_Client', 'Type', 'Mode_de_Paiement', 'Statut']
        widgets = {
            'id_Client':        forms.Select(attrs=W_SEL),
            'Type':             forms.Select(attrs=W_SEL),
            'Mode_de_Paiement': forms.Select(attrs=W_SEL),
            'Statut':           forms.Select(attrs=W_SEL),
        }
        labels = {'id_Client': 'Client'}


class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model   = Ligne_Commande
        fields  = ['id_Produit', 'Quantite', 'Prix_Unitaire']
        widgets = {
            'id_Produit':    forms.Select(attrs=W_SEL),
            'Quantite':      forms.NumberInput(attrs={**W_DEC, 'min': '1', 'value': '1'}),
            'Prix_Unitaire': forms.NumberInput(attrs={**W_NUM, 'min': '0'}),
        }
        labels = {'id_Produit': 'Plat / Produit'}


# ─── PRODUITS ──────────────────────────────────────────────────
class ProduitForm(forms.ModelForm):
    class Meta:
        model   = Produit
        fields  = ['Nom', 'Description', 'id_Createur', 'Duree_Cuisson', 'Nombre_Personnes', 'Prix', 'Disponible']
        widgets = {
            'Nom':              forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Nom du plat'}),
            'Description':      forms.Select(attrs=W_SEL),
            'id_Createur':      forms.Select(attrs=W_SEL),
            'Duree_Cuisson':    forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Ex: 45 minutes'}),
            'Nombre_Personnes': forms.NumberInput(attrs={**W_NUM, 'min': '1'}),
            'Prix':             forms.NumberInput(attrs={**W_NUM, 'min': '0', 'placeholder': 'Prix en FCFA'}),
            'Disponible':       forms.CheckboxInput(attrs=W_CHECK),
        }
        labels = {
            'id_Createur': 'Chef en charge',
            'Description': 'Catégorie',
        }


class CompositionProduitForm(forms.ModelForm):
    class Meta:
        model   = Composition_Produit
        fields  = ['id_Ingredient', 'Quantite_Utilisee']
        widgets = {
            'id_Ingredient':    forms.Select(attrs=W_SEL),
            'Quantite_Utilisee': forms.NumberInput(attrs={**W_DEC, 'min': '0.01'}),
        }
        labels = {'id_Ingredient': 'Ingrédient', 'Quantite_Utilisee': 'Quantité'}


# ─── INGRÉDIENTS ───────────────────────────────────────────────
class IngredientForm(forms.ModelForm):
    class Meta:
        model   = Ingredient
        fields  = ['Nom', 'Unite_de_Mesure', 'Type']
        widgets = {
            'Nom':            forms.TextInput(attrs=W_TEXT),
            'Unite_de_Mesure': forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Kg, Litre, Paquet...'}),
            'Type':           forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Protéine, Légume...'}),
        }


# ─── STOCKS ────────────────────────────────────────────────────
class StockForm(forms.ModelForm):
    class Meta:
        model   = Stock
        fields  = ['Quantite_Actuelle', 'Seuil_Alerte']
        widgets = {
            'Quantite_Actuelle': forms.NumberInput(attrs={**W_DEC, 'min': '0'}),
            'Seuil_Alerte':      forms.NumberInput(attrs={**W_DEC, 'min': '0'}),
        }


class VariationStockForm(forms.ModelForm):
    class Meta:
        model   = Variation_Stock
        fields  = ['id_Ingredient', 'Date', 'Type', 'Quantite']
        widgets = {
            'id_Ingredient': forms.Select(attrs=W_SEL),
            'Date':          forms.DateInput(attrs=W_DATE),
            'Type':          forms.Select(attrs=W_SEL),
            'Quantite':      forms.NumberInput(attrs={**W_DEC, 'min': '0.01'}),
        }
        labels = {'id_Ingredient': 'Ingrédient'}


# ─── EMPLOYÉS ──────────────────────────────────────────────────
class EmployeForm(forms.ModelForm):
    class Meta:
        model   = Employe
        fields  = ['Nom', 'Prenom', 'Tel', 'Salaire', 'Date_Embauche']
        widgets = {
            'Nom':           forms.TextInput(attrs=W_TEXT),
            'Prenom':        forms.TextInput(attrs=W_TEXT),
            'Tel':           forms.TextInput(attrs={**W_TEXT, 'placeholder': '6XXXXXXXX'}),
            'Salaire':       forms.NumberInput(attrs={**W_NUM, 'min': '0', 'placeholder': 'FCFA'}),
            'Date_Embauche': forms.DateInput(attrs=W_DATE),
        }


class AffectationForm(forms.ModelForm):
    class Meta:
        model   = Affectation
        fields  = ['id_Employe', 'id_Poste', 'Date_debut', 'Date_fin']
        widgets = {
            'id_Employe': forms.Select(attrs=W_SEL),
            'id_Poste':   forms.Select(attrs=W_SEL),
            'Date_debut': forms.DateInput(attrs=W_DATE),
            'Date_fin':   forms.DateInput(attrs=W_DATE),
        }
        labels = {'id_Employe': 'Employé', 'id_Poste': 'Poste'}


class PosteForm(forms.ModelForm):
    class Meta:
        model   = Poste
        fields  = ['Libelle_Poste']
        widgets = {'Libelle_Poste': forms.TextInput(attrs=W_TEXT)}


# ─── FOURNISSEURS ──────────────────────────────────────────────
class FournisseurForm(forms.ModelForm):
    class Meta:
        model   = Fournisseur
        fields  = ['Nom', 'Tel', 'Adresse']
        widgets = {
            'Nom':     forms.TextInput(attrs=W_TEXT),
            'Tel':     forms.TextInput(attrs=W_TEXT),
            'Adresse': forms.TextInput(attrs=W_TEXT),
        }


# ─── APPROVISIONNEMENTS ────────────────────────────────────────
class ApprovisionnementForm(forms.ModelForm):
    class Meta:
        model   = Approvisionnement
        fields  = ['id_Ingredient', 'id_Fournisseur', 'id_Deplacement', 'Date', 'Quantite', 'Prix_Unitaire']
        widgets = {
            'id_Ingredient':  forms.Select(attrs=W_SEL),
            'id_Fournisseur': forms.Select(attrs=W_SEL),
            'id_Deplacement': forms.Select(attrs=W_SEL),
            'Date':           forms.DateInput(attrs=W_DATE),
            'Quantite':       forms.NumberInput(attrs={**W_DEC, 'min': '0.01'}),
            'Prix_Unitaire':  forms.NumberInput(attrs={**W_NUM, 'min': '0'}),
        }
        labels = {'id_Ingredient': 'Ingrédient', 'id_Fournisseur': 'Fournisseur'}


# ─── ÉQUIPEMENTS & MAINTENANCE ─────────────────────────────────
class EquipementForm(forms.ModelForm):
    class Meta:
        model   = Equipement
        fields  = ['Nom', 'Etat', 'Date_Achat']
        widgets = {
            'Nom':       forms.TextInput(attrs=W_TEXT),
            'Etat':      forms.Select(attrs=W_SEL),
            'Date_Achat': forms.DateInput(attrs=W_DATE),
        }


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model   = Maintenance
        fields  = ['id_Technicien', 'id_Equipement', 'Date', 'Type', 'Commentaire']
        widgets = {
            'id_Technicien':  forms.Select(attrs=W_SEL),
            'id_Equipement':  forms.Select(attrs=W_SEL),
            'Date':           forms.DateInput(attrs=W_DATE),
            'Type':           forms.Select(attrs=W_SEL),
            'Commentaire':    forms.Textarea(attrs=W_AREA),
        }
        labels = {'id_Technicien': 'Technicien', 'id_Equipement': 'Équipement'}


# ─── MARKETING ─────────────────────────────────────────────────
class ActionMarketingForm(forms.ModelForm):
    class Meta:
        model   = Action_Marketing
        fields  = ['id_Responsable', 'Type_Action', 'Description', 'Date_debut', 'Date_fin', 'Budget']
        widgets = {
            'id_Responsable': forms.Select(attrs=W_SEL),
            'Type_Action':    forms.TextInput(attrs={**W_TEXT, 'placeholder': 'Promo, Publicité...'}),
            'Description':    forms.Textarea(attrs=W_AREA),
            'Date_debut':     forms.DateInput(attrs=W_DATE),
            'Date_fin':       forms.DateInput(attrs=W_DATE),
            'Budget':         forms.NumberInput(attrs={**W_NUM, 'min': '0'}),
        }
        labels = {'id_Responsable': 'Responsable'}


# ─── FACTURES ──────────────────────────────────────────────────
class FactureForm(forms.ModelForm):
    class Meta:
        model   = Facture
        fields  = ['Date', 'Montant', 'Type']
        widgets = {
            'Date':    forms.DateInput(attrs=W_DATE),
            'Montant': forms.NumberInput(attrs={**W_NUM, 'min': '0'}),
            'Type':    forms.TextInput(attrs=W_TEXT),
        }


# ─── VÉHICULES ─────────────────────────────────────────────────
class VehiculeForm(forms.ModelForm):
    class Meta:
        model   = Vehicule
        fields  = ['Immatriculation', 'Modele', 'Marque']
        widgets = {
            'Immatriculation': forms.TextInput(attrs=W_TEXT),
            'Modele':          forms.TextInput(attrs=W_TEXT),
            'Marque':          forms.TextInput(attrs=W_TEXT),
        }
