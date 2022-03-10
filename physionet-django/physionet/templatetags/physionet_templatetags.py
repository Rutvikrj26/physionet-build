from django import template
from physionet.models import StaticPage

register = template.Library()

@register.simple_tag
def get_static_page():
    static_page_obj = StaticPage.objects.all().order_by('nav_order')
    return static_page_obj