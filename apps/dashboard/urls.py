from django.urls import path

from .views import (
    AdminDashboardView,
    OperatorDashboardView,
    SuperAdminDashboardView,
    home_view,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/superadmin/', SuperAdminDashboardView.as_view(), name='dashboard_superadmin'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard_admin'),
    path('dashboard/operator/', OperatorDashboardView.as_view(), name='dashboard_operator'),
]