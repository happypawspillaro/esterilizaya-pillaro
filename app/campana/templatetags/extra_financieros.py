from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Permite acceder a un diccionario con clave dinámica en templates:
    {{ mi_dict|get_item:clave }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
