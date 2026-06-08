"""
views.py — Vues de l'application RestaurantPro
Modules : Auth, Dashboard, Clients, Tables, Réservations,
          Commandes, Produits, Stock, RH, Finance, Rapport
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, IntegerField
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    Client, Table, Reservation, Ingredient, Employe, Produit,
    Composition_Produit, Stock, Variation_Stock, Fournisseur, Poste,
    Affectation, Vehicule, Deplacement, Approvisionnement, Equipement,
    Maintenance, Action_Marketing, Commande, Ligne_Commande, Livraison, Facture
)
from .forms import (
    LoginForm, ClientForm, TableForm, ReservationForm, CommandeForm,
    LigneCommandeForm, ProduitForm, CompositionProduitForm, IngredientForm,
    StockForm, VariationStockForm, EmployeForm, AffectationForm, PosteForm,
    FournisseurForm, ApprovisionnementForm, EquipementForm, MaintenanceForm,
    ActionMarketingForm, FactureForm, VehiculeForm
)
from .decorators import role_required, login_required_custom


# ══════════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ══════════════════════════════════════════════════════════════

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Bienvenue, {user.get_full_name() or user.username} !")
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'Restaurant/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')


# ══════════════════════════════════════════════════════════════
# DASHBOARD (Module 5.7)
# ══════════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    today   = date.today()
    mois    = today.replace(day=1)

    # ── KPI principaux ─────────────────────────────────────────
    total_clients    = Client.objects.count()
    total_commandes  = Commande.objects.count()
    ca_total         = Commande.objects.aggregate(t=Sum('Montant_Total'))['t'] or 0
    total_employes   = Employe.objects.count()

    # CA du mois en cours
    ca_mois = Commande.objects.filter(
        Date__year=today.year, Date__month=today.month
    ).aggregate(t=Sum('Montant_Total'))['t'] or 0

    # ── Répartition CA par type ─────────────────────────────────
    ca_sur_place  = Commande.objects.filter(Type='Sur place').aggregate(t=Sum('Montant_Total'))['t'] or 0
    ca_livraison  = Commande.objects.filter(Type='À livrer').aggregate(t=Sum('Montant_Total'))['t'] or 0
    ca_emporter   = Commande.objects.filter(Type='À emporter').aggregate(t=Sum('Montant_Total'))['t'] or 0

    # ── Produits les plus vendus ────────────────────────────────
    top_produits = (
        Ligne_Commande.objects
        .values('id_Produit__Nom')
        .annotate(total_qte=Sum('Quantite'), total_ca=Sum(
            ExpressionWrapper(F('Quantite') * F('Prix_Unitaire'), output_field=IntegerField())
        ))
        .order_by('-total_qte')[:5]
    )

    # ── Stocks en alerte ────────────────────────────────────────
    stocks_alerte = [s for s in Stock.objects.select_related('id_Ingredient').all() if s.en_alerte]

    # ── Réservations aujourd'hui ────────────────────────────────
    reservations_jour = Reservation.objects.filter(Date=today, Statut='Confirmée').count()

    # ── Équipements en panne ────────────────────────────────────
    equipements_panne = Equipement.objects.filter(Etat='En panne').count()

    # ── Actions marketing actives ───────────────────────────────
    actions_actives = Action_Marketing.objects.filter(
        Date_debut__lte=today
    ).filter(Q(Date_fin__gte=today) | Q(Date_fin__isnull=True)).count()

    # ── Dernières commandes ─────────────────────────────────────
    commandes_recentes = Commande.objects.select_related('id_Client').order_by('-Date')[:8]

    # ── Dépenses approvisionnement du mois ─────────────────────
    depenses_appro = Approvisionnement.objects.filter(
        Date__year=today.year, Date__month=today.month
    ).aggregate(
        t=Sum(ExpressionWrapper(F('Quantite') * F('Prix_Unitaire'), output_field=IntegerField()))
    )['t'] or 0

    context = {
        'total_clients': total_clients,
        'total_commandes': total_commandes,
        'ca_total': ca_total,
        'ca_mois': ca_mois,
        'total_employes': total_employes,
        'ca_sur_place': ca_sur_place,
        'ca_livraison': ca_livraison,
        'ca_emporter': ca_emporter,
        'top_produits': top_produits,
        'stocks_alerte': stocks_alerte,
        'reservations_jour': reservations_jour,
        'equipements_panne': equipements_panne,
        'actions_actives': actions_actives,
        'commandes_recentes': commandes_recentes,
        'depenses_appro': depenses_appro,
        'mois_label': today.strftime('%B %Y'),
        'type_ca': [
            (ca_sur_place, '🪑 Sur place'),
            (ca_livraison, '🚚 À livrer'),
            (ca_emporter,  '🥡 À emporter'),
        ],
    }
    return render(request, 'Restaurant/dashboard.html', context)


# ══════════════════════════════════════════════════════════════
# RAPPORT FINANCIER (Module 5.7 — Dashboard détaillé)
# ══════════════════════════════════════════════════════════════

@login_required
@role_required('administrateur', 'directeur')
def rapport_financier(request):
    today = date.today()
    annee = int(request.GET.get('annee', today.year))
    mois  = int(request.GET.get('mois', today.month))

    debut = date(annee, mois, 1)
    if mois == 12:
        fin = date(annee + 1, 1, 1) - timedelta(days=1)
    else:
        fin = date(annee, mois + 1, 1) - timedelta(days=1)

    # CA du mois sélectionné
    commandes_mois = Commande.objects.filter(Date__date__gte=debut, Date__date__lte=fin)
    ca_mois        = commandes_mois.aggregate(t=Sum('Montant_Total'))['t'] or 0
    nb_commandes   = commandes_mois.count()

    # Dépenses approvisionnement
    appros_mois  = Approvisionnement.objects.filter(Date__gte=debut, Date__lte=fin)
    depenses_mois = appros_mois.aggregate(
        t=Sum(ExpressionWrapper(F('Quantite') * F('Prix_Unitaire'), output_field=IntegerField()))
    )['t'] or 0

    # Masse salariale (fixe mensuelle)
    masse_salariale = Employe.objects.aggregate(t=Sum('Salaire'))['t'] or 0

    # Solde
    solde = ca_mois - depenses_mois - masse_salariale

    # Répartition par type
    repartition = commandes_mois.values('Type').annotate(
        total=Sum('Montant_Total'), nb=Count('id_Commande')
    )

    # Top 5 produits du mois
    top_produits = (
        Ligne_Commande.objects
        .filter(id_Commande__in=commandes_mois)
        .values('id_Produit__Nom')
        .annotate(
            qte=Sum('Quantite'),
            ca=Sum(ExpressionWrapper(F('Quantite') * F('Prix_Unitaire'), output_field=IntegerField()))
        )
        .order_by('-qte')[:5]
    )

    context = {
        'annee': annee,
        'mois': mois,
        'mois_label': debut.strftime('%B %Y'),
        'ca_mois': ca_mois,
        'nb_commandes': nb_commandes,
        'depenses_mois': depenses_mois,
        'masse_salariale': masse_salariale,
        'solde': solde,
        'repartition': repartition,
        'top_produits': top_produits,
        'mois_choices': range(1, 13),
        'annee_choices': range(2024, today.year + 1),
    }
    return render(request, 'Restaurant/rapport_financier.html', context)


# ══════════════════════════════════════════════════════════════
# CLIENTS
# ══════════════════════════════════════════════════════════════

@login_required
def client_list(request):
    q = request.GET.get('q', '').strip()
    qs = Client.objects.all()
    if q:
        qs = qs.filter(Q(Nom__icontains=q) | Q(Prenom__icontains=q) | Q(Email__icontains=q) | Q(Tel__icontains=q))
    return render(request, 'Restaurant/client_list.html', {'clients': qs, 'q': q})

@login_required
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ Client ajouté avec succès.")
        return redirect('client_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouveau client', 'back_url': 'client_list', 'icone': '👤'})

@login_required
def client_update(request, pk):
    obj = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ Client modifié.")
        return redirect('client_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj}', 'back_url': 'client_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def client_delete(request, pk):
    obj = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "🗑️ Client supprimé.")
        return redirect('client_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'client_list'})


# ══════════════════════════════════════════════════════════════
# TABLES
# ══════════════════════════════════════════════════════════════

@login_required
def table_list(request):
    return render(request, 'Restaurant/table_list.html', {'tables': Table.objects.all()})

@login_required
@role_required('administrateur', 'directeur')
def table_create(request):
    form = TableForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Table ajoutée.")
        return redirect('table_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle table', 'back_url': 'table_list', 'icone': '🪑'})

@login_required
@role_required('administrateur', 'directeur')
def table_update(request, pk):
    obj = get_object_or_404(Table, pk=pk)
    form = TableForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Table modifiée.")
        return redirect('table_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj}', 'back_url': 'table_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def table_delete(request, pk):
    obj = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Table supprimée.")
        return redirect('table_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'table_list'})


# ══════════════════════════════════════════════════════════════
# RÉSERVATIONS
# ══════════════════════════════════════════════════════════════

@login_required
def reservation_list(request):
    qs = Reservation.objects.select_related('id_Client', 'id_Table').order_by('-Date', 'Heure')
    return render(request, 'Restaurant/reservation_list.html', {'reservations': qs})

@login_required
def reservation_create(request):
    form = ReservationForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Réservation créée.")
        return redirect('reservation_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle réservation', 'back_url': 'reservation_list', 'icone': '📅'})

@login_required
def reservation_update(request, pk):
    obj = get_object_or_404(Reservation, pk=pk)
    form = ReservationForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Réservation modifiée.")
        return redirect('reservation_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier réservation #{pk}', 'back_url': 'reservation_list', 'icone': '✏️'})

@login_required
def reservation_delete(request, pk):
    obj = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Réservation supprimée.")
        return redirect('reservation_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'reservation_list'})


# ══════════════════════════════════════════════════════════════
# COMMANDES (Module 5.4 — Calcul automatique, Facture)
# ══════════════════════════════════════════════════════════════

@login_required
def commande_list(request):
    qs = Commande.objects.select_related('id_Client').order_by('-Date')
    return render(request, 'Restaurant/commande_list.html', {'commandes': qs})

@login_required
@role_required('administrateur', 'directeur', 'serveur')
def commande_create(request):
    form = CommandeForm(request.POST or None)
    if form.is_valid():
        cmd = form.save(commit=False)
        cmd.prise_par = request.user
        cmd.save()
        messages.success(request, f"✅ Commande #{cmd.id_Commande} créée. Ajoutez maintenant les plats.")
        return redirect('commande_detail', pk=cmd.pk)
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle commande', 'back_url': 'commande_list', 'icone': '🛒'})

@login_required
def commande_detail(request, pk):
    cmd    = get_object_or_404(Commande, pk=pk)
    lignes = Ligne_Commande.objects.filter(id_Commande=cmd).select_related('id_Produit')
    form   = LigneCommandeForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ligne = form.save(commit=False)
        ligne.id_Commande = cmd
        # Prix auto depuis le produit si 0
        if not ligne.Prix_Unitaire:
            ligne.Prix_Unitaire = ligne.id_Produit.Prix
        try:
            ligne.save()
            messages.success(request, f"✅ {ligne.id_Produit.Nom} ajouté à la commande.")
        except Exception:
            messages.warning(request, "Ce plat est déjà dans la commande.")
        return redirect('commande_detail', pk=pk)

    return render(request, 'Restaurant/commande_detail.html', {
        'commande': cmd, 'lignes': lignes, 'form': form,
        'produits': Produit.objects.filter(Disponible=True)
    })

@login_required
@role_required('administrateur', 'directeur', 'serveur')
def commande_update(request, pk):
    obj  = get_object_or_404(Commande, pk=pk)
    form = CommandeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Commande modifiée.")
        return redirect('commande_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier commande #{pk}', 'back_url': 'commande_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def commande_delete(request, pk):
    obj = get_object_or_404(Commande, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Commande supprimée.")
        return redirect('commande_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'commande_list'})

@login_required
def ligne_delete(request, pk):
    ligne = get_object_or_404(Ligne_Commande, pk=pk)
    cmd_pk = ligne.id_Commande_id
    ligne.delete()
    ligne.id_Commande.recalculer_total()
    messages.success(request, "Ligne supprimée.")
    return redirect('commande_detail', pk=cmd_pk)

@login_required
def facture_commande(request, pk):
    """Génère la facture PDF-style d'une commande."""
    cmd    = get_object_or_404(Commande, pk=pk)
    lignes = Ligne_Commande.objects.filter(id_Commande=cmd).select_related('id_Produit')
    return render(request, 'Restaurant/facture_commande.html', {'commande': cmd, 'lignes': lignes})


# ══════════════════════════════════════════════════════════════
# PRODUITS / MENU (Module 5.3 — Catalogue, catégorie, prix)
# ══════════════════════════════════════════════════════════════

@login_required
def produit_list(request):
    cat = request.GET.get('cat', '')
    qs  = Produit.objects.select_related('id_Createur').all()
    if cat:
        qs = qs.filter(Description=cat)
    cats = Produit.objects.values_list('Description', flat=True).distinct()
    return render(request, 'Restaurant/produit_list.html', {'produits': qs, 'cats': cats, 'cat_active': cat})

@login_required
@role_required('administrateur', 'directeur', 'chef_cuisinier')
def produit_create(request):
    form = ProduitForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Produit ajouté au menu.")
        return redirect('produit_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouveau plat', 'back_url': 'produit_list', 'icone': '🍽️'})

@login_required
@role_required('administrateur', 'directeur', 'chef_cuisinier')
def produit_update(request, pk):
    obj  = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, instance=obj)
    compo_form = CompositionProduitForm()
    compositions = Composition_Produit.objects.filter(id_Produit=obj).select_related('id_Ingredient')

    if request.method == 'POST':
        if 'save_produit' in request.POST and form.is_valid():
            form.save(); messages.success(request, "✅ Plat modifié.")
            return redirect('produit_list')
        elif 'add_ingredient' in request.POST:
            compo_form = CompositionProduitForm(request.POST)
            if compo_form.is_valid():
                c = compo_form.save(commit=False)
                c.id_Produit = obj
                try:
                    c.save(); messages.success(request, "✅ Ingrédient ajouté.")
                except Exception:
                    messages.warning(request, "Cet ingrédient est déjà dans la recette.")
            return redirect('produit_update', pk=pk)

    return render(request, 'Restaurant/produit_update.html', {
        'form': form, 'compo_form': compo_form,
        'produit': obj, 'compositions': compositions
    })

