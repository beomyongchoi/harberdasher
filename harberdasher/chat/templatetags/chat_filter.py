from django import template

register = template.Library()

def replace(value, arg):
    """Replace a value to arg"""
    return arg

register.filter('replace', replace)
