import re
import unicodedata


def normalize_text(value):
    """
    Normalise un texte pour faciliter les comparaisons :
    - convertit en chaîne,
    - supprime les accents,
    - met en majuscules,
    - retire les espaces multiples.
    """
    if not value:
        return ''

    value = str(value).strip()
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = value.upper()
    value = re.sub(r'\s+', ' ', value)
    return value.strip()


def normalize_digits(value):
    """
    Conserve uniquement les chiffres d'une chaîne.
    Utile pour téléphone, numéro sécu, etc.
    """
    if not value:
        return ''
    return re.sub(r'\D', '', str(value))


def normalize_contact(value):
    """
    Normalise le contact en ne gardant que les chiffres.
    """
    return normalize_digits(value)


def normalize_num_secu(value):
    """
    Normalise le numéro de sécurité sociale en ne gardant que les chiffres.
    """
    return normalize_digits(value)