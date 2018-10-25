from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from otrtools.views import BaseView
from .process import process
from .forms import AddForm

class AddView(BaseView):
    template_name = 'downloader/add.html'
    form_class = AddForm

    def form_valid(self, form, **kwargs):
        video = form.cleaned_data.get("video")
        audio = form.cleaned_data.get("audio")
        cutlist = form.cleaned_data.get("cutlist")
        keep = form.cleaned_data.get("keep")
        mega = form.cleaned_data.get("Mega", False)
        ctx = self.get_context_data(**kwargs)
        if not process.delay(video, cutlist, audio_url=audio, mega=mega, keep=keep):
            ctx['failed'] = True

        return HttpResponseRedirect(reverse('downloader:add')) #render(self.request, 'downloader/add.html', ctx)

    def get_initial(self):
        initial = super().get_initial()

        initial['video'] = self.request.GET.get("video", "")
        initial['audio'] = self.request.GET.get("audio", "")
        initial['cutlist'] = self.request.GET.get("cutlist", "")
        return initial
