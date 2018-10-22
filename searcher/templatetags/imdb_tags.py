from django import template

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
