from django import forms
from django.contrib.auth.models import User

from .models import Ticket


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            'company',
            'title',
            'description',
            'priority',
            'status',
            'assigned_to',
            'due_date',
        ]

        widgets = {

            'company': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter ticket title'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'placeholder': (
                        'Describe the issue or request...'
                    )
                }
            ),

            'priority': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'status': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'assigned_to': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'due_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
        }