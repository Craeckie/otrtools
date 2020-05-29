from searcher.forms import SimpleSearchForm


class BaseView:
    def get_context_data(self, *args, **kwargs):
        ctx = {
            'nav_form' : SimpleSearchForm()
        }
        return ctx
