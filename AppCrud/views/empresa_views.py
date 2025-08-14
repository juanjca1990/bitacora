from .base_imports import *
from .job_views import filtrar_empresas


@login_required
@permission_required('AppCrud.view_empresa', raise_exception=True)
def empresa(request):
    usuario = request.user
    
    # Mostrar todas las empresas para permitir la navegación y cambio
    # Si es administrador, usar filtrar_empresas para obtener solo las que puede administrar
    empresas = Empresa.objects.all()
    if request.session.get('admin'):
        empresas = filtrar_empresas(request, empresas)
    
    # Add explicit ordering to avoid pagination warning
    empresas = empresas.order_by('id')
    
    # Implementar paginación
    paginator = Paginator(empresas, 10)
    page_number = request.GET.get('page')
    empresas_paginadas = paginator.get_page(page_number)
    
    # Obtener todas las empresas disponibles para el dropdown de cambio de empresa
    if request.session.get('admin'):
        if usuario.is_superuser:
            todas_empresas = Empresa.objects.all()
        elif hasattr(usuario, 'empresas_administradas') and usuario.empresas_administradas.exists():
            todas_empresas = usuario.empresas_administradas.all()
            if usuario.empresa:
                todas_empresas = todas_empresas.union(Empresa.objects.filter(id=usuario.empresa.id))
        else:
            todas_empresas = empresas
    else:
        todas_empresas = empresas
    
    # Obtener empresa actual desde la sesión si es admin, o la empresa del usuario si no es admin
    empresa_actual = None
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_actual = Empresa.objects.get(id=request.session['empresa_actual'])
        except Empresa.DoesNotExist:
            pass
    elif not request.session.get('admin') and usuario.empresa:
        empresa_actual = usuario.empresa
    
    return render(request, "AppCrud/empresa.html", {
        "empresas": empresas_paginadas,
        "empresa_admin": usuario.has_perm('AppCrud.empresa_admin'),
        "todas_empresas": todas_empresas,
        "empresa_actual": empresa_actual
    })


@login_required
@permission_required('AppCrud.add_empresa', raise_exception=True)
def empresaForm(request):
    if request.method == 'POST':
        empresa_form = EmpresaVisualForm(request.POST, request.FILES)
        print(request.FILES)
        if empresa_form.is_valid():
            empresa = empresa_form.save(commit=False)
            # Colores por defecto: primario azul, secundario blanco
            visual_empresa = VisualEmpresa(
                colorPrimario="#007bff",  # Azul
                colorSecundario="#ffffff",  # Blanco
                logo=request.FILES['logo']
            )
            visual_empresa.save()
            empresa.visual_empresa = visual_empresa
            empresa.save()
            empresas = Empresa.objects.all()
            usuario = request.user
            
            # Creación grupos:
            group_sin_admin, _ = Group.objects.get_or_create(name=empresa.nombre)
            permissions_to_add = [
                Permission.objects.get(codename='view_bitacora'),
                Permission.objects.get(codename='view_contacto'),
                Permission.objects.get(codename='view_job'),
                Permission.objects.get(codename='view_aviso')
            ]
            group_sin_admin.permissions.set(permissions_to_add)

            group_admin, _ = Group.objects.get_or_create(name=empresa.nombre + "_admin")
            permissions_to_add = [
                Permission.objects.get(codename='view_bitacora'),
                Permission.objects.get(codename='view_contacto'),
                Permission.objects.get(codename='view_job'),
                Permission.objects.get(codename='view_aviso'),
                Permission.objects.get(codename='add_bitacora'),
                Permission.objects.get(codename='add_contacto'),
                Permission.objects.get(codename='add_job'),
                Permission.objects.get(codename='add_aviso'),
                Permission.objects.get(codename='change_bitacora'),
                Permission.objects.get(codename='change_contacto'),
                Permission.objects.get(codename='change_job'),
                Permission.objects.get(codename='change_aviso'),
                Permission.objects.get(codename='delete_bitacora'),
                Permission.objects.get(codename='delete_contacto'),
                Permission.objects.get(codename='delete_job'),
                Permission.objects.get(codename='delete_aviso'),
                Permission.objects.get(codename='empresa_admin')
            ]
            group_admin.permissions.set(permissions_to_add)

            return redirect('./empresa/', {
                "empresas": empresas, 
                "empresa_admin": usuario.has_perm('AppCrud.empresa_admin')
            })

    empresa_form = EmpresaVisualForm()
    # Oculta los campos de color en el formulario
    return render(request, "AppCrud/empresaForm.html", {
        "empresa_form": empresa_form, 
        "hide_colors": True
    })


