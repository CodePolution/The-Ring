from django import template

register = template.Library()


@register.filter(name='last')
def last(value):
    return value.last()
