from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def json_encode(obj):
    return mark_safe(json.dumps(obj))