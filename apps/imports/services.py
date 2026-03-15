import re
from datetime import datetime

import pandas as pd
from django.db.models import Q

from apps.clients.models import Client
from apps.common.utils import normalize_contact, normalize_num_secu, normalize_text

from .models import ImportBatch, ImportDuplicate


EXPECTED_COLUMNS = [
    'N°',
    'NOMS',
    'PRENOMS',
    'DATE DE NAISSANCE',
    'NUM SECU',
    'LIEU DE NAISSANCE',
    'CONTACT',
    "LIEU D'ENROLEMENT",
    'RANGEMENT',
    'STATUT',
    'DATE DE DELIVRANCE',
]


FRENCH_MONTHS = {
    'janv': '01',
    'janvier': '01',
    'fevr': '02',
    'fevrier': '02',
    'févr': '02',
    'février': '02',
    'mars': '03',
    'avr': '04',
    'avril': '04',
    'mai': '05',
    'juin': '06',
    'juil': '07',
    'juillet': '07',
    'aout': '08',
    'août': '08',
    'sept': '09',
    'septembre': '09',
    'oct': '10',
    'octobre': '10',
    'nov': '11',
    'novembre': '11',
    'dec': '12',
    'decembre': '12',
    'déc': '12',
    'décembre': '12',
}


def read_uploaded_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith('.csv'):
        dataframe = pd.read_csv(uploaded_file)
        file_type = ImportBatch.FileType.CSV
    elif file_name.endswith('.xlsx'):
        dataframe = pd.read_excel(uploaded_file, engine='openpyxl')
        file_type = ImportBatch.FileType.XLSX
    else:
        raise ValueError("Format de fichier non supporté. Utilisez CSV ou XLSX.")

    dataframe.columns = [str(col).strip() for col in dataframe.columns]
    return dataframe, file_type


def validate_columns(dataframe):
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in dataframe.columns]
    return missing_columns


def normalize_french_date_string(value):
    """
    Convertit des dates françaises texte en format exploitable.
    Exemples :
    - 01-sept.2000 -> 01-09-2000
    - 1-janv.-2000 -> 1-01-2000
    - 01 sept 2000 -> 01-09-2000
    """
    value = str(value).strip().lower()

    value = value.replace('.', ' ')
    value = value.replace('/', '-')
    value = re.sub(r'\s+', ' ', value).strip()

    for french_month, month_number in FRENCH_MONTHS.items():
        pattern = r'\b' + re.escape(french_month) + r'\b'
        value = re.sub(pattern, month_number, value)

    value = value.replace(' - ', '-')
    value = value.replace(' ', '-')
    value = re.sub(r'-+', '-', value)

    return value.strip('-')


def parse_date(value):
    """
    Essaie de convertir différentes représentations de dates vers un objet date.
    Gère :
    - dates Excel / pandas
    - formats numériques classiques français
    - mois en français
    """
    if pd.isna(value) or value in [None, '']:
        return None

    if isinstance(value, datetime):
        return value.date()

    if hasattr(value, 'date'):
        try:
            return value.date()
        except Exception:
            pass

    raw_value = str(value).strip()
    normalized_value = normalize_french_date_string(raw_value)

    explicit_formats = [
        '%d-%m-%Y',
        '%d-%m-%y',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%d/%m/%y',
        '%d.%m.%Y',
        '%d.%m.%y',
        '%d %m %Y',
        '%d %m %y',
    ]

    for fmt in explicit_formats:
        try:
            return datetime.strptime(raw_value, fmt).date()
        except ValueError:
            pass

        try:
            return datetime.strptime(normalized_value, fmt).date()
        except ValueError:
            pass

    try:
        parsed = pd.to_datetime(normalized_value, errors='coerce')
        if pd.notna(parsed):
            return parsed.date()
    except Exception:
        pass

    return None

