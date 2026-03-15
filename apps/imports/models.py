from django.conf import settings
from django.db import models


class ImportBatch(models.Model):
    class FileType(models.TextChoices):
        CSV = 'CSV', 'CSV'
        XLSX = 'XLSX', 'Excel (.xlsx)'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        ANALYZED = 'ANALYZED', 'Analysé'
        CONFIRMED = 'CONFIRMED', 'Confirmé'
        COMPLETED = 'COMPLETED', 'Terminé'
        FAILED = 'FAILED', 'Échoué'

    file_name = models.CharField(
        max_length=255,
        verbose_name="Nom du fichier"
    )
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        verbose_name="Type de fichier"
    )
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_batches',
        verbose_name="Importé par"
    )
    imported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Importé le"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )

    total_rows = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre total de lignes"
    )
    new_rows = models.PositiveIntegerField(
        default=0,
        verbose_name="Nouvelles lignes"
    )
    duplicate_rows = models.PositiveIntegerField(
        default=0,
        verbose_name="Lignes en doublon"
    )
    updated_rows = models.PositiveIntegerField(
        default=0,
        verbose_name="Lignes mises à jour"
    )
    skipped_rows = models.PositiveIntegerField(
        default=0,
        verbose_name="Lignes ignorées"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )

    class Meta:
        verbose_name = "Lot d'import"
        verbose_name_plural = "Lots d'import"
        ordering = ['-imported_at']

    def __str__(self):
        return f"{self.file_name} - {self.imported_at:%d/%m/%Y %H:%M}"


class ImportDuplicate(models.Model):
    class MatchType(models.TextChoices):
        NUM_SECU = 'NUM_SECU', 'Correspondance par numéro sécu'
        IDENTITY = 'IDENTITY', 'Correspondance par identité'
        PARTIAL = 'PARTIAL', 'Correspondance partielle'

    class DecisionStatus(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        KEEP_EXISTING = 'KEEP_EXISTING', 'Garder l’existant'
        UPDATE_EXISTING = 'UPDATE_EXISTING', 'Mettre à jour l’existant'
        SKIP = 'SKIP', 'Ignorer'

    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.CASCADE,
        related_name='duplicates',
        verbose_name="Lot d'import"
    )
    row_index = models.PositiveIntegerField(
        verbose_name="Ligne du fichier"
    )
    incoming_data = models.JSONField(
        verbose_name="Données entrantes"
    )
    matched_client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_duplicates',
        verbose_name="Client correspondant"
    )
    match_type = models.CharField(
        max_length=20,
        choices=MatchType.choices,
        verbose_name="Type de correspondance"
    )
    decision_status = models.CharField(
        max_length=20,
        choices=DecisionStatus.choices,
        default=DecisionStatus.PENDING,
        verbose_name="Décision"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )

    class Meta:
        verbose_name = "Doublon détecté"
        verbose_name_plural = "Doublons détectés"
        ordering = ['row_index']
        unique_together = ('import_batch', 'row_index')

    def __str__(self):
        return f"Doublon ligne {self.row_index} - {self.import_batch.file_name}"