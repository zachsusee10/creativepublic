from django import forms
from .models import Event
from django.forms.widgets import DateTimeInput

class EventForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'date', 'location']
