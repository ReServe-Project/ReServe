# PersonalGoals/templatetags/json_filters.py
from django import template
import json

register = template.Library()

@register.filter(name='to_json')
def to_json(value):
    return json.dumps(value)