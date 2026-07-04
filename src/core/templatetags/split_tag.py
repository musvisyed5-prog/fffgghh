from django import template

register = template.Library()


@register.filter
def split(value, sep=","):
    return value.split(sep)



@register.filter
def is_list(value):
    return isinstance(value, list)



@register.filter
def remove_brackets(value):
    return str(value).replace("[]", "")