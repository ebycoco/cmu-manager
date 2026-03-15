from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View

from .forms import (
    AdminUserCreateForm,
    AdminUserUpdateForm,
    CustomAuthenticationForm,
    CustomPasswordChangeForm,
    SuperAdminUserCreateForm,
    SuperAdminUserUpdateForm,
    UserSearchForm,
)
from .mixins import AdminUserManagementAccessMixin, TargetUserAccessMixin
from .models import User
from .permissions import user_is_superadmin
from .utils import generate_default_password

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Connexion réussie.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Nom d'utilisateur ou mot de passe invalide.")
        return super().form_invalid(form)

    def get_success_url(self):
        user = self.request.user

        if user.must_change_password:
            return '/accounts/change-password/'

        if user.role == user.Role.SUPERADMIN:
            return '/dashboard/superadmin/'

        if user.role == user.Role.ADMIN:
            return '/dashboard/admin/'

        return '/dashboard/operator/'


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')


class UserListView(AdminUserManagementAccessMixin, View):
    template_name = 'accounts/user_list.html'
    paginate_by = 10

    def get_visible_users_queryset(self, request):
        users = User.objects.all().order_by('username')

        if request.user.role == User.Role.ADMIN:
            users = users.exclude(role=User.Role.SUPERADMIN)

        return users

    def get(self, request):
        form = UserSearchForm(request.GET or None, current_user=request.user)
        users = self.get_visible_users_queryset(request)

        query = ''
        selected_role = ''

        if form.is_valid():
            query = form.cleaned_data.get('q', '').strip()
            selected_role = form.cleaned_data.get('role', '').strip()

            if query:
                users = users.filter(
                    Q(username__icontains=query) |
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(email__icontains=query)
                )

            if selected_role:
                users = users.filter(role=selected_role)

        paginator = Paginator(users, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'form': form,
            'page_obj': page_obj,
            'users': page_obj.object_list,
            'is_paginated': page_obj.has_other_pages(),
            'query': query,
            'selected_role': selected_role,
        })

class UserCreateView(AdminUserManagementAccessMixin, View):
    template_name = 'accounts/user_create.html'

    def get_form_class(self, user):
        if user_is_superadmin(user):
            return SuperAdminUserCreateForm
        return AdminUserCreateForm

    def get(self, request):
        form_class = self.get_form_class(request.user)
        form = form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form_class = self.get_form_class(request.user)
        form = form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            if not user_is_superadmin(request.user):
                user.role = User.Role.OPERATOR

            generated_password = generate_default_password()
            user.set_password(generated_password)
            user.generated_password = generated_password
            user.must_change_password = True
            user.password_was_changed = False
            user.save()

            messages.success(
                request,
                f"Utilisateur créé avec succès. Mot de passe par défaut : {generated_password}"
            )
            return redirect('user_list')

        return render(request, self.template_name, {'form': form})


class UserUpdateView(AdminUserManagementAccessMixin, TargetUserAccessMixin, View):
    template_name = 'accounts/user_update.html'

    def get_form_class(self, user):
        if user_is_superadmin(user):
            return SuperAdminUserUpdateForm
        return AdminUserUpdateForm

    def get(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de modifier ce compte.")

        form_class = self.get_form_class(request.user)
        form = form_class(instance=user_obj)

        return render(request, self.template_name, {
            'form': form,
            'user_obj': user_obj,
        })

    def post(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de modifier ce compte.")

        form_class = self.get_form_class(request.user)
        form = form_class(request.POST, instance=user_obj)

        if form.is_valid():
            user = form.save(commit=False)

            if not user_is_superadmin(request.user):
                user.role = user_obj.role

            user.save()
            messages.success(request, "Utilisateur mis à jour avec succès.")
            return redirect('user_list')

        return render(request, self.template_name, {
            'form': form,
            'user_obj': user_obj,
        })


class UserDeleteView(AdminUserManagementAccessMixin, TargetUserAccessMixin, View):
    template_name = 'accounts/user_confirm_delete.html'

    def get(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de supprimer ce compte.")

        return render(request, self.template_name, {'user_obj': user_obj})

    def post(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de supprimer ce compte.")

        if user_obj == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect('user_list')

        user_obj.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
        return redirect('user_list')


class UserBanView(AdminUserManagementAccessMixin, TargetUserAccessMixin, View):
    template_name = 'accounts/user_ban_confirm.html'

    def get(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de bannir ce compte.")

        return render(request, self.template_name, {'user_obj': user_obj})

    def post(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de bannir ce compte.")

        if user_obj == request.user:
            messages.error(request, "Vous ne pouvez pas bannir votre propre compte.")
            return redirect('user_list')

        user_obj.ban()
        messages.success(request, "Utilisateur banni avec succès.")
        return redirect('user_list')


class UserReactivateView(AdminUserManagementAccessMixin, TargetUserAccessMixin, View):
    template_name = 'accounts/user_reactivate_confirm.html'

    def get(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de réactiver ce compte.")

        return render(request, self.template_name, {'user_obj': user_obj})

    def post(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de réactiver ce compte.")

        user_obj.reactivate()
        messages.success(request, "Utilisateur réactivé avec succès.")
        return redirect('user_list')


class UserResetPasswordView(AdminUserManagementAccessMixin, TargetUserAccessMixin, View):
    template_name = 'accounts/reset_password_confirm.html'

    def get(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de réinitialiser ce mot de passe.")

        return render(request, self.template_name, {'user_obj': user_obj})

    def post(self, request, pk):
        user_obj = self.get_target_user(request, pk)
        if user_obj is None:
            return self.handle_forbidden_target(request, "Vous n'avez pas le droit de réinitialiser ce mot de passe.")

        if user_obj == request.user:
            messages.error(request, "Vous ne pouvez pas réinitialiser votre propre mot de passe depuis cette interface.")
            return redirect('user_list')

        new_password = generate_default_password()
        user_obj.set_password(new_password)
        user_obj.generated_password = new_password
        user_obj.must_change_password = True
        user_obj.password_was_changed = False
        user_obj.save()

        messages.success(
            request,
            f"Mot de passe réinitialisé avec succès. Nouveau mot de passe : {new_password}"
        )
        return redirect('user_list')


class ChangeOwnPasswordView(View):
    template_name = 'accounts/change_password.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.generated_password = ''
            user.must_change_password = False
            user.password_was_changed = True
            user.save()

            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été modifié avec succès.")
            return redirect('home')

        return render(request, self.template_name, {'form': form})

def secure_admin_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != User.Role.SUPERADMIN:
        raise PermissionDenied("Accès réservé au super administrateur.")

    return HttpResponseRedirect('/secure-admin/')