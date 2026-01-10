from django import forms
from .models import *


class FeesForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = [
            'fee_type',
            'amount',
            'scope',
            'Programs',
            'year_of_study',
        ]

        widgets = {
            'fee_type': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),
            'scope': forms.Select(
                attrs={
                    'class': 'form-control', 'id':'id_scope'
                }
            ),
            'Programs': forms.Select(
                attrs={
                    'class': 'form-control', 'id':'id_Programs'
                }
            ),
            'year_of_study': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def clean(self):
        """
        Custom validation to enforce business rules:
        - If scope = ALL → Programs must be empty
        - If scope = Programs → Programs is required
        """
        cleaned_data = super().clean()
        scope = cleaned_data.get('scope')
        program = cleaned_data.get('Programs')

        if scope == Fee.Scope.ALL and program:
            self.add_error(
                'Programs',
                'Program must be empty when fee applies to all students.'
            )

        if scope == Fee.Scope.Programs and not program:
            self.add_error(
                'Programs',
                'Program is required when scope is Programs-specific.'
            )

        return cleaned_data

class InvoiceForm(forms.ModelForm):

    account = forms.ModelChoiceField(
        queryset=StudentAccount.objects.all(),
        error_messages={
            'required': 'Please select a student account.',
            'invalid_choice': 'Student account does not exist.'
        },
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'id_account'
            }
        )
    )

    fee = forms.ModelChoiceField(
        queryset=Fee.objects.all(),
        error_messages={
            'required': 'Please select a fee.'
        },
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'id': 'id_fee'
            }
        )
    )

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        error_messages={
            'required': 'Amount is required.'
        },
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'id': 'id_amount'
            }
        )
    )

    class Meta:
        model = Invoice
        fields = ['account', 'fee', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fee'].label_from_instance = (
            lambda fee: f'{fee.fee_type} - K{fee.amount}'
        )


