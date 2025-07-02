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

    return render(request, "AppCrud/bitacora.html", {
        "paginated_bitacoras": paginated_bitacoras, 
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'), 
        "empresas": empresas
    })


@login_required
@permission_required('AppCrud.add_bitacora', raise_exception=True)
def bitacoraForm(request, other_periodo=None):
    usuario = request.user
    if request.method == 'POST':
        formulario = BitacoraForm(request.POST, user=usuario)
        if formulario.is_valid():
            info = formulario.cleaned_data
            print("Per:" + info['periodo'])
            print(info['other_periodo'])
            if info['periodo'] == 'Otro':
                info['periodo'] = info['other_periodo']
            info.pop('other_periodo', None)  # Remove 'other_periodo' from cleaned_data
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
        formulario = BitacoraForm(user=usuario)
    return render(request, "AppCrud/bitacoraForm.html", {"formulario": formulario})


@login_required
@permission_required('AppCrud.change_bitacora', raise_exception=True)
def editarBitacora(request, id):
    bitacora = Bitacora.objects.get(id=id)
    usuario = request.user
    if (not usuario.empresa == bitacora.empresa) and not usuario.is_superuser:
        raise PermissionDenied("You do not have permission to access this page.")
    if request.method == "POST":
        form = BitacoraForm(request.POST, user=usuario)
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
        }, user=usuario)
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
