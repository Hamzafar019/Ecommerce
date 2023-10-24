from django import forms

class DisplayCalculationForm(forms.Form):
    show_calculations = forms.BooleanField(
        required=False,
        initial=False,  # Initially, checkbox is unchecked
        label='Show Calculations',
    )
