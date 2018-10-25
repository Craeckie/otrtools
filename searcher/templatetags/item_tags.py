from django import template
from django.urls import reverse
from urllib.parse import quote
from django.utils.safestring import mark_safe

register = template.Library()


format_label = {
  'AVI' : 'primary',
  'HQ'  : 'danger',
  'HD'  : 'warning',
  'MP4' : 'info',
  'AC3' : 'success'
}
@register.filter(name='format2label')
def format2label(f):
    if f in format_label:
      return format_label[f]
    else:
      return None

@register.simple_tag
def cutlist_call(item, i, num):
    return mark_safe('loadCutlists(%s)' % \
      ', '.join(map(lambda x: f"'{x}'",
        [reverse('searcher:cutlist', kwargs={'file': item['file_decrypted']}),
         quote(item['chosen_mirror']['link']),
         item['chosen_mirror']['name'],
         f'#cutlist-table-{num}-{i}'])))
      # "{{ item.chosen_mirror.link|urlencode }}",
      # "{{ item.chosen_mirror.name }}",
      # "#cutlist-table-{{ num }}-{{ forloop.counter }}");"
