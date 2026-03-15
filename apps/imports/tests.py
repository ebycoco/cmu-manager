import pandas as pd
from django.test import TestCase

from apps.clients.models import Client
from apps.imports.models import ImportDuplicate
from apps.imports.services import detect_duplicate, parse_date, validate_columns


class ImportServicesTests(TestCase):
    def test_validate_columns_success(self):
        dataframe = pd.DataFrame(columns=[
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
        ])
        missing = validate_columns(dataframe)
        self.assertEqual(missing, [])

    def test_validate_columns_missing(self):
        dataframe = pd.DataFrame(columns=['NOMS', 'PRENOMS'])
        missing = validate_columns(dataframe)
        self.assertIn('NUM SECU', missing)
        self.assertIn('RANGEMENT', missing)

    def test_parse_date_french_format(self):
        date_value = parse_date('1-janv.-2000')
        self.assertIsNotNone(date_value)
        self.assertEqual(date_value.year, 2000)

    def test_detect_duplicate_by_num_secu(self):
        Client.objects.create(
            noms='KOUASSI',
            prenoms='Jean',
            num_secu='12345678',
            rangement='A-01'
        )

        client_data = {
            'noms': 'KOUASSI',
            'prenoms': 'Jean',
            'num_secu': '12345678',
            'date_naissance': None,
            'contact': '',
            'lieu_naissance': '',
        }

        matched_client, match_type = detect_duplicate(client_data)

        self.assertIsNotNone(matched_client)
        self.assertEqual(match_type, ImportDuplicate.MatchType.NUM_SECU)

    def test_detect_duplicate_by_identity_with_birth_place(self):
        Client.objects.create(
            noms='KONE',
            prenoms='Awa',
            date_naissance='1998-02-10',
            lieu_naissance='Bouaké',
            rangement='B-02'
        )

        client_data = {
            'noms': 'KONE',
            'prenoms': 'Awa',
            'num_secu': '',
            'date_naissance': parse_date('10/02/1998'),
            'contact': '',
            'lieu_naissance': 'Bouaké',
        }

        matched_client, match_type = detect_duplicate(client_data)

        self.assertIsNotNone(matched_client)
        self.assertEqual(match_type, ImportDuplicate.MatchType.IDENTITY)