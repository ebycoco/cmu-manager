from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.accounts.admin import UserAdmin
from apps.accounts.models import User
from apps.accounts.views import secure_admin_redirect_view
from apps.clients.admin import ClientAdmin
from apps.clients.models import Client
from apps.common.admin_site import CMUAdminSite
from apps.imports.admin import ImportBatchAdmin, ImportDuplicateAdmin
from apps.imports.models import ImportBatch, ImportDuplicate
from config.views import (
    custom_bad_request_view,
    custom_page_not_found_view,
    custom_permission_denied_view,
    custom_server_error_view,
)

custom_admin_site = CMUAdminSite(name='cmu_admin')
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Client, ClientAdmin)
custom_admin_site.register(ImportBatch, ImportBatchAdmin)
custom_admin_site.register(ImportDuplicate, ImportDuplicateAdmin)

urlpatterns = [
    path('admin/', secure_admin_redirect_view, name='secure_admin_entry'),
    path('secure-admin/', custom_admin_site.urls),

    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('clients/', include('apps.clients.urls')),
    path('imports/', include('apps.imports.urls')),
]

handler400 = 'config.views.custom_bad_request_view'
handler403 = 'config.views.custom_permission_denied_view'
handler404 = 'config.views.custom_page_not_found_view'
handler500 = 'config.views.custom_server_error_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)