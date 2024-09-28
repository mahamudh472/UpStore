from django import template

register = template.Library()

@register.simple_tag
def get_total(cart):
    total = 0
    for item in cart:
        total += item.subtotal()
    
    return total