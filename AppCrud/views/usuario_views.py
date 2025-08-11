from .base_imports import *

import json
import urllib.parse
import urllib.request
from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
import secrets
from django.contrib import messages

@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def registerOption(request):
    usuario = request.user
    return render(request, "AppCrud/registroUserOpcion.html", {"user": usuario})

@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def registerAdmin(request):
    if request.method == "POST":
        form = AsignarAdminForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data["usuario"]
            empresas = form.cleaned_data["empresas"]

            # Asegurar que el usuario sea staff
            usuario.is_staff = True
            usuario.save()

            # Limpiar empresas administradas anteriores
            usuario.empresas_administradas.clear()
            
            # Asignar las nuevas empresas
            for empresa in empresas:
                usuario.empresas_administradas.add(empresa)
                
                # Crear o actualizar el grupo de admin de la empresa con todos los permisos necesarios
                group_admin, created = Group.objects.get_or_create(name=f"{empresa.nombre}_admin_empresa")
                
                # Lista de permisos necesarios para administradores
                permission_codenames = [
                    # Permisos para Usuario
                    'view_user', 'add_user', 'change_user', 'delete_user',
                    # Permisos para Bitacora
                    'view_bitacora', 'add_bitacora', 'change_bitacora', 'delete_bitacora',
                    # Permisos para Contacto
                    'view_contacto', 'add_contacto', 'change_contacto', 'delete_contacto',
                    # Permisos para Job
                    'view_job', 'add_job', 'change_job', 'delete_job',
                    # Permisos para Aviso
                    'view_aviso', 'add_aviso', 'change_aviso', 'delete_aviso',
                    # Permisos para Empresa
                    'view_empresa', 'change_empresa',
                    # Permisos para Servidor
                    'view_servidor', 'add_servidor', 'change_servidor', 'delete_servidor',
                    # Permisos para Registro
                    'view_registro', 'add_registro', 'change_registro', 'delete_registro',
                    # Permisos para Estado
                    'view_estado', 'add_estado', 'change_estado', 'delete_estado',
                    # Permiso personalizado para administrador de empresa
                    'empresa_admin'
                ]
                
                # Obtener permisos que existen en la base de datos
                permissions_to_add = []
                for codename in permission_codenames:
                    try:
                        permission = Permission.objects.get(codename=codename)
                        permissions_to_add.append(permission)
                    except Permission.DoesNotExist:
                        print(f"Advertencia: El permiso '{codename}' no existe en la base de datos")
                
                # Asignar permisos al grupo
                group_admin.permissions.set(permissions_to_add)

                # Asignar el grupo de admin al usuario
                usuario.groups.add(group_admin)

            empresas_nombres = ", ".join([empresa.nombre for empresa in empresas])
            return redirect('./inicio/', {"mensaje": f"Usuario {usuario.username} ahora es administrador de: {empresas_nombres}"})
        else:
            return render(request, "AppCrud/registrarAdminMultiEmpresa.html", {"form": form, "mensaje": "Error al asignar administrador"})
    else:
        form = AsignarAdminForm()
        return render(request, "AppCrud/registrarAdminMultiEmpresa.html", {"form": form})

@login_required
def listaAdministradoresMultiEmpresa(request):
    """Lista usuarios que son administradores de múltiples empresas"""
    User = get_user_model()
    q_admins = request.GET.get('q_admins', '')
    
    # Buscar usuarios que tienen empresas administradas
    administradores = User.objects.filter(empresas_administradas__isnull=False).distinct()
    
    if q_admins:
        administradores = administradores.filter(
            Q(username__icontains=q_admins) | Q(email__icontains=q_admins)
        )
    
    # Add explicit ordering to avoid pagination warning
    administradores = administradores.order_by('id')
    admin_paginator = Paginator(administradores, 10)
    admin_page = request.GET.get('admin_page', 1)
    admin_obj = admin_paginator.get_page(admin_page)
    
    return render(request, "AppCrud/listaAdministradoresMultiEmpresa.html", {
        "administradores": admin_obj,
    })

