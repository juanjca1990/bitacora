from django.contrib.auth import get_user_model

def lista_usuarios(request):
    User = get_user_model()
    # Incluye superusers, staff y usuarios en grupos de admin
    return {'users': User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True) | User.objects.filter(groups__name__endswith='_admin')}

def empresa_permissions(request):
    """Contexto para verificar permisos de empresa en templates"""
    context = {}
    if request.user.is_authenticated:
        # Función para verificar si el usuario tiene acceso a una empresa específica
        def tiene_acceso_empresa(empresa):
            return request.user.tiene_acceso_empresa(empresa)
        
        # Función para verificar si el usuario es admin de una empresa específica
        def es_admin_empresa(empresa):
            return request.user.es_admin_empresa(empresa)
            
        context['tiene_acceso_empresa'] = tiene_acceso_empresa
        context['es_admin_empresa'] = es_admin_empresa
        context['empresas_administradas'] = request.user.empresas_administradas.all() if hasattr(request.user, 'empresas_administradas') else []
    
    return context