from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', 'Super administrateur'
        ADMIN = 'ADMIN', 'Administrateur'
        OPERATOR = 'OPERATOR', 'Opérateur'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OPERATOR,
        verbose_name="Rôle"
    )
    is_banned = models.BooleanField(
        default=False,
        verbose_name="Compte banni"
    )
    generated_password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Mot de passe généré"
    )
    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Doit changer le mot de passe"
    )
    password_was_changed = models.BooleanField(
        default=False,
        verbose_name="Mot de passe modifié"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    objects = UserManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    @property
    def role_badge_class(self):
        if self.role == self.Role.SUPERADMIN:
            return 'role-superadmin'
        if self.role == self.Role.ADMIN:
            return 'role-admin'
        return 'role-operator'

    @property
    def role_display_label(self):
        if self.role == self.Role.SUPERADMIN:
            return 'Super Admin'
        if self.role == self.Role.ADMIN:
            return 'Admin'
        return 'Opérateur'

    def ban(self):
        self.is_banned = True
        self.save(update_fields=['is_banned', 'updated_at'])

    def reactivate(self):
        self.is_banned = False
        self.save(update_fields=['is_banned', 'updated_at'])