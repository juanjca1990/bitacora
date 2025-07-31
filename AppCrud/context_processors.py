from django.contrib.auth import get_user_model
from AppCrud.models import Empresa

def lista_usuarios(request):
    User = get_user_model()
    # Incluye superusers, staff y usuarios en grupos de admin
    return {'users': User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True) | User.objects.filter(groups__name__endswith='_admin')}

def lista_empresas(request):
    """Contexto para proporcionar la lista de empresas disponibles para el usuario"""
    context = {}
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # Los superusuarios pueden ver todas las empresas
            empresas = Empresa.objects.all()
        elif hasattr(request.user, 'empresas_administradas'):
            # Los administradores pueden ver las empresas que administran y su empresa asignada
            empresas_admin = request.user.empresas_administradas.all()
            if request.user.empresa:
                # Combinar empresa asignada con empresas administradas
                empresas = empresas_admin.union(Empresa.objects.filter(id=request.user.empresa.id))
            else:
                empresas = empresas_admin
        elif request.user.empresa:
            # Usuario regular solo ve su empresa
            empresas = Empresa.objects.filter(id=request.user.empresa.id)
        else:
            empresas = Empresa.objects.none()
        
        context['empresas'] = empresas
        
        # Obtener empresa actual de la sesión o la empresa del usuario por defecto
        empresa_actual_id = request.session.get('empresa_actual')
        if empresa_actual_id:
            try:
                empresa_actual = Empresa.objects.get(id=empresa_actual_id)
                # Verificar que el usuario tenga acceso a esta empresa
                if request.user.tiene_acceso_empresa(empresa_actual):
                    context['empresa_actual'] = empresa_actual
                else:
                    # Si no tiene acceso, usar su empresa por defecto
                    context['empresa_actual'] = request.user.empresa
                    request.session['empresa_actual'] = request.user.empresa.id if request.user.empresa else None
            except Empresa.DoesNotExist:
                context['empresa_actual'] = request.user.empresa
                request.session['empresa_actual'] = request.user.empresa.id if request.user.empresa else None
        else:
            # Si no hay empresa en sesión, usar la empresa del usuario
            context['empresa_actual'] = request.user.empresa
            if request.user.empresa:
                request.session['empresa_actual'] = request.user.empresa.id
    
    return context

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