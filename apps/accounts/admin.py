from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.utils.html import format_html

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        'username',
        'full_name',
        'email',
        'colored_role',
        'is_banned_badge',
        'must_change_password',
        'password_status',
        'is_active',
        'is_staff',
        'created_at',
    )
    list_filter = (
        'role',
        'is_banned',
        'must_change_password',
        'password_was_changed',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'Informations métier',
            {
                'fields': (
                    'role',
                    'is_banned',
                    'generated_password',
                    'must_change_password',
                    'password_was_changed',
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            'Informations métier',
            {
                'fields': ('first_name', 'last_name', 'email', 'role', 'is_banned')
            }
        ),
    )

    actions = ['ban_selected_users', 'reactivate_selected_users']

    def full_name(self, obj):
        full_name = f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return full_name or "-"
    full_name.short_description = "Nom complet"

    def colored_role(self, obj):
        colors = {
            'SUPERADMIN': '#dc3545',
            'ADMIN': '#0d6efd',
            'OPERATOR': '#198754',
        }
        color = colors.get(obj.role, '#6c757d')

        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:999px;font-weight:600;">{}</span>',
            color,
            obj.get_role_display()
        )
    colored_role.short_description = "Rôle"

    def is_banned_badge(self, obj):
        if obj.is_banned:
            return format_html(
                '<span style="background:{};color:white;padding:4px 10px;border-radius:999px;">{}</span>',
                '#dc3545',
                'Oui'
            )
        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:999px;">{}</span>',
            '#198754',
            'Non'
        )
    is_banned_badge.short_description = "Banni"

    def password_status(self, obj):
        if obj.password_was_changed:
            return "Modifié"
        if obj.generated_password:
            return "Généré"
        return "-"
    password_status.short_description = "État mot de passe"

    @admin.action(description="Bannir les utilisateurs sélectionnés")
    def ban_selected_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(is_banned=True)
        self.message_user(request, f"{updated} utilisateur(s) banni(s).")

    @admin.action(description="Réactiver les utilisateurs sélectionnés")
    def reactivate_selected_users(self, request, queryset):
        updated = queryset.update(is_banned=False)
        self.message_user(request, f"{updated} utilisateur(s) réactivé(s).")