@login_required
@role_required('administrateur', 'directeur')
def produit_delete(request, pk):
    obj = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Produit supprimé.")
        return redirect('produit_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'produit_list'})

@login_required
@role_required('administrateur', 'directeur', 'chef_cuisinier')
def composition_delete(request, pk):
    c = get_object_or_404(Composition_Produit, pk=pk)
    prod_pk = c.id_Produit_id
    c.delete(); messages.success(request, "Ingrédient retiré.")
    return redirect('produit_update', pk=prod_pk)


# ══════════════════════════════════════════════════════════════
# STOCK & INVENTAIRE (Module 5.5)
# ══════════════════════════════════════════════════════════════

@login_required
def stock_list(request):
    stocks = Stock.objects.select_related('id_Ingredient').all()
    return render(request, 'Restaurant/stock_list.html', {'stocks': stocks})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock')
def stock_update(request, pk):
    obj  = get_object_or_404(Stock, pk=pk)
    form = StockForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Stock mis à jour.")
        return redirect('stock_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier stock : {obj.id_Ingredient.Nom}', 'back_url': 'stock_list', 'icone': '📦'})

@login_required
def variation_stock_list(request):
    qs = Variation_Stock.objects.select_related('id_Ingredient', 'enregistre_par').order_by('-Date')
    return render(request, 'Restaurant/variation_stock_list.html', {'variations': qs})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock')
