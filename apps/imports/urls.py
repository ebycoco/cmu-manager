from django.urls import path

from .views import (
    ImportBatchDeleteView,
    ImportHistoryView,
    ImportReviewView,
    ImportUploadView,
    TruncateDataView,
)

urlpatterns = [
    path('', ImportHistoryView.as_view(), name='import_history'),
    path('upload/', ImportUploadView.as_view(), name='import_upload'),
    path('review/<int:batch_id>/', ImportReviewView.as_view(), name='import_review'),
    path('delete/<int:pk>/', ImportBatchDeleteView.as_view(), name='import_delete'),
    path('truncate/', TruncateDataView.as_view(), name='truncate_data'),
]