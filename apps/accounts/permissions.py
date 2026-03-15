from django.core.exceptions import PermissionDenied


def user_is_superadmin(user):
    return user.is_authenticated and user.role == user.Role.SUPERADMIN


def user_is_admin(user):
    return user.is_authenticated and user.role == user.Role.ADMIN


def user_is_operator(user):
    return user.is_authenticated and user.role == user.Role.OPERATOR


def user_is_admin_or_superadmin(user):
    return user.is_authenticated and user.role in [
        user.Role.SUPERADMIN,
        user.Role.ADMIN,
    ]


def require_superadmin(user):
    if not user_is_superadmin(user):
        raise PermissionDenied("Accès réservé au super administrateur.")
    return True


def require_admin_or_superadmin(user):
    if not user_is_admin_or_superadmin(user):
        raise PermissionDenied("Accès réservé aux administrateurs.")
    return True