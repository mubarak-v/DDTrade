from django import template

register = template.Library()

@register.filter
def flot(value):
    """
    Custom template filter to format a floating-point number to 2 decimal places.
    """
    try:
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails
