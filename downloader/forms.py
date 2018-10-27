from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class AddForm(forms.Form):
    video = forms.CharField(label="Video (required):", max_length=500, widget=forms.TextInput(attrs={'placeholder': 'http://'}))
    audio = forms.CharField(label="Audio:", max_length=500, required=False, widget=forms.TextInput(attrs={'placeholder': 'http://'}))
    cutlist = forms.CharField(label="Cutlist:", max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'http://www.cutlist.at/getfile.php?id='}))
    dest = forms.CharField(label="Destination:", max_length=300, required=False, widget=forms.TextInput(attrs={'placeholder': 'My Series s01e01 - My episode.%s' % settings.DEST_EXT}))
    keep = forms.BooleanField(label="Keep temporary files", initial=False, required=False)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'post'
        helper.add_input(Submit('submit', 'Start!'))
        return helper
