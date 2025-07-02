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
    return render (request, "AppCrud/registroUserOpcion.html")

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

            # Asigna el grupo de admin de la empresa
            group = Group.objects.get(name=f"{empresa.nombre}_admin")
            usuario.groups.clear()
            usuario.groups.add(group)

            return redirect('./inicio/', {"mensaje": f"Usuario {usuario.username} ahora es administrador de {empresa.nombre}"})
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
