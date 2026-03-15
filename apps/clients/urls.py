from django.urls import path

from .views import (
    ClientDetailView,
    ClientSearchView,
    ExportClientsCSVView,
    ExportClientsExcelView,
)

urlpatterns = [
    path('search/', ClientSearchView.as_view(), name='client_search'),
    path('export/csv/', ExportClientsCSVView.as_view(), name='client_export_csv'),
    path('export/excel/', ExportClientsExcelView.as_view(), name='client_export_excel'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
]