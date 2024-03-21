from django import template


register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)