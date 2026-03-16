from django.http import HttpResponseForbidden
from django.views import View
from django.views.generic import DetailView, ListView

from apps.accounts.mixins import AuthenticatedNotBannedMixin
from apps.accounts.permissions import user_is_admin_or_superadmin

from .exports import export_clients_to_csv, export_clients_to_excel
from .forms import ClientSearchForm
from .models import Client


def get_filtered_clients(request):
    queryset = Client.objects.all().order_by('noms', 'prenoms','contact')
    form = ClientSearchForm(request.GET or None)

    noms = ''
    prenoms = ''
    contact = ''
    date_naissance = None

    if form.is_valid():
        noms = form.cleaned_data.get('noms')
        prenoms = form.cleaned_data.get('prenoms')
        contact = form.cleaned_data.get('contact')
        date_naissance = form.cleaned_data.get('date_naissance')

        if noms:
            queryset = queryset.filter(noms__icontains=noms)

        if prenoms:
            queryset = queryset.filter(prenoms__icontains=prenoms)

        if contact:
            queryset = queryset.filter(contact__icontains=contact)

        if date_naissance:
            queryset = queryset.filter(date_naissance=date_naissance)

    has_name_input = bool(noms or prenoms or contact)
    return queryset, form, has_name_input


class ClientSearchView(AuthenticatedNotBannedMixin, ListView):
    model = Client
    template_name = 'clients/search.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        queryset, form, has_name_input = get_filtered_clients(self.request)
        self.form = form
        self.filtered_queryset = queryset
        self.has_name_input = has_name_input
        return queryset

    def get_template_names(self):
        if self.request.headers.get('HX-Request') == 'true':
            return ['clients/partials/search_results.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_results = self.filtered_queryset.count()

        context['form'] = self.form
        context['total_results'] = total_results
        context['has_name_input'] = self.has_name_input
        context['show_advanced_filters'] = self.has_name_input and total_results > 5
        context['can_export'] = user_is_admin_or_superadmin(self.request.user)

        querydict = self.request.GET.copy()
        if 'page' in querydict:
            querydict.pop('page')
        context['query_string'] = querydict.urlencode()

        return context


class ClientDetailView(AuthenticatedNotBannedMixin, DetailView):
    model = Client
    template_name = 'clients/detail.html'
    context_object_name = 'client'


class ExportClientsCSVView(AuthenticatedNotBannedMixin, View):
    def get(self, request, *args, **kwargs):
        if not user_is_admin_or_superadmin(request.user):
            return HttpResponseForbidden("Accès non autorisé.")

        queryset, _, _ = get_filtered_clients(request)
        return export_clients_to_csv(queryset, filename='clients_cmu_export.csv')


class ExportClientsExcelView(AuthenticatedNotBannedMixin, View):
    def get(self, request, *args, **kwargs):
        if not user_is_admin_or_superadmin(request.user):
            return HttpResponseForbidden("Accès non autorisé.")

        queryset, _, _ = get_filtered_clients(request)
        return export_clients_to_excel(queryset, filename='clients_cmu_export.xlsx')