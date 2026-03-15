from django.contrib import admin
from django.utils.html import format_html

from .models import ImportBatch, ImportDuplicate


class ImportDuplicateInline(admin.TabularInline):
    model = ImportDuplicate
    extra = 0
    readonly_fields = (
        'row_index',
        'matched_client',
        'match_type',
        'decision_status',
        'created_at',
    )
    fields = (
        'row_index',
        'matched_client',
        'match_type',
        'decision_status',
        'created_at',
    )
    can_delete = False
    show_change_link = True


class ImportBatchAdmin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'file_type',
        'imported_by',
        'colored_status',
        'total_rows',
        'new_rows',
        'duplicate_rows',
        'updated_rows',
        'skipped_rows',
        'imported_at',
    )
    list_filter = ('file_type', 'status', 'imported_at')
    search_fields = ('file_name', 'notes', 'imported_by__username')
    ordering = ('-imported_at',)
    readonly_fields = ('imported_at',)
    inlines = [ImportDuplicateInline]

    def colored_status(self, obj):
        colors = {
            'PENDING': '#6c757d',
            'ANALYZED': '#0d6efd',
            'CONFIRMED': '#6f42c1',
            'COMPLETED': '#198754',
            'FAILED': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')

        return format_html(
            '<span style="background:{};color:white;padding:4px 10px;border-radius:999px;">{}</span>',
            color,
            obj.get_status_display()
        )
    colored_status.short_description = "Statut"


class ImportDuplicateAdmin(admin.ModelAdmin):
    list_display = (
        'import_batch',
        'row_index',
        'matched_client',
        'match_type',
        'decision_status',
        'created_at',
    )
    list_filter = ('match_type', 'decision_status', 'created_at')
    search_fields = (
        'import_batch__file_name',
        'matched_client__noms',
        'matched_client__prenoms',
    )
    ordering = ('import_batch', 'row_index')
    readonly_fields = ('created_at',)