@login_required  
def editarAdminMultiEmpresa(request, admin_id):
    """Editar las empresas administradas por un usuario"""
    User = get_user_model()
    admin_usuario = get_object_or_404(User, id=admin_id)
    
    if request.method == "POST":
        form = AsignarAdminForm(request.POST)
        
        # Forzar el usuario en el formulario después de la validación inicial
        form.data = form.data.copy()
        form.data['usuario'] = admin_usuario.id
        
        # Re-bind el formulario con el usuario correcto
        form = AsignarAdminForm(form.data)
        form.fields['usuario'].queryset = User.objects.filter(id=admin_usuario.id)
        
        if form.is_valid():
            empresas = form.cleaned_data["empresas"]

            # Limpiar empresas administradas anteriores
            admin_usuario.empresas_administradas.clear()
            
            # Limpiar grupos de administrador anteriores
            grupos_admin_anterior = admin_usuario.groups.filter(name__endswith='_admin_empresa')
            admin_usuario.groups.remove(*grupos_admin_anterior)
            
            # Asignar las nuevas empresas
            for empresa in empresas:
                admin_usuario.empresas_administradas.add(empresa)
                
                # Crear o actualizar el grupo de admin de la empresa
                group_admin, created = Group.objects.get_or_create(name=f"{empresa.nombre}_admin_empresa")
                
                # Lista de permisos necesarios para administradores
                permission_codenames = [
                    'view_user', 'add_user', 'change_user', 'delete_user',
                    'view_bitacora', 'add_bitacora', 'change_bitacora', 'delete_bitacora',
                    'view_contacto', 'add_contacto', 'change_contacto', 'delete_contacto',
                    'view_job', 'add_job', 'change_job', 'delete_job',
                    'view_aviso', 'add_aviso', 'change_aviso', 'delete_aviso',
                    'view_empresa', 'change_empresa',
                    'view_servidor', 'add_servidor', 'change_servidor', 'delete_servidor',
                    'view_registro', 'add_registro', 'change_registro', 'delete_registro',
                    'view_estado', 'add_estado', 'change_estado', 'delete_estado',
                    'empresa_admin'
                ]
                
                # Obtener permisos que existen en la base de datos
                permissions_to_add = []
                for codename in permission_codenames:
                    try:
                        permission = Permission.objects.get(codename=codename)
                        permissions_to_add.append(permission)
                    except Permission.DoesNotExist:
                        print(f"Advertencia: El permiso '{codename}' no existe en la base de datos")
                
                # Asignar permisos al grupo
                group_admin.permissions.set(permissions_to_add)

                # Asignar el grupo de admin al usuario
                admin_usuario.groups.add(group_admin)

            if empresas:
                empresas_nombres = ", ".join([empresa.nombre for empresa in empresas])
                messages.success(request, f"Usuario {admin_usuario.username} ahora administra: {empresas_nombres}")
            else:
                messages.success(request, f"Se removieron todos los permisos de administrador del usuario {admin_usuario.username}")
            
            return redirect('listaAdministradoresMultiEmpresa')
        else:
            messages.error(request, "Error al actualizar las empresas administradas")
            print("Errores del formulario:", form.errors)
    else:
        # Preseleccionar las empresas que ya administra
        empresas_actuales = admin_usuario.empresas_administradas.all()
        form = AsignarAdminForm(initial={
            'usuario': admin_usuario,
            'empresas': empresas_actuales
        })
        
        # Limitar el queryset del campo usuario solo a este usuario
        form.fields['usuario'].queryset = User.objects.filter(id=admin_usuario.id)
    
    # Hacer que el campo usuario esté oculto y configurar el queryset
    form.fields['usuario'].widget = forms.HiddenInput()
    form.fields['usuario'].initial = admin_usuario
    form.fields['usuario'].queryset = User.objects.filter(id=admin_usuario.id)
    
    return render(request, "AppCrud/editarAdminMultiEmpresa.html", {
        "form": form,
        "admin_usuario": admin_usuario
    })

@login_required
def detallesAdminMultiEmpresa(request, admin_id):
    """Ver detalles de un administrador multi-empresa"""
    User = get_user_model()
    admin_usuario = get_object_or_404(User, id=admin_id)
    
    return render(request, "AppCrud/detallesAdminMultiEmpresa.html", {
        "admin_usuario": admin_usuario,
        "empresas_administradas": admin_usuario.empresas_administradas.all(),
        "grupos": admin_usuario.groups.filter(name__endswith='_admin_empresa')
    })

