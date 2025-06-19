from django import template
from ..utils import encode_id

register = template.Library()

@register.filter(name='hash_id')
def hash_id(id_number):
    """
    A template filter that converts an integer ID into a hashid string.
    Usage in template: {{ my_object.id|hash_id }}
    """
    return encode_id(id_number) 