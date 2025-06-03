from django import template
from django.forms.utils import ErrorList

register = template.Library()

@register.filter(name='add_bootstrap_class')
def add_bootstrap_class(field, css_class="form-control"):
    if field is None:
        return ''
    # Ensure that field.field exists and has an attribute widget
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and hasattr(field.field.widget, 'attrs'):
        existing_class = field.field.widget.attrs.get('class', '')
        # Avoid adding form-control if it's a checkbox or radio, let Bootstrap handle them
        if field.field.widget.__class__.__name__ in ['CheckboxInput', 'RadioSelect']:
            if 'form-check-input' not in existing_class:
                 field.field.widget.attrs['class'] = f'{existing_class} form-check-input'.strip()
        elif css_class not in existing_class:
            field.field.widget.attrs['class'] = f'{existing_class} {css_class}'.strip()
    return field

@register.filter(name='as_bootstrap_errors')
def as_bootstrap_errors(errors):
    if not isinstance(errors, ErrorList) or not errors:
        return ''
    error_html = '<div class="alert alert-danger mt-1 p-2" role="alert">'
    if len(errors) == 1:
        error_html += f'<small>{errors.as_text().strip("* ")}</small>'
    else:
        error_html += '<ul class="mb-0 list-unstyled">'
        for error in errors:
            error_html += f'<li><small>{error}</small></li>'
        error_html += '</ul>'
    error_html += '</div>'
    return template.mark_safe(error_html) 