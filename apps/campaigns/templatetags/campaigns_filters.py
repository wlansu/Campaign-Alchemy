from django import template

register = template.Library()


@register.filter
def to_class_name(value):
    """A filter to show the class name in a template.

    Used in the `search_results.html` template.
    """
    return value.__class__.__name__
