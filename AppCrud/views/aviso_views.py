from .base_imports import *
from django.contrib import messages
from django.core.mail import send_mail
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import FileResponse
import io


@login_required
@permission_required('AppCrud.view_aviso', raise_exception=True)
def aviso(request):
    usuario = request.user
    
    # Si el usuario puede cambiar de empresa, filtrar por la empresa actual de la sesión
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_actual = Empresa.objects.get(id=request.session.get('empresa_actual'))
            avisos = Aviso.objects.filter(empresa=empresa_actual)
        except Empresa.DoesNotExist:
            avisos = Aviso.objects.all()
    else:
        # Filtrar avisos según los permisos del usuario
        if not usuario.is_superuser:
            if usuario.empresa:
                avisos = Aviso.objects.filter(empresa=usuario.empresa)
                empresa_actual = usuario.empresa
            else:
                avisos = Aviso.objects.none()
                empresa_actual = None
        else:
            avisos = Aviso.objects.all()
            empresa_actual = None
    
    # Obtener empresa actual desde la sesión si es admin, o la empresa del usuario si no es admin
    if request.session.get('admin') and request.session.get('empresa_actual'):
        try:
            empresa_actual = Empresa.objects.get(id=request.session['empresa_actual'])
        except Empresa.DoesNotExist:
            empresa_actual = None
    elif not request.session.get('admin') and usuario.empresa:
        empresa_actual = usuario.empresa
    else:
        empresa_actual = None
    
    return render(request, "AppCrud/aviso.html", {
        "avisos": avisos,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin'),
        "empresa_actual": empresa_actual
    })


@login_required
@permission_required('AppCrud.add_aviso', raise_exception=True)
def avisoForm(request):
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
        formulario = AvisoForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid():
            info = formulario.cleaned_data
            
            # Crear el aviso con la empresa actual, no con el texto del formulario
            aviso = Aviso(
                ambiente=info['ambiente'],
                inicio=info['inicio'],
                contacto=info['contacto'],
                job=info['job'],
                empresa=empresa_para_filtrar or usuario.empresa
            )
            aviso.save()
            avisos = Aviso.objects.all()
            return redirect("./aviso/", {
                "avisos": avisos,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
        
    else:
        formulario = AvisoForm(user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/avisoForm.html", {"formulario": formulario})


@login_required  
@permission_required('AppCrud.change_aviso', raise_exception=True) 
def editarAviso(request, id):
    aviso = Aviso.objects.get(id=id)
    usuario = request.user
    if (not usuario.empresa == aviso.empresa) and not usuario.is_superuser:
        raise PermissionDenied("No tiene permisos para editar este aviso.")
    
    # Determinar la empresa para filtrar (usar la empresa del aviso existente)
    empresa_para_filtrar = aviso.empresa
    
    if request.method == "POST":
        form = AvisoForm(request.POST, user=usuario, empresa_filtro=empresa_para_filtrar)
        if form.is_valid():
            info = form.cleaned_data
            # La empresa no cambia, mantener la empresa original del aviso
            aviso.ambiente = info["ambiente"]
            aviso.inicio = info["inicio"]
            aviso.job = info["job"]
            aviso.contacto = info["contacto"]
            aviso.save()
            avisos = Aviso.objects.all()
            return redirect("../aviso/", {
                "avisos": avisos,
                "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
            })
    else:
        formulario = AvisoForm(initial={
            "empresa": aviso.empresa.nombre, 
            "ambiente": aviso.ambiente, 
            "inicio": aviso.inicio, 
            "job": aviso.job,
            "contacto": aviso.contacto
        }, user=usuario, empresa_filtro=empresa_para_filtrar)
        return render(request, "AppCrud/editarAviso.html", {
            "formulario": formulario, 
            "aviso": aviso
        })


@login_required   
@permission_required('AppCrud.delete_aviso', raise_exception=True)
def borrarAviso(request, id):
    aviso = Aviso.objects.get(id=id)
    aviso.delete()
    avisos = Aviso.objects.all()
    usuario = request.user
    return redirect("../aviso/", {
        "avisos": avisos,
        "admin_perm": usuario.has_perm('AppCrud.empresa_admin')
    })


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
    from .bitacora_views import obtener_bitacoras_paginadas, filtrar_empresas
    
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

            try:
                send_mail(subject, message, 'avisos@exerom.com', emails)
                # Redirige a la página de inicio with un mensaje de éxito
                messages.success(request, 'Los correos electrónicos han sido enviados.')
                return redirect('bitacora')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
            
        # Si hay errores, mostrar el modal nuevamente
        paginated_bitacoras, empresas = obtener_bitacoras_paginadas(request)
        nombres_string = ""
        for nombre in nombres:
            nombres_string += nombre + ", "
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

    else:
        print("Hola, soy el job id: ", id)
        
        # asunto en el form es el nombre del job, anteponiendo "JOB: "
        form = EmailForm(initial={'asunto': f"JOB: {job.nombre}"})
        
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


@login_required
@permission_required('AppCrud.view_aviso', raise_exception=True)
def exportar_avisos_pdf(request):
    # Crear un buffer para el PDF
    buffer = io.BytesIO()

    # Configurar el documento PDF
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleTitle = styles["Title"]

    # Título del PDF
    elements = [Paragraph("Lista de Avisos", styleTitle)]

    # Obtener los datos de los avisos
    usuario = request.user
    if usuario.is_superuser:
        avisos = Aviso.objects.all()
    elif usuario.empresa:
        avisos = Aviso.objects.filter(empresa=usuario.empresa)
    else:
        avisos = Aviso.objects.none()

    # Crear la tabla de datos
    data = [["Empresa", "Ambiente", "Hora Inicio", "Job", "Contacto"]]
    for aviso in avisos:
        data.append([
            Paragraph(aviso.empresa.nombre, styleN),
            Paragraph(aviso.ambiente, styleN),
            # Paragraph(aviso.inicio.strftime("%H:%M"), styleN),
            Paragraph(aviso.inicio, styleN),
            Paragraph(aviso.job.nombre, styleN),
            Paragraph(aviso.contacto.nombre, styleN)
        ])

    # Estilo de la tabla
        # Ajustar los anchos de las columnas
    table = Table(data, colWidths=[100, 100, 150, 150, 80])
    # table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construir el PDF
    pdf.build(elements)

    # Retornar el archivo PDF como respuesta
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="avisos.pdf")
