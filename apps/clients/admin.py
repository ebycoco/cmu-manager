from django.contrib import admin
from django.utils.html import format_html

from .models import Client


class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'noms',
        'prenoms',
        'date_naissance',
        'lieu_naissance',
        'lieu_enrolement',
        'colored_rangement',
        'statut',
        'source_file_name',
        'updated_at',
    )
    search_fields = (
        'numero',
        'noms',
        'prenoms',
        'num_secu',
        'contact',
        'lieu_naissance',
        'lieu_enrolement',
        'rangement',
    )
    list_filter = (
        'statut',
        'lieu_enrolement',
        'lieu_naissance',
        'date_naissance',
        'date_delivrance',
        'created_at',
    )
    ordering = ('noms', 'prenoms')
    readonly_fields = (
        'noms_normalized',
        'prenoms_normalized',
        'num_secu_normalized',
        'contact_normalized',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            "Informations principales",
            {
                'fields': (
                    'numero',
                    'noms',
                    'prenoms',
                    'date_naissance',
                    'num_secu',
                    'lieu_naissance',
                    'contact',
                    'lieu_enrolement',
                    'rangement',
                    'statut',
                    'date_delivrance',
                    'source_file_name',
                )
            }
        ),
        (
            "Champs techniques",
            {
                'fields': (
                    'noms_normalized',
                    'prenoms_normalized',
                    'num_secu_normalized',
                    'contact_normalized',
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )

    def colored_rangement(self, obj):
        return format_html(
            '<span style="background:#198754;color:white;padding:4px 10px;border-radius:8px;font-weight:700;">{}</span>',
            obj.rangement
        )
    colored_rangement.short_description = "Rangement"