@login_required
def editarPerfil(request):
    usuario=request.user

    if request.method=="POST":
        form=UserEditForm(request.POST)
        if form.is_valid():
            info=form.cleaned_data
            usuario.email=info["email"]
            usuario.password1=info["password1"]
            usuario.password2=info["password2"]
            usuario.first_name=info["first_name"]
            usuario.last_name=info["last_name"]
            usuario.save()
            return redirect('./inicio/', {"mensaje":f"Usuario {usuario.username} editado correctamente"})
        else:
            return render(request, "AppCrud/editarPerfil.html", {"form": form, "nombreusuario":usuario.username})
    else:
        form=UserEditForm(instance=usuario)
        return render(request, "AppCrud/editarPerfil.html", {"form": form, "nombreusuario":usuario.username})

def login_request(request):
    if request.method=="POST":
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # borro por si quedo registro en la sesion
            request.session['admin'] = False
            info=form.cleaned_data
            usu=info["username"]
            clave=info["password"]
            usuario=authenticate(username=usu, password=clave)
            if usuario is not None:
                login(request, usuario)
                cambiar_empresa(request)
                return redirect('../inicio/', {"mensaje":f"Usuario {usu} logueado correctamente"})
            else:
                return render(request, "AppCrud/login.html", {"form": form, "mensaje":"Usuario o contraseña incorrectos"})
        else:
            return render(request, "AppCrud/login.html", {"form": form, "mensaje":"Usuario o contraseña incorrectos"})
    else:
        form=AuthenticationForm()
        return render(request, "AppCrud/login.html", {"form": form})
    
def google_login(request):
    """Initiate Google OAuth login"""
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Google OAuth URL
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
    }
    print("params:", params)
    
    auth_url = f"{google_auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

