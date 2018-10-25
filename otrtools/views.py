from django.views.generic.edit import FormView
from searcher.forms import SimpleSearchForm

class BaseView(FormView):
    def get_context_data(self, *args, **kwargs):
        ctx = super(BaseView, self).get_context_data(**kwargs)
        ctx['nav_form'] = SimpleSearchForm()
        return ctx
