from .base_imports import *
from .job_views import filtrar_empresas


def filtrar_bitacoras(request, bitacoras):
    query = Q()
    periodo = request.GET.get('periodo')
    dia = request.GET.get('dia')
    hora = request.GET.get('hora')
    impacto = request.GET.get('impacto')
    job = request.GET.get('job')
    if dia:
        query &= Q(dias__icontains=dia)
    if periodo:
        query &= Q(periodo__icontains=periodo)
    if hora:
        query &= Q(inicio__icontains=hora)
    if impacto:
        query &= Q(impacto__icontains=impacto)
    if job:
        query &= Q(job__nombre__icontains=job)
    return bitacoras.filter(query)


def obtener_bitacoras_paginadas(request):
    # Si el usuario puede cambiar de empresa, usar solo la empresa actual de la sesión para filtrar
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_actual = Empresa.objects.get(id=request.session.get('empresa_actual'))
            empresas = [empresa_actual]  # Solo para filtrar el contenido
        except Empresa.DoesNotExist:
            empresas = Empresa.objects.all()
            empresas = filtrar_empresas(request, empresas)
    else:
        empresas = Empresa.objects.all()
        empresas = filtrar_empresas(request, empresas)
    
    bitacoras_by_empresa = {}
    for empresa in empresas:
        bitacoras = Bitacora.objects.filter(empresa=empresa)
        bitacoras = filtrar_bitacoras(request, bitacoras)
        if bitacoras.exists():
            bitacoras_by_empresa[empresa] = bitacoras

    paginated_bitacoras = {}
    table_number = 1
    for empresa, bitacoras in bitacoras_by_empresa.items():
        # Add explicit ordering to avoid pagination warning
        bitacoras = bitacoras.order_by('id')
        paginator = Paginator(bitacoras, 20)
        page_number = request.GET.get('page{}'.format(table_number), 1)
        page_obj = paginator.get_page(page_number)
        paginated_bitacoras[empresa] = page_obj
        table_number += 1
    
    return paginated_bitacoras, empresas


@login_required
@permission_required('AppCrud.view_bitacora', raise_exception=True)
def bitacora(request):
    usuario = request.user
    paginated_bitacoras, empresas = obtener_bitacoras_paginadas(request)
    
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

    return render(request, "AppCrud/bitacora.html", {
        "paginated_bitacoras": paginated_bitacoras, 
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'), 
        "empresas": todas_empresas,
        "empresa_actual": empresa_actual
    })


