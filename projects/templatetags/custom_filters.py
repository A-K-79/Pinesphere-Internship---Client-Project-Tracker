from django import template

register = template.Library()

@register.filter
def key(d, key_name):
    """Get value from dict using a key"""
    if isinstance(d, dict):
        return d.get(key_name, None)
    return None

@register.filter
def add(value, arg):
    """Add arg to value"""
    try:
        return str(value) + str(arg)
    except:
        return ''

@register.filter
def stringformat_custom(value, format_string):
    """Format string like sprintf"""
    try:
        return format_string % value
    except:
        return str(value)
