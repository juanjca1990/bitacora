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
            empresa = form.cleaned_data["empresa"]

            # Asigna la nueva empresa al usuario
            usuario.empresa = empresa
            usuario.is_staff = True  # Asegúrate de que el usuario sea staff
            usuario.save()

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

            # Asigna el grupo de admin al usuario
            usuario.groups.clear()
            usuario.groups.add(group_admin)

            return redirect('./inicio/', {"mensaje": f"Usuario {usuario.username} ahora es administrador de {empresa.nombre} con todos los permisos necesarios"})
        else:
            return render(request, "AppCrud/registrarUsuario.html", {"form": form, "mensaje": "Error al asignar administrador", "tipo": "Administrador"})
    else:
        form = AsignarAdminForm()
        return render(request, "AppCrud/registrarUsuario.html", {"form": form, "tipo": "Administrador"})

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
    request.session['admin'] = True
    return redirect('inicio')

@login_required
def logout_request(request):
    logout(request)
    request.session["admin"] = False
    return redirect('Login')

@login_required
def lista_usuarios(request):
    User = get_user_model()
    q_usuarios = request.GET.get('q_usuarios', '')
    usuarios = User.objects.filter(is_superuser=False).exclude(groups__name__endswith='_admin')
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
def lista_administradores(request):
    User = get_user_model()
    q_admins = request.GET.get('q_admins', '')
    administradores = User.objects.filter(is_superuser=True) | User.objects.filter(groups__name__endswith='_admin')
    if q_admins:
        administradores = administradores.filter(
            Q(username__icontains=q_admins) | Q(email__icontains=q_admins)
        )
    admin_paginator = Paginator(administradores.distinct(), 10)
    admin_page = request.GET.get('admin_page', 1)
    admin_obj = admin_paginator.get_page(admin_page)
    return render(request, "AppCrud/lista_administradores.html", {
        "administradores": admin_obj,
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
