from django import forms


class ClientSearchForm(forms.Form):
    noms = forms.CharField(
        required=False,
        label="NOMS",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: KOUASSI',
            'autocomplete': 'off',
        })
    )
    prenoms = forms.CharField(
        required=False,
        label="PRENOMS",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Jean',
            'autocomplete': 'off',
        })
    )
    date_naissance = forms.DateField(
        required=False,
        label="DATE DE NAISSANCE",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )