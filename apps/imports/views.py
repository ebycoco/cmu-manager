from django.contrib import messages
from django.db import connection, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DeleteView, ListView

from apps.accounts.mixins import AdminOrSuperAdminRequiredMixin
from apps.clients.models import Client

from .forms import ImportUploadForm
from .models import ImportBatch, ImportDuplicate
from .services import (
    apply_update_to_client,
    detect_duplicate,
    parse_date,
    read_uploaded_file,
    row_to_client_data,
    serialize_incoming_data,
    validate_columns,
)


class ImportHistoryView(AdminOrSuperAdminRequiredMixin, ListView):
    model = ImportBatch
    template_name = 'imports/history.html'
    context_object_name = 'batches'
    paginate_by = 10
    ordering = ['-imported_at']


class ImportUploadView(AdminOrSuperAdminRequiredMixin, View):
    template_name = 'imports/upload.html'

    def get(self, request):
        form = ImportUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ImportUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, "Veuillez sélectionner un fichier valide.")
            return render(request, self.template_name, {'form': form})

        uploaded_file = form.cleaned_data['file']

        try:
            dataframe, file_type = read_uploaded_file(uploaded_file)
        except ValueError as error:
            messages.error(request, str(error))
            return render(request, self.template_name, {'form': form})
        except Exception as error:
            messages.error(request, f"Erreur lors de la lecture du fichier : {error}")
            return render(request, self.template_name, {'form': form})

        missing_columns = validate_columns(dataframe)
        if missing_columns:
            messages.error(
                request,
                "Colonnes manquantes dans le fichier : " + ", ".join(missing_columns)
            )
            return render(request, self.template_name, {'form': form})

        batch = ImportBatch.objects.create(
            file_name=uploaded_file.name,
            file_type=file_type,
            imported_by=request.user,
            status=ImportBatch.Status.ANALYZED,
            total_rows=len(dataframe),
        )

        new_rows_data = []
        duplicate_count = 0
        new_count = 0
        skipped_count = 0

        for index, row in dataframe.iterrows():
            client_data = row_to_client_data(row, source_file_name=uploaded_file.name)

            if not client_data.get('noms') or not client_data.get('rangement'):
                skipped_count += 1
                continue

            matched_client, match_type = detect_duplicate(client_data)

            if matched_client:
                ImportDuplicate.objects.create(
                    import_batch=batch,
                    row_index=index + 2,
                    incoming_data=serialize_incoming_data(client_data),
                    matched_client=matched_client,
                    match_type=match_type,
                )
                duplicate_count += 1
            else:
                new_rows_data.append(serialize_incoming_data(client_data))
                new_count += 1

        batch.new_rows = new_count
        batch.duplicate_rows = duplicate_count
        batch.skipped_rows = skipped_count
        batch.status = ImportBatch.Status.ANALYZED
        batch.save()

        request.session[f'import_batch_{batch.id}_new_rows'] = new_rows_data

        messages.info(
            request,
            (
                f"Analyse terminée : {new_count} nouvelle(s) ligne(s), "
                f"{duplicate_count} doublon(s), {skipped_count} ligne(s) ignorée(s)."
            )
        )
        return redirect('import_review', batch_id=batch.id)


class ImportReviewView(AdminOrSuperAdminRequiredMixin, View):
    template_name = 'imports/review.html'

    def get(self, request, batch_id):
        batch = get_object_or_404(ImportBatch, pk=batch_id)
        duplicates = batch.duplicates.select_related('matched_client').all()

        return render(request, self.template_name, {
            'batch': batch,
            'duplicates': duplicates,
        })

    def post(self, request, batch_id):
        batch = get_object_or_404(ImportBatch, pk=batch_id)
        duplicates = batch.duplicates.select_related('matched_client').all()
        new_rows_data = request.session.get(f'import_batch_{batch.id}_new_rows', [])

        created_count = 0
        updated_count = 0
        skipped_count = batch.skipped_rows

        for duplicate in duplicates:
            decision = request.POST.get(
                f'decision_{duplicate.id}',
                ImportDuplicate.DecisionStatus.KEEP_EXISTING
            )

            if decision not in [
                ImportDuplicate.DecisionStatus.KEEP_EXISTING,
                ImportDuplicate.DecisionStatus.UPDATE_EXISTING,
                ImportDuplicate.DecisionStatus.SKIP,
            ]:
                decision = ImportDuplicate.DecisionStatus.KEEP_EXISTING

            duplicate.decision_status = decision
            duplicate.save(update_fields=['decision_status'])

            incoming_data = duplicate.incoming_data.copy()

            if incoming_data.get('date_naissance'):
                incoming_data['date_naissance'] = parse_date(incoming_data['date_naissance'])

            if incoming_data.get('date_delivrance'):
                incoming_data['date_delivrance'] = parse_date(incoming_data['date_delivrance'])

            if (
                decision == ImportDuplicate.DecisionStatus.UPDATE_EXISTING
                and duplicate.matched_client
            ):
                apply_update_to_client(duplicate.matched_client, incoming_data)
                updated_count += 1
            elif decision in [
                ImportDuplicate.DecisionStatus.KEEP_EXISTING,
                ImportDuplicate.DecisionStatus.SKIP,
            ]:
                skipped_count += 1

        for row_data in new_rows_data:
            row_data = row_data.copy()

            if row_data.get('date_naissance'):
                row_data['date_naissance'] = parse_date(row_data['date_naissance'])

            if row_data.get('date_delivrance'):
                row_data['date_delivrance'] = parse_date(row_data['date_delivrance'])

            Client.objects.create(**row_data)
            created_count += 1

        batch.updated_rows = updated_count
        batch.skipped_rows = skipped_count
        batch.status = ImportBatch.Status.COMPLETED
        batch.save()

        session_key = f'import_batch_{batch.id}_new_rows'
        if session_key in request.session:
            del request.session[session_key]

        messages.success(
            request,
            (
                f"Import terminé : {created_count} création(s), "
                f"{updated_count} mise(s) à jour, {skipped_count} ignorée(s)."
            )
        )
        return redirect('import_history')


class ImportBatchDeleteView(AdminOrSuperAdminRequiredMixin, View):
    template_name = 'imports/confirm_delete_history.html'

    def get(self, request, pk):
        batch = get_object_or_404(ImportBatch, pk=pk)
        return render(request, self.template_name, {'batch': batch})

    def post(self, request, pk):
        batch = get_object_or_404(ImportBatch, pk=pk)
        file_name = batch.file_name
        batch.delete()

        messages.success(
            request,
            f"L'historique de l'import '{file_name}' a été supprimé. Les données clients restent conservées."
        )
        return redirect('import_history')


class TruncateDataView(AdminOrSuperAdminRequiredMixin, View):
    template_name = 'imports/confirm_truncate.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        confirm_text = request.POST.get('confirm_text', '').strip().upper()

        if confirm_text != 'CONFIRMER':
            messages.error(
                request,
                "Confirmation invalide. Tapez exactement CONFIRMER pour vider les données."
            )
            return render(request, self.template_name)

        try:
            with transaction.atomic():
                ImportDuplicate.objects.all().delete()
                ImportBatch.objects.all().delete()
                Client.objects.all().delete()

                if connection.vendor == 'sqlite':
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'clients_client';")
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'imports_importbatch';")
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'imports_importduplicate';")

            messages.success(
                request,
                "Toutes les données métier ont été supprimées avec succès."
            )
            return redirect('import_history')

        except Exception as error:
            messages.error(
                request,
                f"Une erreur est survenue lors de la suppression des données : {error}"
            )
            return render(request, self.template_name)