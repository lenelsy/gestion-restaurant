"""
decorators.py — Décorateurs de contrôle d'accès par rôle
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restreint l'accès à une vue aux rôles spécifiés.
    Un superuser ou administrateur passe toujours.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            try:
                profil = request.user.profil
                if profil.role in roles or profil.role == 'administrateur':
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass
            messages.error(request, "⛔ Accès refusé : vous n'avez pas les permissions requises.")
            return redirect('dashboard')
        return wrapper
    return decorator


def login_required_custom(view_func):
    """Redirige vers login si non connecté."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
