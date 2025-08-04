from .base_imports import *
from .job_views import filtrar_empresas


def filtrar_contactos(request, contactos):
    query = Q()
    nombre = request.GET.get('nombre')
    tel = request.GET.get('tel')
    mail = request.GET.get('mail')
    if tel:
        query &= Q(telefono__icontains=tel)
    if nombre:
        query &= Q(nombre__icontains=nombre)
    if mail:
        query &= Q(mail__icontains=mail)

    return contactos.filter(query)


@login_required
@permission_required('AppCrud.view_contacto', raise_exception=True)
def contacto(request):
    # Si el usuario puede cambiar de empresa, usar solo la empresa actual de la sesión
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_actual = Empresa.objects.get(id=request.session.get('empresa_actual'))
            empresas = [empresa_actual]
        except Empresa.DoesNotExist:
            empresas = Empresa.objects.all()
            empresas = filtrar_empresas(request, empresas)
    else:
        empresas = Empresa.objects.all()
        empresas = filtrar_empresas(request, empresas)
    
    contactos_by_empresa = {}
    for empresa in empresas:
        contactos = Contacto.objects.filter(empresa=empresa)
        contactos = filtrar_contactos(request, contactos)
        if contactos.exists():
            contactos_by_empresa[empresa] = contactos
    usuario = request.user
    
    # Obtener empresa actual desde la sesión si es admin, o la empresa del usuario si no es admin
    empresa_actual = None
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_actual = Empresa.objects.get(id=request.session['empresa_actual'])
        except Empresa.DoesNotExist:
            pass
    elif not request.session.get('admin') and usuario.empresa:
        empresa_actual = usuario.empresa
    
    return render(request, "AppCrud/contacto.html", {
        "contactos_by_empresa": contactos_by_empresa,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'),
        "empresa_actual": empresa_actual
    })


@login_required
@permission_required('AppCrud.add_contacto', raise_exception=True)
def contactoForm(request):
    usuario = request.user
    
    # Determinar la empresa para filtrar
    empresa_para_filtrar = None
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_para_filtrar = Empresa.objects.get(id=request.session.get('empresa_actual'))
        except Empresa.DoesNotExist:
            empresa_para_filtrar = None
    elif usuario.empresa:
        empresa_para_filtrar = usuario.empresa
    
    if request.method == 'POST':
        formulario = ContactoForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid():
            info = formulario.cleaned_data
            
            # Crear el contacto con la empresa actual, no con el texto del formulario
            contacto = Contacto(
                nombre=info['nombre'],
                mail=info['mail'],
                telefono=info['telefono'],
                empresa=empresa_para_filtrar or usuario.empresa
            )
            contacto.save()
            contactos = Contacto.objects.all()
            usuario = request.user
            return redirect("./contacto/", {
                "contactos": contactos,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
        
    else:
        formulario = ContactoForm(user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/contactoForm.html", {"formulario": formulario})


@login_required 
@permission_required('AppCrud.change_contacto', raise_exception=True)
def editarContacto(request, id):
    contacto = Contacto.objects.get(id=id)
    usuario = request.user
    if (not usuario.empresa == contacto.empresa) and not usuario.is_superuser:
        raise PermissionDenied("No tiene permisos para editar este contacto.")
    
    # Determinar la empresa para filtrar (usar la empresa del contacto existente)
    empresa_para_filtrar = contacto.empresa
    
    if request.method == "POST":
        form = ContactoForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        if form.is_valid():
            info = form.cleaned_data
            contacto.nombre = info["nombre"]
            contacto.mail = info["mail"]
            contacto.telefono = info["telefono"]
            # La empresa no cambia, se mantiene la original
            contacto.save()
            contactos = Contacto.objects.all()
            usuario = request.user
            return redirect("../contacto/", {
                "contactos": contactos,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
    else:
        formulario = ContactoForm(initial={
            "nombre": contacto.nombre,
            "mail": contacto.mail, 
            "telefono": contacto.telefono
        }, user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/editarContacto.html", {
            "formulario": formulario, 
            "contacto": contacto
        })


@login_required
@permission_required('AppCrud.delete_contacto', raise_exception=True)
def borrarContacto(request, id):
    contacto = Contacto.objects.get(id=id)
    contacto.delete()
    contactos = Contacto.objects.all()
    usuario = request.user
    return redirect("../contacto/", {
        "contactos": contactos,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
    })
