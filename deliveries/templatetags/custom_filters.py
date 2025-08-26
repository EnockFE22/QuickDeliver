from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica o valor pelo argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """Formata como moeda brasileira"""
    try:
        return f"R$ {float(value):.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return "R$ 0,00"