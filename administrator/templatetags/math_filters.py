from django import template

register = template.Library()

def safe_float_convert(value):
    """Safely convert value to float, handling lists and other types"""
    if value is None:
        return 0.0
    if isinstance(value, list):
        # If it's a list, take the first element or return 0
        return float(value[0]) if value and value[0] is not None else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

@register.filter
def div(value, arg):
    """Divides the value by the argument."""
    try:
        safe_value = safe_float_convert(value)
        safe_arg = safe_float_convert(arg)
        return safe_value / safe_arg if safe_arg != 0 else 0
    except (ValueError, ZeroDivisionError, TypeError):
        return 0