@login_required
@permission_required('AppCrud.add_bitacora', raise_exception=True)
def bitacoraForm(request, other_periodo=None):
    usuario = request.user
    
    # Determinar la empresa para filtrar jobs
    empresa_para_filtrar = None
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_para_filtrar = Empresa.objects.get(id=request.session.get('empresa_actual'))
            print(f"Admin detectado - Empresa actual: {empresa_para_filtrar.nombre}")
        except Empresa.DoesNotExist:
            print("Admin detectado pero empresa_actual no existe")
            pass
    elif usuario.empresa:
        empresa_para_filtrar = usuario.empresa
        print(f"Usuario normal - Empresa: {empresa_para_filtrar.nombre}")
    else:
        print("No se pudo determinar empresa para filtrar")
    
    print(f"Empresa para filtrar: {empresa_para_filtrar}")
    print(f"Session admin: {request.session.get('admin')}")
    print(f"Session empresa_actual: {request.session.get('empresa_actual')}")
    
    # Verificar qué jobs están disponibles para esta empresa
    if empresa_para_filtrar:
        jobs_disponibles = Job.objects.filter(empresa=empresa_para_filtrar)
        print(f"Jobs disponibles para {empresa_para_filtrar.nombre}: {jobs_disponibles.count()}")
        for job in jobs_disponibles:
            print(f"  - {job.nombre} ({job.empresa.nombre})")
    else:
        print("No hay empresa para filtrar, mostrando todos los jobs")
        jobs_disponibles = Job.objects.all()
        print(f"Total de jobs: {jobs_disponibles.count()}")
    
    if request.method == 'POST':
        formulario = BitacoraForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        if formulario.is_valid():
            info = formulario.cleaned_data
            print("Per:" + info['periodo'])
            print(info['other_periodo'])
            if info['periodo'] == 'Otro':
                info['periodo'] = info['other_periodo']
            info.pop('other_periodo', None)
            bitacora = Bitacora(**info)
            
            bitacora.empresa = bitacora.job.empresa
            bitacora.ambiente = bitacora.job.ambiente
            bitacora.save()
            bitacoras = Bitacora.objects.all()
            return redirect("./bitacora/", {
                "bitacoras": bitacoras, 
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
    else:
        formulario = BitacoraForm(user=usuario, empresa_filtro=empresa_para_filtrar)
        # Verificar qué jobs tiene el formulario después de crearlo
        print(f"Jobs en el formulario: {formulario.fields['job'].queryset.count()}")
        for job in formulario.fields['job'].queryset:
            print(f"  - {job.nombre} ({job.empresa.nombre})")
        
    return render(request, "AppCrud/bitacoraForm.html", {"formulario": formulario})


@login_required
@permission_required('AppCrud.change_bitacora', raise_exception=True)
def editarBitacora(request, id):
    bitacora = Bitacora.objects.get(id=id)
    usuario = request.user
    
    # Verificar permisos: superuser, empresa propia, o empresa administrada
    tiene_permisos = (
        usuario.is_superuser or 
        usuario.empresa == bitacora.empresa or
        (hasattr(usuario, 'empresas_administradas') and 
         usuario.empresas_administradas.filter(id=bitacora.empresa.id).exists())
    )
    
    if not tiene_permisos:
        raise PermissionDenied("No tiene permisos para editar esta bitácora.")
    
    # Determinar la empresa para filtrar jobs (usar la empresa de la bitácora existente)
    empresa_para_filtrar = bitacora.empresa
    
    if request.method == "POST":
        form = BitacoraForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        print(form)
        if form.is_valid():
            print("Hola")
            info = form.cleaned_data
            print("Hola")
            if info['periodo'] == 'Otro':
                info['periodo'] = info['other_periodo']
            info.pop('other_periodo', None)  # Remove 'other_periodo' from cleaned_data
            bitacora.inicio = info["inicio"]
            bitacora.job = info["job"]
            bitacora.impacto = info["impacto"]
            bitacora.periodo = info["periodo"]
            bitacora.descripcion = info["descripcion"]
            bitacora.dias = info["dias"]
            bitacora.tiempo_estimado = info["tiempo_estimado"]
            bitacora.si_cancela = info["si_cancela"]
            bitacora.empresa = bitacora.job.empresa
            bitacora.ambiente = bitacora.job.ambiente
            bitacora.save()
            bitacoras = Bitacora.objects.all()
            usuario = request.user
            return redirect('../bitacora/', {
                "bitacoras": bitacoras,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
    else:
        formulario = BitacoraForm(initial={
            "empresa": bitacora.empresa, 
            "ambiente": bitacora.ambiente, 
            "inicio": bitacora.inicio, 
            "job": bitacora.job,
            "impacto": bitacora.impacto, 
            "tiempo_estimado": bitacora.tiempo_estimado,
            "si_cancela": bitacora.si_cancela,
            "periodo": bitacora.periodo,
            "dias": bitacora.dias,
            "descripcion": bitacora.descripcion
        }, user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/editarBitacora.html", {
            "formulario": formulario, 
            "bitacora": bitacora
        })


@login_required  
@permission_required('AppCrud.delete_bitacora', raise_exception=True)
def borrarBitacora(request, id):
    bitacora = Bitacora.objects.get(id=id)
    bitacora.delete()
    bitacoras = Bitacora.objects.all()
    usuario = request.user
    return redirect('../bitacora/', {
        "bitacoras": bitacoras,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
    })
