from django.contrib.admin import AdminSite


class CMUAdminSite(AdminSite):
    site_header = "Administration CMU Manager"
    site_title = "CMU Manager Admin"
    index_title = "Tableau de bord administration"

    def has_permission(self, request):
        user = request.user
        return (
            user.is_active
            and user.is_authenticated
            and getattr(user, 'role', None) == 'SUPERADMIN'
        )