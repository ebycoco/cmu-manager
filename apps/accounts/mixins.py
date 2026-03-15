from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import User
from .permissions import user_is_admin_or_superadmin

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class BannedUserAccessMixin:
    """
    Bloque l'accès si l'utilisateur est banni.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_banned:
            raise PermissionDenied("Votre compte est banni.")
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedNotBannedMixin(LoginRequiredMixin, BannedUserAccessMixin):
    """
    Utilisateur connecté et non banni.
    """
    pass


class SuperAdminRequiredMixin(AuthenticatedNotBannedMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == self.request.user.Role.SUPERADMIN

    def handle_no_permission(self):
        raise PermissionDenied("Accès réservé au super administrateur.")


class AdminOrSuperAdminRequiredMixin(AuthenticatedNotBannedMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in [
            self.request.user.Role.SUPERADMIN,
            self.request.user.Role.ADMIN,
        ]

    def handle_no_permission(self):
        raise PermissionDenied("Accès réservé aux administrateurs.")


class OperatorOrAdminMixin(AuthenticatedNotBannedMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in [
            self.request.user.Role.SUPERADMIN,
            self.request.user.Role.ADMIN,
            self.request.user.Role.OPERATOR,
        ]

    def handle_no_permission(self):
        raise PermissionDenied("Vous n'avez pas les droits nécessaires.")

class OperatorRequiredMixin(AuthenticatedNotBannedMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == self.request.user.Role.OPERATOR

    def handle_no_permission(self):
        raise PermissionDenied("Accès réservé aux opérateurs.")

class AdminUserManagementAccessMixin:
    """
    Accès réservé aux administrateurs et super administrateurs.
    """

    def dispatch(self, request, *args, **kwargs):
        if not user_is_admin_or_superadmin(request.user):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class TargetUserAccessMixin:
    """
    Récupère un utilisateur cible et applique les restrictions métier :
    - un administrateur ne peut pas agir sur un super administrateur.
    """

    def get_target_user(self, request, pk):
        user_obj = get_object_or_404(User, pk=pk)

        if request.user.role == User.Role.ADMIN and user_obj.role == User.Role.SUPERADMIN:
            return None

        return user_obj

    def handle_forbidden_target(self, request, message):
        messages.error(request, message)
        return redirect('user_list')
