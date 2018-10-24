from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class MovieIndexForm(forms.Form):
    query = forms.CharField(label="Query to otrkeyfinder.de", max_length=200)
    min_duration = forms.IntegerField(initial=80, min_value=0, max_value=500, label="Minimum duration")
    max_page = forms.IntegerField(initial=20, min_value=1, max_value=50, label="Maximum pages")
    start_page = forms.IntegerField(initial=0, min_value=0, max_value=30, label="Start page")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Search'))

class SeriesIndexForm(forms.Form):
    url = forms.URLField(label="URL to episode list", max_length=300)
    website = forms.ChoiceField(
      label="Website",
      choices=(
        ('IM', 'IMDB'),
        ('SJ', 'Serienjunkies'),
    ))
    series = forms.CharField(label="Name of the series", max_length=100)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Search'))