@login_required
@permission_required('AppCrud.change_empresa', raise_exception=True)
def editarEmpresa(request, id):
    empresa = Empresa.objects.get(id=id)
    if request.method == "POST":
        empresa_form = EmpresaVisualForm(request.POST, request.FILES, instance=empresa)
        if empresa_form.is_valid():
            empresa = empresa_form.save(commit=False)
            print(empresa.visual_empresa.colorPrimario)
            # Check if a new logo file was uploaded
            if 'logo' in request.FILES:
                visual_empresa = VisualEmpresa(
                    colorPrimario=request.POST['colorPrimario'],
                    colorSecundario=request.POST['colorSecundario'],
                    logo=request.FILES['logo']
                )
                visual_empresa.save()
                empresa.visual_empresa = visual_empresa
            else:
                # Keep the previous logo file
                empresa.visual_empresa.colorPrimario = request.POST['colorPrimario']
                empresa.visual_empresa.colorSecundario = request.POST['colorSecundario']
                
                print(empresa.visual_empresa.colorPrimario)
            print(empresa.visual_empresa.colorPrimario)
            empresa.visual_empresa.save()
            empresa.save()
            empresas = Empresa.objects.all()
            return redirect('../empresa/', {"empresas": empresas})
    else:
        empresa_form = EmpresaVisualForm(initial={
            "nombre": empresa.nombre,
            "colorPrimario": empresa.visual_empresa.colorPrimario,
            "colorSecundario": empresa.visual_empresa.colorSecundario,
            "logo": empresa.visual_empresa.logo
        })
    return render(request, "AppCrud/editarEmpresa.html", {
        "empresa_form": empresa_form, 
        "empresa": empresa
    })


@login_required
@permission_required('AppCrud.delete_empresa', raise_exception=True)
def borrarEmpresa(request, id):
    empresa = Empresa.objects.get(id=id)
    empresa.delete()
    empresas = Empresa.objects.all()
    usuario = request.user
    return redirect('../empresa/', {
        "empresas": empresas,
        "empresa_admin": usuario.has_perm('AppCrud.empresa_admin')
    })


@login_required
def empresa_otros(request):
    """Vista para usuarios que solo pueden ver y editar su propia empresa"""
    usuario = request.user
    if not usuario.empresa:
        # Si el usuario no tiene empresa asignada, redirigir con mensaje de error
        return redirect('../inicio/', {"mensaje": "No tienes una empresa asignada"})
    
    empresa = usuario.empresa
    return render(request, "AppCrud/empresa_otros.html", {
        "empresa": empresa,
        "user": usuario
    })
    

@login_required
def editarEmpresa_otros(request, id):
    """Vista para que los usuarios editen solo su propia empresa"""
    usuario = request.user
    if not usuario.empresa:
        # Si el usuario no tiene empresa asignada, redirigir con mensaje de error
        return redirect('../inicio/', {"mensaje": "No tienes una empresa asignada"})
    
    empresa = Empresa.objects.get(id=id)
    
    if request.method == "POST":
        empresa_form = EmpresaVisualForm(request.POST, request.FILES, instance=empresa)
        if empresa_form.is_valid():
            empresa = empresa_form.save(commit=False)
            # Check if a new logo file was uploaded
            if 'logo' in request.FILES:
                visual_empresa = VisualEmpresa(
                    colorPrimario=request.POST['colorPrimario'],
                    colorSecundario=request.POST['colorSecundario'],
                    logo=request.FILES['logo']
                )
                visual_empresa.save()
                empresa.visual_empresa = visual_empresa
            else:
                # Keep the previous logo file
                empresa.visual_empresa.colorPrimario = request.POST['colorPrimario']
                empresa.visual_empresa.colorSecundario = request.POST['colorSecundario']
                
            empresa.visual_empresa.save()
            empresa.save()
            return redirect('../empresa_otros/', {
                "mensaje": "Empresa actualizada correctamente"
            })
    else:
        empresa_form = EmpresaVisualForm(initial={
            "nombre": empresa.nombre,
            "colorPrimario": empresa.visual_empresa.colorPrimario,
            "colorSecundario": empresa.visual_empresa.colorSecundario,
            "logo": empresa.visual_empresa.logo
        })
    
    return render(request, "AppCrud/editarEmpresa.html", {
        "empresa_form": empresa_form, 
        "empresa": empresa,
        "es_empresa_otros": True  # Flag para distinguir en el template
    })
