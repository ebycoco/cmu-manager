from django.db import models

from apps.common.utils import normalize_contact, normalize_num_secu, normalize_text


class Client(models.Model):
    numero = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="N°"
    )
    noms = models.CharField(
        max_length=150,
        verbose_name="NOMS"
    )
    prenoms = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="PRENOMS"
    )
    date_naissance = models.DateField(
        blank=True,
        null=True,
        verbose_name="DATE DE NAISSANCE"
    )
    num_secu = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="NUM SECU"
    )
    lieu_naissance = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="LIEU DE NAISSANCE"
    )
    contact = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="CONTACT"
    )
    lieu_enrolement = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="LIEU D'ENROLEMENT"
    )
    rangement = models.CharField(
        max_length=100,
        verbose_name="RANGEMENT"
    )
    statut = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="STATUT"
    )
    date_delivrance = models.DateField(
        blank=True,
        null=True,
        verbose_name="DATE DE DELIVRANCE"
    )

    noms_normalized = models.CharField(
        max_length=150,
        editable=False,
        db_index=True
    )
    prenoms_normalized = models.CharField(
        max_length=150,
        blank=True,
        default='',
        editable=False,
        db_index=True
    )
    num_secu_normalized = models.CharField(
        max_length=100,
        blank=True,
        default='',
        editable=False,
        db_index=True
    )
    contact_normalized = models.CharField(
        max_length=50,
        blank=True,
        default='',
        editable=False,
        db_index=True
    )

    source_file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Fichier source"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    class Meta:
        verbose_name = "Client CMU"
        verbose_name_plural = "Clients CMU"
        ordering = ['noms', 'prenoms']
        indexes = [
            models.Index(fields=['noms']),
            models.Index(fields=['prenoms']),
            models.Index(fields=['date_naissance']),
            models.Index(fields=['rangement']),
            models.Index(fields=['statut']),
            models.Index(fields=['lieu_enrolement']),
            models.Index(fields=['noms_normalized', 'prenoms_normalized']),
            models.Index(fields=['num_secu_normalized']),
        ]

    def __str__(self):
        prenoms = self.prenoms or ''
        return f"{self.noms} {prenoms}".strip()

    def save(self, *args, **kwargs):
        self.noms_normalized = normalize_text(self.noms)
        self.prenoms_normalized = normalize_text(self.prenoms)
        self.num_secu_normalized = normalize_num_secu(self.num_secu)
        self.contact_normalized = normalize_contact(self.contact)
        super().save(*args, **kwargs)