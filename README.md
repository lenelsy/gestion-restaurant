# Restaurant Manager

Application web de gestion de restaurant développée avec Django et MySQL.

## Prérequis
- Python 3.9+
- MySQL 8.0+
- pip
  
## Installation
**1. Cloner le projet**
```bash
git clone https://github.com/lenelsy/gestion-restaurant
```
**2. Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```
**3. Installer les dépendances**
```bash
pip install -r requirements.txt
```
**4. Créer la base de données MySQL**
```bash
mysql -u root -p
```
```sql
CREATE DATABASE Restaurant;
EXIT;
```
**5. Importer le schéma et les données**
```bash
mysql -u root -p Restaurant < Base_Restaurant.sql
```
**6. Configurer la connexion dans `settings.py`**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Restaurant',
        'USER': 'root',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
**7. Appliquer les migrations**
```bash
python manage.py migrate
```
**8. Créer un compte administrateur**
```bash
python manage.py createsuperuser
```
## Lancer l'application
```bash
python manage.py runserver
```
Ouvrir dans le navigateur : **http://127.0.0.1:8000**
Interface admin : **http://127.0.0.1:8000/admin**
## Fonctionnalités
- Authentification et gestion des rôles (Admin, Directeur, Chef, Cuisinier, Serveur, Gestionnaire stock)
- Gestion des produits et recettes
- Gestion des commandes et factures
- Gestion du stock avec alertes
- Gestion des employés et des postes
- Gestion des livraisons et véhicules
- Gestion des fournisseurs
- Tableau de bord avec statistiques

## Documents

Le rapport technique du projet est disponible dans le dossier `/docs/rapport_final.pdf`
