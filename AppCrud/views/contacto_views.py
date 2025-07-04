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
    empresas = Empresa.objects.all()
    empresas = filtrar_empresas(request, empresas)
    contactos_by_empresa = {}
    for empresa in empresas:
        contactos = Contacto.objects.filter(empresa=empresa)
        contactos = filtrar_contactos(request, contactos)
        if contactos.exists():
            contactos_by_empresa[empresa] = contactos
    usuario = request.user
    return render(request, "AppCrud/contacto.html", {
        "contactos_by_empresa": contactos_by_empresa,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'),
    })


@login_required
@permission_required('AppCrud.add_contacto', raise_exception=True)
def contactoForm(request):
    usuario = request.user
    if request.method == 'POST':
        formulario = ContactoForm(request.POST, user=usuario)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid():
            info = formulario.cleaned_data
            contacto = Contacto(**info)
            contacto.save()
            contactos = Contacto.objects.all()
            usuario = request.user
            return redirect("./contacto/", {
                "contactos": contactos,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
        
    else:
        formulario = ContactoForm(user=usuario)
        return render(request, "AppCrud/contactoForm.html", {"formulario": formulario})


@login_required 
@permission_required('AppCrud.change_contacto', raise_exception=True)
def editarContacto(request, id):
    contacto = Contacto.objects.get(id=id)
    usuario = request.user
    if request.method == "POST":
        form = ContactoForm(request.POST, user=usuario)
        if form.is_valid():
            info = form.cleaned_data
            contacto.nombre = info["nombre"]
            contacto.mail = info["mail"]
            contacto.telefono = info["telefono"]
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
            "empresa": contacto.empresa, 
            "mail": contacto.mail, 
            "telefono": contacto.telefono
        }, user=usuario)
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
