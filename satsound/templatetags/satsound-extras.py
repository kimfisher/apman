from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def wpstatic(resource):
    return '%s%s' % (settings.WPSTATIC_URL, resource)