def variation_stock_create(request):
    form = VariationStockForm(request.POST or None)
    if form.is_valid():
        v = form.save(commit=False)
        v.enregistre_par = request.user
        v.save()
        messages.success(request, f"✅ Variation de stock enregistrée. Stock mis à jour automatiquement.")
        return redirect('stock_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle variation de stock', 'back_url': 'stock_list', 'icone': '📊'})


# ══════════════════════════════════════════════════════════════
# INGRÉDIENTS
# ══════════════════════════════════════════════════════════════

@login_required
def ingredient_list(request):
    return render(request, 'Restaurant/ingredient_list.html', {'ingredients': Ingredient.objects.all()})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock', 'chef_cuisinier')
def ingredient_create(request):
    form = IngredientForm(request.POST or None)
    if form.is_valid():
        ing = form.save()
        Stock.objects.get_or_create(id_Ingredient=ing)  # Crée un stock à 0 automatiquement
        messages.success(request, "✅ Ingrédient ajouté + stock initialisé.")
        return redirect('ingredient_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvel ingrédient', 'back_url': 'ingredient_list', 'icone': '🌿'})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock', 'chef_cuisinier')
def ingredient_update(request, pk):
    obj  = get_object_or_404(Ingredient, pk=pk)
    form = IngredientForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Ingrédient modifié.")
        return redirect('ingredient_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj.Nom}', 'back_url': 'ingredient_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def ingredient_delete(request, pk):
    obj = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Ingrédient supprimé.")
        return redirect('ingredient_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'ingredient_list'})


# ══════════════════════════════════════════════════════════════
# EMPLOYÉS (Module 5.6 — RH, Affectations)
# ══════════════════════════════════════════════════════════════

@login_required
def employe_list(request):
    employes = Employe.objects.prefetch_related('affectation_set__id_Poste').all()
    masse_salariale = Employe.objects.aggregate(t=Sum('Salaire'))['t'] or 0
    return render(request, 'Restaurant/employe_list.html', {'employes': employes, 'masse_salariale': masse_salariale})

@login_required
@role_required('administrateur', 'directeur')
def employe_create(request):
    form = EmployeForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Employé ajouté.")
        return redirect('employe_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvel employé', 'back_url': 'employe_list', 'icone': '👷'})

@login_required
@role_required('administrateur', 'directeur')
def employe_update(request, pk):
    obj  = get_object_or_404(Employe, pk=pk)
    form = EmployeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Employé modifié.")
        return redirect('employe_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj}', 'back_url': 'employe_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def employe_delete(request, pk):
    obj = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Employé supprimé.")
        return redirect('employe_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'employe_list'})

@login_required
@role_required('administrateur', 'directeur')
def affectation_list(request):
    return render(request, 'Restaurant/affectation_list.html',
                  {'affectations': Affectation.objects.select_related('id_Employe', 'id_Poste').all()})

@login_required
@role_required('administrateur', 'directeur')
def affectation_create(request):
    form = AffectationForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Affectation créée.")
        return redirect('affectation_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle affectation', 'back_url': 'affectation_list', 'icone': '📋'})

@login_required
def poste_list(request):
    return render(request, 'Restaurant/poste_list.html', {'postes': Poste.objects.annotate(nb=Count('affectation'))})

@login_required
@role_required('administrateur', 'directeur')
def poste_create(request):
    form = PosteForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Poste créé.")
        return redirect('poste_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouveau poste', 'back_url': 'poste_list', 'icone': '💼'})


# ══════════════════════════════════════════════════════════════
# FOURNISSEURS & APPROVISIONNEMENTS
# ══════════════════════════════════════════════════════════════

@login_required
def fournisseur_list(request):
    return render(request, 'Restaurant/fournisseur_list.html', {'fournisseurs': Fournisseur.objects.all()})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock')
def fournisseur_create(request):
    form = FournisseurForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Fournisseur ajouté.")
        return redirect('fournisseur_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouveau fournisseur', 'back_url': 'fournisseur_list', 'icone': '🏪'})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock')
