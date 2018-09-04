from django import template
import numpy as np
register = template.Library()

@register.filter_function
def order_by(queryset, args):
    if queryset is None:
        return None
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)
    
@register.filter_function
def subtract(value,arg):
    return int(value - arg)

@register.filter_function
def times(value,arg):
    return int(value*arg)
    
@register.filter_function
def subtract2(value, arg):
    return int(value - arg * 0.8)
    
@register.filter_function
def times2(value):
    return int(value * 2 * 0.8)