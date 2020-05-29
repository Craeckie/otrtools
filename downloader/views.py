import json
from ast import literal_eval

import requests
from celery.app import control
from celery.app.control import Control, Inspect
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, ListView, TemplateView

from otrtools.celery import app
from otrtools.views import BaseView
from .process import process
from .forms import AddForm

session = requests.session()


@csrf_exempt
def startRequest(request):
    video = request.POST.get("video")
    cutlist = request.POST.get("cutlist")
    dest = request.POST.get("dest")
    ret = False
    message = None
    try:
        ret = startDownload(video, cutlist, dest)
    except Exception as e:
        message = str(e)
    if ret:
        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'success': False,
            'message': message
        })
    return

def startDownload(video, cutlist, dest, audio=None, keep=False):
    return process.delay(video, cutlist, session, audio_url=audio, destName=dest, keep=keep)

class AddView(BaseView, FormView):
    template_name = 'downloader/add.html'
    form_class = AddForm

    def form_valid(self, form, **kwargs):
        video = form.cleaned_data.get("video")
        audio = form.cleaned_data.get("audio")
        cutlist = form.cleaned_data.get("cutlist")
        dest = form.cleaned_data.get("dest")
        keep = form.cleaned_data.get("keep")
        # mega = form.cleaned_data.get("Mega", False)
        ctx = self.get_context_data(**kwargs)
        if not startDownload(video, cutlist, dest, audio, keep):
            ctx['failed'] = True

        return HttpResponseRedirect(reverse('downloader:add'))  # render(self.request, 'downloader/add.html', ctx)


    def get_initial(self):
        initial = super().get_initial()

        initial['video'] = self.request.GET.get("video", "")
        initial['audio'] = self.request.GET.get("audio", "")
        initial['cutlist'] = self.request.GET.get("cutlist", "")
        initial['dest'] = self.request.GET.get("dest", "")
        return initial

    def get_context_data(self, **kwargs):
        ctx = super(FormView, self).get_context_data(**kwargs)
        ctx.update(super(AddView, self).get_context_data(**kwargs))
        return ctx

class DownloadsView(BaseView, TemplateView):
    template_name = 'downloader/downloads.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        tasks_data = requests.get(f'http://{settings.FLOWER_HOST}/api/tasks')
        tasks = tasks_data.json()
        for task_id in tasks:
            task = tasks[task_id]
            if 'args' in task and 'kwargs' in task:
                args = eval(task['args'])
                # args = json.loads(args.replace('(', '[').replace(')', ']').replace("'", '"'))
                kwargs = eval(task['kwargs'])
                print(args + ", " + kwargs)
        # print(tasks)
        return ctx
