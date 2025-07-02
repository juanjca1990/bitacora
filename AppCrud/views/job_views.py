from .base_imports import *


def filtrar_empresas(request, empresas):
    query = Q()
    emp = request.GET.get('emp')
    if emp:
        query &= Q(nombre__icontains=emp)
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
        if formulario.is_valid:
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

def obtener_mails_y_nombres(job):
    emails = []
    nombres = []
    # obtener los avisos que tenga asignado ese job
    avisos = Aviso.objects.filter(job=job)
    # por cada aviso, obtener los contactos que tenga asignado ese aviso
    for aviso in avisos:
        contactos = Contacto.objects.filter(aviso=aviso)
        # por cada contacto, obtener el email y guardarlo en la lista
        for contacto in contactos:
            emails.append(contacto.mail)
            nombres.append(contacto.nombre)
    return(emails, nombres)

def avisar(request, id):
    job = Job.objects.get(id=id)
    emails, nombres = obtener_mails_y_nombres(job)
    if len(emails) == 0:
        # generate alert in template
        mensaje = f"No hay contactos asignados al trabajo {job.nombre}"
        messages.info(request, mensaje)
        return redirect('bitacora')

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            # enviar mail a cada email de la lista con el aviso
            subject = form.cleaned_data.get("asunto")
            message = form.cleaned_data.get("mensaje")
            from_email = "avisos@exerom.com"

            send_mail(subject, message, 'avisos@exerom.com', emails)
            # Redirige a la página de inicio with un mensaje de éxito
            messages.success(request, 'Los correos electrónicos han sido enviados.')
            
            return redirect('bitacora')

    else:
        print("Hola, soy el job id: ", id)
        
        # asunto en el form es el nombre del job, anteponiendo "JOB: "
        form = EmailForm(initial={'asunto': f"JOB: {job.nombre}"})
        
        # Importar la función desde bitacora_views
        from .bitacora_views import obtener_bitacoras_paginadas
        paginated_bitacoras, empresas = obtener_bitacoras_paginadas(request)
        
        # create string with nombres separated by commas
        nombres_string = ""
        for nombre in nombres:
            nombres_string += nombre + ", "
        # remove last comma
        nombres_string = nombres_string[:-2]

        usuario = request.user
        return render(request, "AppCrud/bitacora.html", {
            "paginated_bitacoras": paginated_bitacoras, 
            "admin_perm": usuario.has_perm('AppCrud.empresa_admin'), 
            "empresas": empresas, 
            'job': job, 
            'form': form, 
            "nombres": nombres_string
        })