def google_callback(request):
    """Handle Google OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # Crear el formulario para casos de error
    form = AuthenticationForm()
    
    # Verify state parameter
    if state != request.session.get('oauth_state'):
        return render(request, "AppCrud/login.html", {
            "form": form,
            "mensaje": "Error de seguridad en la autenticación"
        })
    
    if not code:
        return render(request, "AppCrud/login.html", {
            "form": form,
            "mensaje": "Error en la autenticación con Google"
        })
    
    try:
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
        }
        
        token_request = urllib.request.Request(
            token_url,
            data=urllib.parse.urlencode(token_data).encode(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urllib.request.urlopen(token_request) as response:
            token_response = json.loads(response.read().decode())
        
        access_token = token_response.get('access_token')
        id_token_str = token_response.get('id_token')
        
        if not access_token or not id_token_str:
            return render(request, "AppCrud/login.html", {
                "form": form,
                "mensaje": "Error obteniendo tokens de Google"
            })
        
        # Verify and decode the ID token
        idinfo = id_token.verify_oauth2_token(
            id_token_str, 
            requests.Request(), 
            settings.GOOGLE_OAUTH2_CLIENT_ID
        )
        
        # Get user info from Google
        google_user_id = idinfo.get('sub')
        email = idinfo.get('email')
        name = idinfo.get('name')
        
        if not email:
            return render(request, "AppCrud/login.html", {
                "form": form,
                "mensaje": "No se pudo obtener el email de Google"
            })
            
        # busco la persona con el email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "AppCrud/login.html", {
                "form": form,
                "mensaje": "El correo no está registrado en el sistema"
            })
        
        # EL CORREO EXISTE, LOGEO A LA PERSONA
        login(request, user)
        request.session['admin'] = False
        
        # Clean up session
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        messages.success(request, f"Usuario {user.username} logueado correctamente con Google")
        return redirect('inicio')
        
    except Exception as e:
        print("ERROR DE MIERDA")
        print(str(e))
        if errors := getattr(e, 'errors', None):
            error_message = errors[0].get('message', 'Error desconocido')
            return render(request, "AppCrud/login.html", {
                "form": form,
                "mensaje": f"Error en la autenticación: {error_message}"
            })
        return render(request, "AppCrud/login.html", {
            "form": form,
            "mensaje": f"Error en la autenticación: {str(e)}"
        })

@login_required
def cambiar_empresa(request):
    if request.method == "POST":
        print("Cambiando empresa. es un post..")
        empresa_id = request.POST.get("empresa_id")
        
        # Si empresa_id es None, tomar la primera empresa asignada al usuario
        if not empresa_id:
            empresas_asignadas = request.user.empresas_administradas.all()
            if empresas_asignadas.exists():
                empresa_id = empresas_asignadas.first().id
                print(f"No se proporcionó empresa_id. Asignando la primera empresa: {empresa_id}")
            else:
                print("El usuario no tiene empresas asignadas.")
                return redirect('inicio')  # Redirigir si no hay empresas asignadas
        
        print("la empresa es : ", empresa_id)
        try:
            nueva_empresa = Empresa.objects.get(id=empresa_id)
            # Verificar que el usuario tenga acceso a esta empresa
            if request.user.tiene_acceso_empresa(nueva_empresa):
                request.session['empresa_actual'] = nueva_empresa.id
                # Mantener la sesión admin si el usuario tiene permisos para cambiar empresas
                if request.user.is_superuser or (hasattr(request.user, 'empresas_administradas') and request.user.empresas_administradas.exists()):
                    request.session['admin'] = True
                print(f"Empresa cambiada a: {nueva_empresa.nombre}")
            else:
                print("Usuario no tiene acceso a esta empresa")
        except Empresa.DoesNotExist:
            print("Empresa no existe")
            pass
        # Redirige SIEMPRE después del POST
        return redirect('inicio')
    # Si GET, muestra la página normalmente
    print("fue un GET")

@login_required
def logout_request(request):
    logout(request)
    request.session["admin"] = False
    return redirect('Login')

@login_required
# lista todos los usuarios de las empresas excluyendo los administradores
def lista_usuarios(request):
    User = get_user_model()
    q_usuarios = request.GET.get('q_usuarios', '')
    
    # Excluir superusuarios y usuarios que tienen empresas administradas
    usuarios = User.objects.filter(is_superuser=False).exclude(empresas_administradas__isnull=False)
    
    if q_usuarios:
        usuarios = usuarios.filter(
            Q(username__icontains=q_usuarios) | Q(email__icontains=q_usuarios)
        )
    # Add explicit ordering to avoid pagination warning
    usuarios = usuarios.order_by('id')
    usuarios_paginator = Paginator(usuarios.distinct(), 10)
    usuarios_page = request.GET.get('usuarios_page', 1)
    usuarios_obj = usuarios_paginator.get_page(usuarios_page)
    return render(request, "AppCrud/lista_usuarios.html", {
        "usuarios": usuarios_obj,
    })
    
@login_required
#lista los administradores de una empresa en particular, incluyendo los superusuarios y usuarios que administran esa empresa
def listaAdministradoresEmpresa(request, empresa_id):
    User = get_user_model()
    empresa = get_object_or_404(Empresa, id=empresa_id)
    q_admins = request.GET.get('q_admins', '')
    
    # Incluir superusuarios y usuarios que administran esta empresa específica
    administradores = User.objects.filter(
        Q(is_superuser=True) | Q(empresas_administradas__id=empresa_id)
    ).distinct()
    
    if q_admins:
        administradores = administradores.filter(
            Q(username__icontains=q_admins) | Q(email__icontains=q_admins)
        )
    
    # Add explicit ordering to avoid pagination warning
    administradores = administradores.order_by('id')
    admin_paginator = Paginator(administradores, 10)
    admin_page = request.GET.get('admin_page', 1)
    admin_obj = admin_paginator.get_page(admin_page)
    return render(request, "AppCrud/listaAdministradoresEmpresa.html", {
        "administradores": admin_obj,
        "empresa_actual": empresa,
    })

@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def RegistrarUsuario(request):
    #si es el admin que ingresa primero el campo esta vacio
    if 'empresa_actual' not in request.session:
        empresa = Empresa.objects.first()  # obtengo la primer empresa si es admin el que ingreso
    else:
        empresa = request.session['empresa_actual']
        empresa = get_object_or_404(Empresa, id=empresa)
    print("empresa actual:", empresa)
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        # Remove el campo de seleccion de empresa
        if 'empresa' in form.fields:
            del form.fields['empresa']
            
        if form.is_valid():
            user = form.save(commit=False)
            usernm = form.cleaned_data.get("username")

            # Always assign the empresa from URL parameter
            user.empresa = empresa
            user.save()

            # Assign group according to empresa
            try:
                group = Group.objects.get(name=empresa.nombre)
                user.groups.add(group)
            except Group.DoesNotExist:
                # If group doesn't exist, create it or handle the error
                pass

            return redirect('inicio')
        else:
            return render(request, "AppCrud/registrarUsuarioVistaAdmin.html", {
                "form": form, 
                "mensaje": "Error al crear el usuario", 
                "tipo": "Usuario", 
                "empresa": empresa
            })
    else:
        form = RegistroUsuarioForm()
        # Remove empresa field since it will be shown in template as read-only info
        if 'empresa' in form.fields:
            del form.fields['empresa']
        return render(request, "AppCrud/registrarUsuarioVistaAdmin.html", {
            "form": form, 
            "tipo": "Usuario", 
            "empresa": empresa
        })

@login_required
@permission_required('AppCrud.change_user', raise_exception=True)
def editar_usuario(request, user_id):
    """Vista para editar un usuario existente"""
    User = get_user_model()
    usuario_a_editar = get_object_or_404(User, id=user_id)
    
    # Verificar que el usuario actual tenga permisos para editar este usuario
    if not request.user.is_superuser:
        # Si no es superusuario, verificar que sea admin de la empresa del usuario
        if usuario_a_editar.empresa and not request.user.es_admin_empresa(usuario_a_editar.empresa):
            messages.error(request, "No tienes permisos para editar este usuario.")
            return redirect('usuarios')
    
    if request.method == "POST":
        form = RegistroUsuarioAdminEditForm(request.POST, instance=usuario_a_editar)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Si se cambió la empresa, actualizar los grupos
            empresa_anterior = usuario_a_editar.empresa
            nueva_empresa = form.cleaned_data.get('empresa')
            
            if empresa_anterior != nueva_empresa:
                # Remover del grupo anterior si existe
                if empresa_anterior:
                    try:
                        grupo_anterior = Group.objects.get(name=empresa_anterior.nombre)
                        user.groups.remove(grupo_anterior)
                    except Group.DoesNotExist:
                        pass
                
                # Agregar al nuevo grupo si existe
                if nueva_empresa:
                    try:
                        nuevo_grupo = Group.objects.get(name=nueva_empresa.nombre)
                        user.groups.add(nuevo_grupo)
                    except Group.DoesNotExist:
                        pass
            
            user.save()
            messages.success(request, f"Usuario {user.username} editado correctamente.")
            return redirect('usuarios')
        else:
            messages.error(request, "Error al editar el usuario.")
    else:
        form = RegistroUsuarioAdminEditForm(instance=usuario_a_editar)
    
    return render(request, "AppCrud/editarUsuario.html", {
        "form": form,
        "usuario_a_editar": usuario_a_editar
    })

@login_required
@permission_required('AppCrud.delete_user', raise_exception=True)
def eliminar_usuario(request, user_id):
    """Vista para eliminar un usuario"""
    User = get_user_model()
    usuario_a_eliminar = get_object_or_404(User, id=user_id)
    
    # Verificar que el usuario actual tenga permisos para eliminar este usuario
    if not request.user.is_superuser:
        # No permitir que se elimine a sí mismo
        if usuario_a_eliminar == request.user:
            messages.error(request, "No puedes eliminarte a ti mismo.")
            return redirect('usuarios')
        
        # Si no es superusuario, verificar que sea admin de la empresa del usuario
        if usuario_a_eliminar.empresa and not request.user.es_admin_empresa(usuario_a_eliminar.empresa):
            messages.error(request, "No tienes permisos para eliminar este usuario.")
            return redirect('usuarios')
    
    # No permitir eliminar superusuarios
    if usuario_a_eliminar.is_superuser:
        messages.error(request, "No se puede eliminar un superusuario.")
        return redirect('usuarios')
    
    # No permitir eliminar administradores de empresas
    if usuario_a_eliminar.empresas_administradas.exists():
        messages.error(request, "No se puede eliminar un administrador de empresas. Primero remueve sus permisos de administrador.")
        return redirect('usuarios')
    
    if request.method == "POST":
        username = usuario_a_eliminar.username
        usuario_a_eliminar.delete()
        messages.success(request, f"Usuario {username} eliminado correctamente.")
        return redirect('usuarios')
    
    return render(request, "AppCrud/eliminarUsuario.html", {
        "usuario_a_eliminar": usuario_a_eliminar
    })
