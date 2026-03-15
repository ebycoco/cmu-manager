from django import forms

from .models import ImportDuplicate


class ImportUploadForm(forms.Form):
    file = forms.FileField(
        label="Fichier CSV ou Excel",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
        })
    )


class DuplicateDecisionForm(forms.Form):
    decision = forms.ChoiceField(
        choices=ImportDuplicate.DecisionStatus.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )