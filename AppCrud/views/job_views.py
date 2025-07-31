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
        paginator = Paginator(jobs, 20)
        page_number = request.GET.get('page{}'.format(table_number), 1)
        page_obj = paginator.get_page(page_number)
        paginated_jobs[empresa] = page_obj
        table_number += 1
        
    usuario = request.user
    return render(request, "AppCrud/job.html", {
        "paginated_jobs": paginated_jobs, 
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'),
        "empresas": empresas
    })


@login_required
@permission_required('AppCrud.add_job', raise_exception=True)
def jobForm(request):
    usuario = request.user
    if request.method == 'POST':
        formulario = JobForm(request.POST, user=usuario)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid():
            info = formulario.cleaned_data
            print(info)
            job = Job(**info)
            job.save()
            jobs = Job.objects.all()
            return redirect("./job/", {
                "jobs": jobs,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
        
    else:
        formulario = JobForm(user=usuario)
        return render(request, "AppCrud/jobForm.html", {"formulario": formulario})


@login_required
@permission_required('AppCrud.change_job', raise_exception=True)
def editarJob(request, id):
    job = Job.objects.get(id=id)
    usuario = request.user
    if request.method == "POST":
        form = JobForm(request.POST, user=usuario)
        if form.is_valid():
            info = form.cleaned_data
            job.nombre = info["nombre"]
            job.ambiente = info["ambiente"]
            job.descripcion = info["descripcion"]
            job.empresa = info["empresa"]
            job.save()
            jobs = Job.objects.all()
            return redirect("../job/", {
                "jobs": jobs,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
    else:
        formulario = JobForm(initial={
            "nombre": job.nombre, 
            "empresa": job.empresa, 
            "ambiente": job.ambiente, 
            "descripcion": job.descripcion
        }, user=usuario)
        return render(request, "AppCrud/editarJob.html", {
            "formulario": formulario, 
            "job": job
        })


@login_required
@permission_required('AppCrud.delete_job', raise_exception=True)
def borrarJob(request, id):
    job = Job.objects.get(id=id)
    job.delete()
    jobs = Job.objects.all()
    usuario = request.user
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


