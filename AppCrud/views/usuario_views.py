from .base_imports import *

@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def register(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            usernm = form.cleaned_data.get("username")
            empresa = form.cleaned_data.get("empresa")

            # Asignar empresa solo si no es superusuario
            if not user.is_superuser:
                user.empresa = empresa

            user.save()

            # Asignar grupo según la empresa
            if empresa:
                group = Group.objects.get(name=empresa)
                user.groups.add(group)

            return redirect('./inicio/', {"mensaje": f"Usuario {usernm} creado correctamente"})
        else:
            return render(request, "AppCrud/registrarUsuario.html", {"form": form, "mensaje": "Error al crear el usuario", "tipo": "Usuario"})
    else:
        form = RegistroUsuarioForm()
        return render(request, "AppCrud/registrarUsuario.html", {"form": form, "tipo": "Usuario"})

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
        form = AsignarAdminForm(request.POST, initial={'usuario': admin_usuario})
        # Hacer que el campo usuario esté oculto ya que estamos editando
        form.fields['usuario'].widget = forms.HiddenInput()
        form.fields['usuario'].initial = admin_usuario
        
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

            empresas_nombres = ", ".join([empresa.nombre for empresa in empresas])
            messages.success(request, f"Usuario {admin_usuario.username} ahora administra: {empresas_nombres}")
            return redirect('listaAdministradoresMultiEmpresa')
        else:
            messages.error(request, "Error al actualizar las empresas administradas")
    else:
        # Preseleccionar las empresas que ya administra
        empresas_actuales = admin_usuario.empresas_administradas.all()
        form = AsignarAdminForm(initial={
            'usuario': admin_usuario,
            'empresas': empresas_actuales
        })
        # Hacer que el campo usuario esté oculto
        form.fields['usuario'].widget = forms.HiddenInput()
    
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
                return redirect('../inicio/', {"mensaje":f"Usuario {usu} logueado correctamente"})
            else:
                return render(request, "AppCrud/login.html", {"form": form, "mensaje":"Usuario o contraseña incorrectos"})
        else:
            return render(request, "AppCrud/login.html", {"form": form, "mensaje":"Usuario o contraseña incorrectos"})
    else:
        form=AuthenticationForm()
        return render(request, "AppCrud/login.html", {"form": form})

@login_required
def cambiar_usuario(request):
    User = get_user_model()
    if request.method == "POST":
        print("Cambiando usuario. es un post..")
        user_id = request.POST.get("user_id")
        print("el usuario es : ", user_id)
        try:
            nuevo_usuario = User.objects.get(id=user_id)
            login(request, nuevo_usuario)
            request.session['admin'] = True
        except User.DoesNotExist:
            pass
        # Redirige SIEMPRE después del POST
        return redirect('inicio')
    # Si GET, muestra la página normalmente
    print("fue un GET")
    # request.session['admin'] = True
    # return redirect('inicio')

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
    usuarios_paginator = Paginator(usuarios.distinct(), 10)
    usuarios_page = request.GET.get('usuarios_page', 1)
    usuarios_obj = usuarios_paginator.get_page(usuarios_page)
    return render(request, "AppCrud/lista_usuarios.html", {
        "usuarios": usuarios_obj,
    })

@login_required
#lista todos los administradores de las empresas tomando únicamente la tabla user_empresas_administradas
def lista_administradores(request):
    User = get_user_model()
    q_admins = request.GET.get('q_admins', '')
    
    # Solo incluir usuarios que tienen empresas administradas (tabla user_empresas_administradas)
    # Usar prefetch_related para optimizar las consultas de empresas administradas
    administradores = User.objects.filter(
        empresas_administradas__isnull=False
    ).prefetch_related('empresas_administradas').distinct()
    
    if q_admins:
        administradores = administradores.filter(
            Q(username__icontains=q_admins) | Q(email__icontains=q_admins)
        )
    
    admin_paginator = Paginator(administradores, 10)
    admin_page = request.GET.get('admin_page', 1)
    admin_obj = admin_paginator.get_page(admin_page)
    return render(request, "AppCrud/lista_administradores.html", {
        "administradores": admin_obj,
    })
    
    
@login_required
#lista los usuarios de una empresa en particular, excluyendo los administradores
def listaUsuariosEmpresa(request, empresa_id): 
    User = get_user_model()
    empresa = get_object_or_404(Empresa, id=empresa_id)
    q_usuarios = request.GET.get('q_usuarios', '')
    
    # Usuarios de la empresa específica, excluyendo superusuarios y administradores de empresas
    usuarios = User.objects.filter(
        is_superuser=False, 
        empresa_id=empresa_id
    ).exclude(empresas_administradas__isnull=False)
    
    if q_usuarios:
        usuarios = usuarios.filter(
            Q(username__icontains=q_usuarios) | Q(email__icontains=q_usuarios)
        )
    usuarios_paginator = Paginator(usuarios.distinct(), 10)
    usuarios_page = request.GET.get('usuarios_page', 1)
    usuarios_obj = usuarios_paginator.get_page(usuarios_page)
    return render(request, "AppCrud/listaUsuariosEmpresa.html", {
        "usuarios": usuarios_obj,
        "empresa": empresa,
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
    
    admin_paginator = Paginator(administradores, 10)
    admin_page = request.GET.get('admin_page', 1)
    admin_obj = admin_paginator.get_page(admin_page)
    return render(request, "AppCrud/listaAdministradoresEmpresa.html", {
        "administradores": admin_obj,
        "empresa": empresa,
    })

@login_required
def register_user_vista_admin(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        # Remove empresa field since it's automatically assigned
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
