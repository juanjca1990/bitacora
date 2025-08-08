from .base_imports import *


def filtrar_empresas(request, empresas):
    """Filtra las empresas según los parámetros de búsqueda y permisos del usuario"""
    query = Q()
    emp = request.GET.get('emp')
    if emp:
        query &= Q(nombre__icontains=emp)
    
    # Filtrar empresas según permisos del usuario
    usuario = request.user
    if not usuario.is_superuser:
        # Si el usuario no es superuser, solo mostrar empresas que puede administrar o su empresa asignada
        empresas_permitidas = Q()
        if usuario.empresa:
            empresas_permitidas |= Q(id=usuario.empresa.id)
        if hasattr(usuario, 'empresas_administradas'):
            empresas_administradas_ids = usuario.empresas_administradas.values_list('id', flat=True)
            if empresas_administradas_ids:
                empresas_permitidas |= Q(id__in=empresas_administradas_ids)
        query &= empresas_permitidas
    
    return empresas.filter(query)


def filtrar_jobs(request, jobs):
    query = Q()
    nombre = request.GET.get('nombre')
    ambiente = request.GET.get('ambiente')
    if ambiente:
        query &= Q(ambiente__icontains=ambiente)
    if nombre:
        query &= Q(nombre__icontains=nombre)

    return jobs.filter(query)


@login_required
@permission_required('AppCrud.view_job', raise_exception=True)
def job(request):
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
    
    jobs_by_empresa = {}
    for empresa in empresas:
        jobs = Job.objects.filter(empresa=empresa)
        jobs = filtrar_jobs(request, jobs)
        if jobs.exists():
            jobs_by_empresa[empresa] = jobs

    paginated_jobs = {}

    table_number = 1
    for empresa, jobs in jobs_by_empresa.items():
        # Add explicit ordering to avoid pagination warning
        jobs = jobs.order_by('id')
        paginator = Paginator(jobs, 20)
        page_number = request.GET.get('page{}'.format(table_number), 1)
        page_obj = paginator.get_page(page_number)
        paginated_jobs[empresa] = page_obj
        table_number += 1
    
    # Obtener todas las empresas disponibles para el dropdown de cambio de empresa
    usuario = request.user
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
    
    return render(request, "AppCrud/job.html", {
        "paginated_jobs": paginated_jobs, 
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'),
        "empresas": todas_empresas,
        "empresa_actual": empresa_actual
    })


@login_required
@permission_required('AppCrud.add_job', raise_exception=True)
def jobForm(request):
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
        formulario = JobForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid():
            info = formulario.cleaned_data
            print(info)
            
            # Crear el job con la empresa actual, no con el texto del formulario
            job = Job(
                nombre=info['nombre'],
                ambiente=info['ambiente'],
                descripcion=info['descripcion'],
                empresa=empresa_para_filtrar or usuario.empresa
            )
            job.save()
            jobs = Job.objects.all()
            return redirect("./job/", {
                "jobs": jobs,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
        
    else:
        formulario = JobForm(user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/jobForm.html", {"formulario": formulario})


@login_required
@permission_required('AppCrud.change_job', raise_exception=True)
def editarJob(request, id):
    job = Job.objects.get(id=id)
    usuario = request.user
    
    # Verificar permisos: superuser, empresa propia, o empresa administrada
    tiene_permisos = (
        usuario.is_superuser or 
        usuario.empresa == job.empresa or
        (hasattr(usuario, 'empresas_administradas') and 
         usuario.empresas_administradas.filter(id=job.empresa.id).exists())
    )
    
    if not tiene_permisos:
        raise PermissionDenied("No tiene permisos para editar este job.")
    
    # Determinar la empresa para filtrar (usar la empresa del job existente)
    empresa_para_filtrar = job.empresa
    
    if request.method == "POST":
        form = JobForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        if form.is_valid():
            info = form.cleaned_data
            job.nombre = info["nombre"]
            job.ambiente = info["ambiente"]
            job.descripcion = info["descripcion"]
            # La empresa no cambia, mantener la empresa original del job
            job.save()
            jobs = Job.objects.all()
            return redirect("../job/", {
                "jobs": jobs,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
    else:
        formulario = JobForm(initial={
            "nombre": job.nombre, 
            "empresa": job.empresa.nombre, 
            "ambiente": job.ambiente, 
            "descripcion": job.descripcion
        }, user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/editarJob.html", {
            "formulario": formulario, 
            "job": job
        })


@login_required
@permission_required('AppCrud.delete_job', raise_exception=True)
def borrarJob(request, id):
    job = Job.objects.get(id=id)
    usuario = request.user
    
    # Verificar permisos: superuser, empresa propia, o empresa administrada
    tiene_permisos = (
        usuario.is_superuser or 
        (usuario.empresa and usuario.empresa == job.empresa) or
        (hasattr(usuario, 'empresas_administradas') and 
         usuario.empresas_administradas.filter(id=job.empresa.id).exists())
    )
    
    if not tiene_permisos:
        raise PermissionDenied("No tiene permisos para eliminar este job.")
    
    job.delete()
    jobs = Job.objects.all()
    return redirect("../job/", {
        "jobs": jobs,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
    })


@csrf_exempt
def get_job_description(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        job_id = data.get('job_id')
        try:
            job = Job.objects.get(id=job_id)
            return JsonResponse({'descripcion': job.descripcion})
        except Job.DoesNotExist:
            return JsonResponse({'descripcion': ''})
    return JsonResponse({'descripcion': ''})