def row_to_client_data(row, source_file_name=''):
    return {
        'numero': str(row.get('N°')).strip() if pd.notna(row.get('N°')) else '',
        'noms': str(row.get('NOMS')).strip() if pd.notna(row.get('NOMS')) else '',
        'prenoms': str(row.get('PRENOMS')).strip() if pd.notna(row.get('PRENOMS')) else '',
        'date_naissance': parse_date(row.get('DATE DE NAISSANCE')),
        'num_secu': str(row.get('NUM SECU')).strip() if pd.notna(row.get('NUM SECU')) else '',
        'lieu_naissance': str(row.get('LIEU DE NAISSANCE')).strip() if pd.notna(row.get('LIEU DE NAISSANCE')) else '',
        'contact': str(row.get('CONTACT')).strip() if pd.notna(row.get('CONTACT')) else '',
        'lieu_enrolement': str(row.get("LIEU D'ENROLEMENT")).strip() if pd.notna(row.get("LIEU D'ENROLEMENT")) else '',
        'rangement': str(row.get('RANGEMENT')).strip() if pd.notna(row.get('RANGEMENT')) else '',
        'statut': str(row.get('STATUT')).strip() if pd.notna(row.get('STATUT')) else '',
        'date_delivrance': parse_date(row.get('DATE DE DELIVRANCE')),
        'source_file_name': source_file_name,
    }


def serialize_incoming_data(client_data):
    serialized = client_data.copy()

    for key in ['date_naissance', 'date_delivrance']:
        if serialized.get(key):
            serialized[key] = serialized[key].isoformat()

    return serialized


def detect_duplicate(client_data):
    """
    Détection des doublons selon une stratégie progressive :
    1. Par numéro de sécurité normalisé
    2. Par identité très forte : noms + prenoms + date_naissance + lieu_naissance
    3. Par identité forte : noms + prenoms + date_naissance
    4. Par identité partielle : noms + prenoms + (contact ou date_naissance ou lieu_naissance)
    """
    num_secu_normalized = normalize_num_secu(client_data.get('num_secu'))
    noms_normalized = normalize_text(client_data.get('noms'))
    prenoms_normalized = normalize_text(client_data.get('prenoms'))
    contact_normalized = normalize_contact(client_data.get('contact'))
    lieu_naissance_normalized = normalize_text(client_data.get('lieu_naissance'))
    date_naissance = client_data.get('date_naissance')

    # 1. Doublon fort par NUM SECU
    if num_secu_normalized:
        client = Client.objects.filter(num_secu_normalized=num_secu_normalized).first()
        if client:
            return client, ImportDuplicate.MatchType.NUM_SECU

    # 2. Doublon très fort par identité complète
    if noms_normalized and prenoms_normalized and date_naissance and lieu_naissance_normalized:
        possible_clients = Client.objects.filter(
            noms_normalized=noms_normalized,
            prenoms_normalized=prenoms_normalized,
            date_naissance=date_naissance
        )

        for client in possible_clients:
            if normalize_text(client.lieu_naissance) == lieu_naissance_normalized:
                return client, ImportDuplicate.MatchType.IDENTITY

    # 3. Doublon fort par identité sans lieu de naissance
    if noms_normalized and prenoms_normalized and date_naissance:
        client = Client.objects.filter(
            noms_normalized=noms_normalized,
            prenoms_normalized=prenoms_normalized,
            date_naissance=date_naissance
        ).first()
        if client:
            return client, ImportDuplicate.MatchType.IDENTITY

    # 4. Doublon partiel : noms + prenoms + (contact ou date_naissance ou lieu_naissance)
    if noms_normalized and prenoms_normalized:
        possible_clients = Client.objects.filter(
            noms_normalized=noms_normalized,
            prenoms_normalized=prenoms_normalized
        )

        for client in possible_clients:
            same_contact = (
                contact_normalized
                and normalize_contact(client.contact) == contact_normalized
            )
            same_date = (
                date_naissance
                and client.date_naissance == date_naissance
            )
            same_lieu_naissance = (
                lieu_naissance_normalized
                and normalize_text(client.lieu_naissance) == lieu_naissance_normalized
            )

            if same_contact or same_date or same_lieu_naissance:
                return client, ImportDuplicate.MatchType.PARTIAL

    return None, None

def apply_update_to_client(client, incoming_data):
    """
    Met à jour le client existant uniquement avec les valeurs importées non vides.
    """
    for field in [
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
    ]:
        incoming_value = incoming_data.get(field)

        if incoming_value not in [None, '']:
            setattr(client, field, incoming_value)

    client.save()
    return client