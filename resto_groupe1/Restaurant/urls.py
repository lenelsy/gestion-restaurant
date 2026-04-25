from django.urls import path
from . import views

urlpatterns = [
    path('catalogue/', views.catalogue_produits, name='catalogue'),
]