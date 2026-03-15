import csv
from io import BytesIO

from django.http import HttpResponse
from openpyxl import Workbook


EXPORT_HEADERS = [
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


def client_to_row(client):
    return [
        client.numero or '',
        client.noms or '',
        client.prenoms or '',
        client.date_naissance.strftime('%d/%m/%Y') if client.date_naissance else '',
        client.num_secu or '',
        client.lieu_naissance or '',
        client.contact or '',
        client.lieu_enrolement or '',
        client.rangement or '',
        client.statut or '',
        client.date_delivrance.strftime('%d/%m/%Y') if client.date_delivrance else '',
    ]


def export_clients_to_csv(queryset, filename='clients_export.csv'):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(EXPORT_HEADERS)

    for client in queryset:
        writer.writerow(client_to_row(client))

    return response


def export_clients_to_excel(queryset, filename='clients_export.xlsx'):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Clients CMU'

    worksheet.append(EXPORT_HEADERS)

    for client in queryset:
        worksheet.append(client_to_row(client))

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response