def fournisseur_update(request, pk):
    obj = get_object_or_404(Fournisseur, pk=pk)
    form = FournisseurForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Fournisseur modifié.")
        return redirect('fournisseur_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj}', 'back_url': 'fournisseur_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def fournisseur_delete(request, pk):
    obj = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Fournisseur supprimé.")
        return redirect('fournisseur_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'fournisseur_list'})

@login_required
def approvisionnement_list(request):
    qs = Approvisionnement.objects.select_related('id_Ingredient', 'id_Fournisseur').order_by('-Date')
    return render(request, 'Restaurant/approvisionnement_list.html', {'appros': qs})

@login_required
@role_required('administrateur', 'directeur', 'gestionnaire_stock')
def approvisionnement_create(request):
    form = ApprovisionnementForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Approvisionnement enregistré.")
        return redirect('approvisionnement_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvel approvisionnement', 'back_url': 'approvisionnement_list', 'icone': '🚚'})

@login_required
@role_required('administrateur', 'directeur')
def approvisionnement_delete(request, pk):
    obj = get_object_or_404(Approvisionnement, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Approvisionnement supprimé.")
        return redirect('approvisionnement_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'approvisionnement_list'})


# ══════════════════════════════════════════════════════════════
# ÉQUIPEMENTS & MAINTENANCE
# ══════════════════════════════════════════════════════════════

@login_required
def equipement_list(request):
    return render(request, 'Restaurant/equipement_list.html', {'equipements': Equipement.objects.all()})

@login_required
@role_required('administrateur', 'directeur')
def equipement_create(request):
    form = EquipementForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Équipement ajouté.")
        return redirect('equipement_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvel équipement', 'back_url': 'equipement_list', 'icone': '🔧'})

@login_required
@role_required('administrateur', 'directeur')
def equipement_update(request, pk):
    obj = get_object_or_404(Equipement, pk=pk)
    form = EquipementForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Équipement modifié.")
        return redirect('equipement_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj.Nom}', 'back_url': 'equipement_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def equipement_delete(request, pk):
    obj = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Équipement supprimé.")
        return redirect('equipement_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'equipement_list'})

@login_required
def maintenance_list(request):
    return render(request, 'Restaurant/maintenance_list.html',
                  {'maintenances': Maintenance.objects.select_related('id_Equipement', 'id_Technicien').order_by('-Date')})

@login_required
@role_required('administrateur', 'directeur')
def maintenance_create(request):
    form = MaintenanceForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Maintenance enregistrée.")
        return redirect('maintenance_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle maintenance', 'back_url': 'maintenance_list', 'icone': '🔩'})

@login_required
@role_required('administrateur', 'directeur')
def maintenance_delete(request, pk):
    obj = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Maintenance supprimée.")
        return redirect('maintenance_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'maintenance_list'})


# ══════════════════════════════════════════════════════════════
# MARKETING
# ══════════════════════════════════════════════════════════════

@login_required
def marketing_list(request):
    return render(request, 'Restaurant/marketing_list.html',
                  {'actions': Action_Marketing.objects.select_related('id_Responsable').order_by('-Date_debut')})

@login_required
@role_required('administrateur', 'directeur')
def marketing_create(request):
    form = ActionMarketingForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Action marketing créée.")
        return redirect('marketing_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle action marketing', 'back_url': 'marketing_list', 'icone': '📢'})

@login_required
@role_required('administrateur', 'directeur')
def marketing_update(request, pk):
    obj = get_object_or_404(Action_Marketing, pk=pk)
    form = ActionMarketingForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Action modifiée.")
        return redirect('marketing_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Modifier action', 'back_url': 'marketing_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def marketing_delete(request, pk):
    obj = get_object_or_404(Action_Marketing, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Action supprimée.")
        return redirect('marketing_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'marketing_list'})


# ══════════════════════════════════════════════════════════════
# FACTURES
# ══════════════════════════════════════════════════════════════

@login_required
@role_required('administrateur', 'directeur')
def facture_list(request):
    return render(request, 'Restaurant/facture_list.html', {'factures': Facture.objects.order_by('-Date')})

@login_required
@role_required('administrateur', 'directeur')
def facture_create(request):
    form = FactureForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Facture créée.")
        return redirect('facture_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouvelle facture', 'back_url': 'facture_list', 'icone': '🧾'})

@login_required
@role_required('administrateur', 'directeur')
def facture_delete(request, pk):
    obj = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Facture supprimée.")
        return redirect('facture_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'facture_list'})


# ══════════════════════════════════════════════════════════════
# VÉHICULES
# ══════════════════════════════════════════════════════════════

@login_required
def vehicule_list(request):
    return render(request, 'Restaurant/vehicule_list.html', {'vehicules': Vehicule.objects.all()})

@login_required
@role_required('administrateur', 'directeur')
def vehicule_create(request):
    form = VehiculeForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Véhicule ajouté.")
        return redirect('vehicule_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': 'Nouveau véhicule', 'back_url': 'vehicule_list', 'icone': '🚗'})

@login_required
@role_required('administrateur', 'directeur')
def vehicule_update(request, pk):
    obj = get_object_or_404(Vehicule, pk=pk)
    form = VehiculeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "✅ Véhicule modifié.")
        return redirect('vehicule_list')
    return render(request, 'Restaurant/form.html', {'form': form, 'titre': f'Modifier : {obj}', 'back_url': 'vehicule_list', 'icone': '✏️'})

@login_required
@role_required('administrateur', 'directeur')
def vehicule_delete(request, pk):
    obj = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        obj.delete(); messages.success(request, "🗑️ Véhicule supprimé.")
        return redirect('vehicule_list')
    return render(request, 'Restaurant/confirm_delete.html', {'objet': obj, 'back_url': 'vehicule_list'})


# ══════════════════════════════════════════════════════════════
# PAGE ACCUEIL PUBLIQUE
# ══════════════════════════════════════════════════════════════

def accueil(request):
    produits_vedette = Produit.objects.filter(Disponible=True).order_by('?')[:4]
    steps = [
        (1, '🍽️', 'Choisissez vos plats', 'Parcourez notre menu et ajoutez vos plats préférés au panier.'),
        (2, '🛒', 'Vérifiez votre panier', 'Ajustez les quantités et vérifiez votre sélection.'),
        (3, '📝', 'Renseignez vos infos', 'Nom, téléphone, mode de service et paiement.'),
        (4, '🧾', 'Recevez votre facture', 'Votre commande est confirmée et la facture générée instantanément.'),
    ]
    return render(request, 'Restaurant/accueil.html', {'produits_vedette': produits_vedette, 'steps': steps})


# ══════════════════════════════════════════════════════════════
# MENU PUBLIC
# ══════════════════════════════════════════════════════════════

def menu_public(request):
    cat = request.GET.get('cat', '')
    produits = Produit.objects.filter(Disponible=True).order_by('Description', 'Nom')
    if cat:
        produits = produits.filter(Description=cat)
    categories = Produit.objects.filter(Disponible=True).values_list('Description', flat=True).distinct()
    panier = request.session.get('panier', {})
    nb_panier = sum(int(v.get('quantite', 0)) for v in panier.values())
    return render(request, 'Restaurant/menu_public.html', {
        'produits': produits,
        'categories': categories,
        'cat_active': cat,
        'nb_panier': nb_panier,
    })


# ══════════════════════════════════════════════════════════════
# PANIER (session)
# ══════════════════════════════════════════════════════════════

def panier_ajouter(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    panier = request.session.get('panier', {})
    key = str(pk)
    if key in panier:
        panier[key]['quantite'] = int(panier[key].get('quantite', 0)) + 1
    else:
        panier[key] = {
            'id': pk,
            'nom': produit.Nom,
            'prix': int(produit.Prix or 0),
            'quantite': 1,
            'categorie': produit.Description or '',
        }
    request.session['panier'] = panier
    request.session.modified = True
    messages.success(request, f"✅ {produit.Nom} ajouté au panier.")
    return redirect(request.META.get('HTTP_REFERER', 'menu_public'))


def panier_retirer(request, pk):
    panier = request.session.get('panier', {})
    key = str(pk)
    if key in panier:
        qte = int(panier[key].get('quantite', 1))
        if qte > 1:
            panier[key]['quantite'] = qte - 1
        else:
            del panier[key]
    request.session['panier'] = panier
    request.session.modified = True
    return redirect('panier_voir')


def panier_supprimer(request, pk):
    panier = request.session.get('panier', {})
    key = str(pk)
    if key in panier:
        del panier[key]
    request.session['panier'] = panier
    request.session.modified = True
    return redirect('panier_voir')


def panier_voir(request):
    panier = request.session.get('panier', {})
    items = []
    total = 0
    for key, item in panier.items():
        prix = int(item.get('prix') or 0)
        qte  = int(item.get('quantite') or 1)
        sous_total = prix * qte
        total += sous_total
        items.append({
            'id': item['id'],
            'nom': item['nom'],
            'prix': prix,
            'quantite': qte,
            'sous_total': sous_total,
        })
    return render(request, 'Restaurant/panier.html', {'items': items, 'total': total})


def panier_vider(request):
    request.session['panier'] = {}
    request.session.modified = True
    messages.info(request, "🗑️ Panier vidé.")
    return redirect('menu_public')


# ══════════════════════════════════════════════════════════════
# VALIDER COMMANDE + FACTURE PUBLIQUE
# ══════════════════════════════════════════════════════════════

def valider_commande(request):
    panier = request.session.get('panier', {})
    if not panier:
        messages.warning(request, "⚠️ Votre panier est vide.")
        return redirect('menu_public')

    if request.method == 'POST':
        nom      = request.POST.get('nom', '').strip()
        prenom   = request.POST.get('prenom', '').strip()
        tel      = request.POST.get('tel', '').strip()
        type_cmd = request.POST.get('type_commande', 'Sur place')
        paiement = request.POST.get('paiement', 'Espèces')

        if not nom or not prenom:
            messages.error(request, "❌ Veuillez renseigner votre nom et prénom.")
            return redirect('valider_commande')

        client, _ = Client.objects.get_or_create(
            Nom=nom.upper(), Prenom=prenom.capitalize(),
            defaults={'Tel': tel, 'Type_de_Client': 'Particulier'}
        )

        total = sum(
            int(i.get('prix') or 0) * int(i.get('quantite') or 1)
            for i in panier.values()
        )

        commande = Commande.objects.create(
            id_Client=client,
            Type=type_cmd,
            Montant_Total=total,
            Mode_de_Paiement=paiement,
            Statut='en_cours',
        )

        for key, item in panier.items():
            try:
                produit = Produit.objects.get(pk=item['id'])
                Ligne_Commande.objects.create(
                    id_Commande=commande,
                    id_Produit=produit,
                    Quantite=int(item.get('quantite') or 1),
                    Prix_Unitaire=int(item.get('prix') or produit.Prix or 0),
                )
            except Produit.DoesNotExist:
                continue

        commande.recalculer_total()
        request.session['panier'] = {}
        request.session.modified = True
        messages.success(request, f"✅ Commande #{commande.id_Commande} validée !")
        return redirect('facture_publique', pk=commande.pk)

    # GET
    items = []
    total = 0
    for key, item in panier.items():
        prix = int(item.get('prix') or 0)
        qte  = int(item.get('quantite') or 1)
        sous_total = prix * qte
        total += sous_total
        items.append({'nom': item['nom'], 'prix': prix, 'quantite': qte, 'sous_total': sous_total})

    return render(request, 'Restaurant/valider_commande.html', {'items': items, 'total': total})


def facture_publique(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    lignes   = Ligne_Commande.objects.filter(id_Commande=commande).select_related('id_Produit')
    return render(request, 'Restaurant/facture_publique.html', {'commande': commande, 'lignes': lignes})
