from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from apps.accounts.mixins import (
    AdminOrSuperAdminRequiredMixin,
    OperatorRequiredMixin,
    SuperAdminRequiredMixin,
)


def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_banned:
            raise PermissionDenied("Votre compte est banni.")
        if request.user.role == request.user.Role.SUPERADMIN:
            return redirect('dashboard_superadmin')
        if request.user.role == request.user.Role.ADMIN:
            return redirect('dashboard_admin')
        return redirect('dashboard_operator')

    return render(request, 'home.html')


class SuperAdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'dashboard/superadmin_dashboard.html'


class AdminDashboardView(AdminOrSuperAdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'


class OperatorDashboardView(OperatorRequiredMixin, TemplateView):
    template_name = 'dashboard/operator_dashboard.html'