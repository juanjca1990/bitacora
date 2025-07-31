from django import template

register = template.Library()

@register.filter
def index(lista, i):
    try:
        return lista[i]
    except (IndexError, TypeError):
        return None

@register.filter
def tiene_acceso_empresa(user, empresa):
    """Filtro para verificar si un usuario tiene acceso a una empresa"""
    if hasattr(user, 'tiene_acceso_empresa'):
        return user.tiene_acceso_empresa(empresa)
    return False

@register.filter
def es_admin_empresa(user, empresa):
    """Filtro para verificar si un usuario es administrador de una empresa"""
    if hasattr(user, 'es_admin_empresa'):
        return user.es_admin_empresa(empresa)
    return False