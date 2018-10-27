from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Series

class MovieIndexForm(forms.Form):
    query = forms.CharField(
        label="Query to otrkeyfinder.de",
        max_length=200,
        widget=forms.TextInput(attrs={'required': False}))

    min_duration = forms.IntegerField(initial=80, min_value=0, max_value=500, label="Minimum duration")
    max_page = forms.IntegerField(initial=20, min_value=1, max_value=50, label="Maximum pages")
    start_page = forms.IntegerField(initial=1, min_value=0, max_value=30, label="Start page")
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'post'
        helper.add_input(Submit('submit', 'Search'))
        return helper

class SimpleSearchForm(MovieIndexForm):
    # class Meta:
    #     fields = ['query']
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['max_page'] = 10
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        self.fields['max_page'].widget = forms.HiddenInput()
        self.fields['min_duration'].widget = forms.HiddenInput()
        self.fields['start_page'].widget = forms.HiddenInput()

class SeriesIndexForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['url', 'website', 'series']
        labels = {
            'url': "URL to episode list",
            'website': "Website",
            'series': "Name of the series",
        }
        widgets = {
            'website': forms.Select(choices=(
            ('IM', 'IMDB'),
            ('SJ', 'Serienjunkies'),
            ))
        }

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'post'
        helper.add_input(Submit('submit', 'Search'))
        return helper
