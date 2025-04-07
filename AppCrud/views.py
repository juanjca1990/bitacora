from collections import defaultdict
import locale
from django.http import JsonResponse
from django.shortcuts import render, redirect
from AppCrud.models import  Estado, Job, Contacto, Aviso, Bitacora, Empresa, RegistroMonitor, Servidor, User, VisualEmpresa
from AppCrud.forms import JobForm, EmailForm, ContactoForm, AvisoForm, BitacoraForm, RegistroMonitorForm, RegistroUsuarioForm, ServidorForm, UserEditForm, EmpresaVisualForm

from django.core.paginator import Paginator

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.db.models import Q
import datetime
from django.utils.timezone import now
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, timedelta
from django.shortcuts import get_object_or_404
import json
from dateutil.relativedelta import relativedelta
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle ,PageTemplate, BaseDocTemplate ,Frame ,Paragraph# type: ignore
from reportlab.lib.pagesizes import letter ,landscape # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib import colors # type: ignore
from django.http import FileResponse
import io
from reportlab.lib.styles import getSampleStyleSheet # type: ignore


def inicio(request):
    mensaje = request.GET.get('mensaje', '')
    
    return render (request, "AppCrud/inicio.html", {"mensaje":mensaje})

def filtrar_jobs(request,jobs):
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
    return render(request,"AppCrud/job.html",{"paginated_jobs": paginated_jobs, "admin_perm": usuario.has_perm('AppCrud.empresa_admin'),"empresas":empresas})

@login_required
@permission_required('AppCrud.add_job', raise_exception=True)
def jobForm(request):
    usuario = request.user
    if request.method == 'POST':
        formulario = JobForm(request.POST,user=usuario)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid:
            info = formulario.cleaned_data
            print(info)
            job = Job(**info)
            job.save()
            jobs=Job.objects.all()
            return redirect("./job/",{"jobs":jobs,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        
    else:
        formulario = JobForm(user=usuario)
        return render(request,"AppCrud/jobForm.html",{"formulario":formulario})
@login_required
@permission_required('AppCrud.change_job', raise_exception=True)
def editarJob(request, id):
    job=Job.objects.get(id=id)
    usuario = request.user
    if request.method=="POST":
        form= JobForm(request.POST,user=usuario)
        if form.is_valid():
            info=form.cleaned_data
            job.nombre=info["nombre"]
            job.ambiente=info["ambiente"]
            job.descripcion=info["descripcion"]
            job.empresa=info["empresa"]
            job.save()
            jobs=Job.objects.all()
            return redirect("../job/" ,{"jobs":jobs,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        pass
    else:
        formulario= JobForm(initial={"nombre":job.nombre, "empresa":job.empresa, "ambiente":job.ambiente, "descripcion":job.descripcion},user=usuario)
        return render(request,"AppCrud/editarJob.html", {"formulario": formulario, "job": job})
@login_required
@permission_required('AppCrud.delete_job', raise_exception=True)
def borrarJob(request, id):
    job=Job.objects.get(id=id)
    job.delete()
    jobs=Job.objects.all()
    usuario = request.user
    return redirect("../job/", {"jobs": jobs,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})

#Contacto

def filtrar_contactos(request,contactos):
    query = Q()
    nombre = request.GET.get('nombre')
    tel = request.GET.get('tel')
    mail= request.GET.get('mail')
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
        contactos = filtrar_contactos(request,contactos)
        if contactos.exists():
            contactos_by_empresa[empresa] = contactos
    usuario = request.user
    return render(request,"AppCrud/contacto.html",{"contactos_by_empresa":contactos_by_empresa,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
@login_required
@permission_required('AppCrud.add_contacto', raise_exception=True)
def contactoForm(request):
    usuario = request.user
    if request.method == 'POST':

        formulario = ContactoForm(request.POST,user=usuario)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid:
            info = formulario.cleaned_data
            contacto = Contacto(**info)
            contacto.save()
            contactos=Contacto.objects.all()
            usuario = request.user
            return redirect("./contacto/",{"contactos":contactos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        
    else:
        formulario = ContactoForm(user=usuario)
        return render(request,"AppCrud/contactoForm.html",{"formulario":formulario})
@login_required 
@permission_required('AppCrud.change_contacto', raise_exception=True)
def editarContacto(request, id):
    contacto=Contacto.objects.get(id=id)
    usuario = request.user
    if request.method=="POST":
        form= ContactoForm(request.POST,user=usuario)
        if form.is_valid():
            info=form.cleaned_data
            contacto.nombre=info["nombre"]
            contacto.mail= info["mail"]
            contacto.telefono=info["telefono"]
            contacto.save()
            contactos=Contacto.objects.all()
            usuario = request.user
            return redirect("../contacto/" ,{"contactos":contactos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        pass
    else:
        formulario= ContactoForm(initial={"nombre":contacto.nombre,"empresa":contacto.empresa, "mail":contacto.mail, "telefono":contacto.telefono},user=usuario)
        return render(request,"AppCrud/editarContacto.html", {"formulario": formulario, "contacto": contacto})
@login_required
@permission_required('AppCrud.delete_contacto', raise_exception=True)
def borrarContacto(request, id):
    contacto=Contacto.objects.get(id=id)
    contacto.delete()
    contactos=Contacto.objects.all()
    usuario = request.user
    return redirect("../contacto/", {"contactos": contactos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})


#Aviso
@login_required
@permission_required('AppCrud.view_aviso', raise_exception=True)
def aviso(request):
    avisos=Aviso.objects.all()
    usuario = request.user
    return render(request,"AppCrud/aviso.html",{"avisos":avisos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
@login_required
@permission_required('AppCrud.add_aviso', raise_exception=True)
def avisoForm(request):
    usuario = request.user
    if request.method == 'POST':
        formulario = AvisoForm(request.POST,user=usuario)
        print("-------------------------------")
        print(formulario)
        print("-------------------------------")
        if formulario.is_valid:
            info = formulario.cleaned_data
            aviso = Aviso(**info)
            aviso.save()
            avisos=Aviso.objects.all()
            return redirect("./aviso/",{"avisos":avisos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        
    else:
        formulario = AvisoForm(user=usuario)
        return render(request,"AppCrud/avisoForm.html",{"formulario":formulario})
@login_required  
@permission_required('AppCrud.change_aviso', raise_exception=True) 
def editarAviso(request, id):
    aviso=Aviso.objects.get(id=id)
    usuario = request.user
    if request.method=="POST":
        form= AvisoForm(request.POST,user=usuario)
        if form.is_valid():
            info=form.cleaned_data
            aviso.empresa=info["empresa"]
            aviso.ambiente= info["ambiente"]
            aviso.inicio=info["inicio"]
            aviso.job= info["job"]
            aviso.contacto=info["contacto"]
            aviso.save()
            avisos=Aviso.objects.all()
            return redirect("../aviso/" ,{"avisos":avisos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        pass
    else:
        formulario= AvisoForm(initial={"empresa":aviso.empresa, "ambiente":aviso.ambiente, "inicio":aviso.inicio, "job":aviso.job,"contacto":aviso.contacto},user=usuario)
        return render(request,"AppCrud/editarAviso.html", {"formulario": formulario, "aviso": aviso})
@login_required   
@permission_required('AppCrud.delete_aviso', raise_exception=True)
def borrarAviso(request, id):
    aviso=Aviso.objects.get(id=id)
    aviso.delete()
    avisos=Aviso.objects.all()
    usuario = request.user
    return redirect("../aviso/", {"avisos": avisos,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})


#Bitacora
def filtrar_empresas(request,empresas):
    query = Q()
    emp = request.GET.get('emp')
    if emp:
        query &= Q(nombre__icontains=emp)
    return empresas.filter(query)
def filtrar_bitacoras(request,bitacoras):
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
@login_required
@permission_required('AppCrud.view_bitacora', raise_exception=True)
def bitacora(request):

    usuario = request.user
    paginated_bitacoras, empresas= obtener_bitacoras_paginadas(request)

    return render(request, "AppCrud/bitacora.html", {"paginated_bitacoras": paginated_bitacoras, "admin_perm": usuario.has_perm('AppCrud.empresa_admin'), "empresas": empresas})

@login_required
@permission_required('AppCrud.add_bitacora', raise_exception=True)
def bitacoraForm(request, other_periodo=None):
    usuario = request.user
    if request.method == 'POST':
        formulario = BitacoraForm(request.POST, user=usuario)
        if formulario.is_valid():
            info = formulario.cleaned_data
            print("Per:"+info['periodo'])
            print(info['other_periodo'])
            if info['periodo'] == 'Otro':
                info['periodo'] = info['other_periodo']
            info.pop('other_periodo', None)  # Remove 'other_periodo' from cleaned_data
            bitacora = Bitacora(**info)
            
            bitacora.empresa = bitacora.job.empresa
            bitacora.ambiente = bitacora.job.ambiente
            bitacora.save()
            bitacoras = Bitacora.objects.all()
            return redirect("./bitacora/", {"bitacoras": bitacoras, "admin_perm": usuario.has_perm('AppCrud.empresa_admin')})
    else:
        formulario = BitacoraForm(user=usuario)
    return render(request, "AppCrud/bitacoraForm.html", {"formulario": formulario})

@login_required
@permission_required('AppCrud.change_bitacora', raise_exception=True)
def editarBitacora(request, id):
    bitacora=Bitacora.objects.get(id=id)
    usuario = request.user
    if (not usuario.empresa == bitacora.empresa) and not usuario.is_superuser:
        raise PermissionDenied("You do not have permission to access this page.")
    if request.method=="POST":
        form= BitacoraForm(request.POST,user=usuario)
        print(form)
        if form.is_valid():
            print("Hola")
            info=form.cleaned_data
            print("Hola")
            if info['periodo'] == 'Otro':
                info['periodo'] = info['other_periodo']
            info.pop('other_periodo', None)  # Remove 'other_periodo' from cleaned_data
            bitacora.inicio=info["inicio"]
            bitacora.job= info["job"]
            bitacora.impacto=info["impacto"]
            bitacora.periodo = info["periodo"]
            bitacora.descripcion = info["descripcion"]
            bitacora.dias = info["dias"]
            bitacora.tiempo_estimado=info["tiempo_estimado"]
            bitacora.si_cancela=info["si_cancela"]
            bitacora.empresa= bitacora.job.empresa
            bitacora.ambiente= bitacora.job.ambiente
            bitacora.save()
            bitacoras=Bitacora.objects.all()
            usuario = request.user
            return redirect('../bitacora/' ,{"bitacoras":bitacoras,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})
        pass
    else:
        formulario= BitacoraForm(initial={"empresa":bitacora.empresa, "ambiente":bitacora.ambiente, "inicio":bitacora.inicio, "job":bitacora.job,"impacto":bitacora.impacto, "tiempo_estimado":bitacora.tiempo_estimado,"si_cancela":bitacora.si_cancela,"periodo":bitacora.periodo,"dias":bitacora.dias,"descripcion":bitacora.descripcion},user=usuario)
        return render(request,"AppCrud/editarBitacora.html", {"formulario": formulario, "bitacora": bitacora})
@login_required  
@permission_required('AppCrud.delete_bitacora', raise_exception=True)
def borrarBitacora(request, id):
    bitacora=Bitacora.objects.get(id=id)
    bitacora.delete()
    bitacoras=Bitacora.objects.all()
    usuario = request.user
    return redirect('../bitacora/', {"bitacoras": bitacoras,"admin_perm":usuario.has_perm('AppCrud.empresa_admin')})

#Empresa:
@login_required
@permission_required('AppCrud.view_empresa', raise_exception=True)
def empresa(request):
    empresas=Empresa.objects.all()
    usuario = request.user
    return render(request,"AppCrud/empresa.html",{"empresas":empresas,"empresa_admin":usuario.has_perm('AppCrud.empresa_admin')})
@login_required
@permission_required('AppCrud.add_empresa', raise_exception=True)
def empresaForm(request):
    if request.method == 'POST':
        empresa_form = EmpresaVisualForm(request.POST, request.FILES)
        print(request.FILES)
        if empresa_form.is_valid():
            empresa = empresa_form.save(commit=False)
            visual_empresa = VisualEmpresa(colorPrimario=request.POST['colorPrimario'],
                                           colorSecundario=request.POST['colorSecundario'],
                                           logo=request.FILES['logo'])
            visual_empresa.save()
            empresa.visual_empresa = visual_empresa
            empresa.save()
            # Replicar registros en otras empresas 
            # Obtener la empresa "Exerom" y los registros de los servidores EPE, EDE y EQE para replicarlos a la nueva empresa
            exerom = Empresa.objects.get(nombre="Exerom")
            registros = RegistroMonitor.objects.filter(servidor__nombre__in=["EPE", "EDE", "EQE"], empresa = exerom)
            for registro in registros:
                print("Registro: ", registro.nombre)
                print("Descripcion: ", registro.descripcion)
                print("Servidor: ", registro.servidor.nombre)
                print("Empresa: ", empresa)
                RegistroMonitor.objects.create(
                    nombre=registro.nombre,
                    descripcion=registro.descripcion,
                    empresa=empresa,
                    servidor=registro.servidor
    )
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

            return redirect('./empresa/', {"empresas": empresas, "empresa_admin": usuario.has_perm('AppCrud.empresa_admin')})

    empresa_form = EmpresaVisualForm()
    return render(request, "AppCrud/empresaForm.html", {"empresa_form": empresa_form})


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
                visual_empresa = VisualEmpresa(colorPrimario=request.POST['colorPrimario'],
                                               colorSecundario=request.POST['colorSecundario'],
                                               logo=request.FILES['logo'])
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
        empresa_form = EmpresaVisualForm(initial={"nombre":empresa.nombre,"colorPrimario":empresa.visual_empresa.colorPrimario,"colorSecundario":empresa.visual_empresa.colorSecundario,"logo":empresa.visual_empresa.logo})
    return render(request, "AppCrud/editarEmpresa.html",
                  {"empresa_form": empresa_form, "empresa": empresa})

@login_required
@permission_required('AppCrud.delete_empresa', raise_exception=True)
def borrarEmpresa(request, id):
    empresa=Empresa.objects.get(id=id)
    empresa.delete()
    empresas=Empresa.objects.all()
    usuario = request.user
    return redirect('../empresa/',{"empresas":empresas,"empresa_admin":usuario.has_perm('AppCrud.empresa_admin')})

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
@permission_required('AppCrud.add_user', raise_exception=True)
def register(request):
    if request.method=="POST":
        form= RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usernm= form.cleaned_data.get("username")
            empresa= form.cleaned_data.get("empresa")

            form.save()

            user = User.objects.get(username=usernm)
            group = Group.objects.get(name=empresa)
            user.groups.add(group)
            return redirect('./inicio/', {"mensaje":f"Usuario {usernm} creado correctamente"})
        else:
            return render(request, "AppCrud/registro.html", {"form": form, "mensaje":"Error al crear el usuario","tipo":"Usuario"})
    else:
        form= RegistroUsuarioForm()
        return render(request, "AppCrud/registro.html", {"form": form,"tipo":"Usuario"})
@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def registerOption(request):
    return render (request, "AppCrud/registroOption.html")
@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def registerAdmin(request):
    if request.method=="POST":
        form= RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usernm= form.cleaned_data.get("username")
            empresa= form.cleaned_data.get("empresa")

            form.save()

            user = User.objects.get(username=usernm)
            group = Group.objects.get(name=f"{empresa}_admin")
            user.groups.add(group)
            return redirect('./inicio/', {"mensaje":f"Usuario {usernm} creado correctamente"})
        else:
            return render(request, "AppCrud/registro.html", {"form": form, "mensaje":"Error al crear el usuario","tipo":"Administrador"})
    else:
        form= RegistroUsuarioForm()
        return render(request, "AppCrud/registro.html", {"form": form,"tipo":"Administrador"})
    
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
    

def get_job_description(request):
    job_id = request.GET.get('job_id')
    job = Job.objects.get(id=job_id)
    description = job.descripcion
    return JsonResponse({'description': description})


from django.core.mail import send_mail
from django.http import HttpResponse

def enviar_correo(request):
    subject = 'last prueba'
    message = 'last prueba'
    from_email = 'exerom.eldorado.desarrollo@gmail.com'  # tu dirección de correo electrónico
    recipient_list = ['francogdimartino@gmail.com', 'franco.dimartino@exerom.com']  # lista de destinatarios

    send_mail(subject, message, from_email, recipient_list)
    return HttpResponse('Correo enviado correctamente.')

# @login_required
# def avisar(request, id):
#     print("hola")
#     job = Job.objects.get(id=id)
#     emails=[]
#     #obtener los avisos que tenga asignado ese job
#     avisos = Aviso.objects.filter(job=job)
#     #por cada aviso, obtener los contactos que tenga asignado ese aviso
#     for aviso in avisos:
#         contactos = Contacto.objects.filter(aviso=aviso)
#         #por cada contacto, obtener el email y guardarlo en la lista
#         for contacto in contactos:
#             emails.append(contacto.mail)
    
#     #enviar mail a cada email de la lista con el aviso
#     subject = 'Aviso de trabajo'
#     message = f'El trabajo {job.nombre} ha sido modificado'
#     from_email = "avisos@exerom.com"
#     recipient_list = emails

#     #send_mail(subject, message, from_email, recipient_list)
#     for mail in recipient_list:
        
#         print(f"Se envió un mail a {mail}")
#     mensaje=f"Se avisó a los contactos del trabajo {job.nombre}"
#     #redirect to inicio with mensaje in GET
#     return render (request, "AppCrud/inicio.html", {"mensaje":mensaje})

    


from django.shortcuts import render, redirect
from django.contrib import messages
        
#cambiar mail de ester por ester.west@exerom.com
def avisar(request, id):
    job = Job.objects.get(id=id)
    emails, nombres=obtener_mails_y_nombres(job)
    if len(emails)==0:
        #generate alert in template
        mensaje=f"No hay contactos asignados al trabajo {job.nombre}"
        messages.info(request, mensaje)
        return redirect('bitacora')

    if request.method == 'POST':
        form= EmailForm(request.POST)
        if form.is_valid():
            
            
            #enviar mail a cada email de la lista con el aviso
            subject = form.cleaned_data.get("asunto")
            message = form.cleaned_data.get("mensaje")
            from_email = "avisos@exerom.com"

            
        

            send_mail(subject, message, 'avisos@exerom.com', emails)
        # Redireccionar a la página de inicio con un mensaje de éxito
            messages.success(request, 'Los correos electrónicos han sido enviados.')
            
            return redirect('bitacora')

    else:
        

        print("Hola, soy el job id: ", id)
        
        #asunto en el form es el nombre del job, anteponiendo "JOB: "
        form= EmailForm(initial={'asunto': f"JOB: {job.nombre}"})
        
        paginated_bitacoras, empresas= obtener_bitacoras_paginadas(request)
        #create string with nombres separated by commas
        nombres_string=""
        for nombre in nombres:
            nombres_string+=nombre+", "
        #remove last comma
        nombres_string=nombres_string[:-2]


        usuario = request.user
        return render(request, "AppCrud/bitacora.html", {"paginated_bitacoras": paginated_bitacoras, "admin_perm": usuario.has_perm('AppCrud.empresa_admin'), "empresas": empresas, 'job': job, 'form': form, "nombres":nombres_string})


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

def obtener_mails_y_nombres(job):
    emails=[]
    nombres=[]
    #obtener los avisos que tenga asignado ese job
    avisos = Aviso.objects.filter(job=job)
    #por cada aviso, obtener los contactos que tenga asignado ese aviso
    for aviso in avisos:
        contactos = Contacto.objects.filter(aviso=aviso)
        #por cada contacto, obtener el email y guardarlo en la lista
        for contacto in contactos:
            emails.append(contacto.mail)
            nombres.append(contacto.nombre)
    return(emails, nombres)


def servidor(request):
    usuario = request.user
    empresa = Empresa.objects.get(nombre=usuario.empresa.nombre)
    servidores = Servidor.objects.filter(empresa=empresa)
    return render(request, "AppCrud/ABMservidor.html", {"servidores": servidores, "usuario":usuario , 'empresa':empresa})
    # return render(request, "AppCrud/ABMservidor.html", {"servidores": servidores, "admin_perm": usuario.has_perm('AppCrud.empresa_admin')})
    
def registro(request):
    usuario = request.user
    empresa = Empresa.objects.get(nombre=usuario.empresa.nombre)
    registros = RegistroMonitor.objects.filter(empresa=empresa)
    return render(request, "AppCrud/ABMregistro.html", {"registros": registros, "usuario":usuario ,  'empresa':empresa})

def altaServidor(request, empresa_id):
    usuario = request.user
    empresa = Empresa.objects.get(id=empresa_id)
    print ("Empresa")
    print(empresa)
    if request.method == "POST":
        form = ServidorForm(request.POST)
        if form.is_valid():
            form.instance.nombre = request.POST['nombre']  # Asigna nombre del formulario
            form.instance.empresa = empresa 
            form.save()
            return redirect('servidor')  # Asegúrate de tener esta vista creada
    else:
        form = ServidorForm()
    return render(request, "AppCrud/altaServidor.html", {"empresa": empresa, "usuario":usuario , "form":form})

def eliminarServidor(request, empresa_id, servidor_id):
    usuario = request.user
    servidor = Servidor.objects.get(id=servidor_id , empresa_id=empresa_id)
    servidor.delete()
    return redirect('servidor')


# def altaRegistroMonitor(request, empresa_id):
#     usuario = request.user
#     empresa = Empresa.objects.get(id=empresa_id)
#     if request.method == "POST":
#         form = RegistroMonitorForm(request.POST)
#         if form.is_valid():
#             form.instance.nombre = request.POST['nombre']
#             form.instance.descripcion = request.POST['descripcion']
#             form.instance.empresa = empresa 
#             servidor = request.POST['servidor']
#             form.instance.servidor = Servidor.objects.get(id=servidor)
#             form.save()
#             return redirect('registro')  # Asegúrate de tener esta vista creada
#     else:
#         form = RegistroMonitorForm()
#     return render(request, "AppCrud/altaRegistroMonitor.html", {"empresa": empresa, "usuario":usuario , "form":form})

def altaRegistroMonitor(request, empresa_id):
    usuario = request.user
    empresa = Empresa.objects.get(id=empresa_id)
    
    if request.method == "POST":
        form = RegistroMonitorForm(request.POST)
        if form.is_valid():
            nombre = request.POST['nombre']
            descripcion = request.POST['descripcion']
            servidor_id = request.POST['servidor']
            servidor = Servidor.objects.get(id=servidor_id)
            
            # Crear el registro original
            registro = form.save(commit=False)
            registro.nombre = nombre
            registro.descripcion = descripcion
            registro.empresa = empresa
            registro.servidor = servidor
            registro.save()
            print("servidor", servidor.nombre)
            # Si el servidor se llama 'ede', 'eqe' o 'epe', replicar en otras empresas
            if servidor.nombre in ['EDE', 'EQE', 'EPE']:
                otras_empresas = Empresa.objects.exclude(id=empresa.id)
                print(otras_empresas)
                for otra_empresa in otras_empresas:
                    try:
                        # servidor_otro = Servidor.objects.get(nombre=servidor.nombre, empresa=otra_empresa)
                        RegistroMonitor.objects.create(
                            nombre=nombre,
                            descripcion=descripcion,
                            empresa=otra_empresa,
                            servidor=servidor
                        )
                    except Servidor.DoesNotExist:
                        # Si la otra empresa no tiene un servidor con ese nombre, simplemente lo ignoramos
                        continue

            return redirect('registro')  # Redirigir después del guardado

    else:
        form = RegistroMonitorForm()

    return render(request, "AppCrud/altaRegistroMonitor.html", {
        "empresa": empresa,
        "usuario": usuario,
        "form": form
    })


def eliminarRegistroMonitor(request, empresa_id, registro_id):
    usuario = request.user
    registro = RegistroMonitor.objects.get(id=registro_id , empresa_id=empresa_id)
    registro.delete()
    return redirect('registro')


def obtener_fecha(request):
    hoy = now().date()
    return redirect('monitoreo', hoy=hoy)


def cambiarFechaMonitor(request):
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    
    print("El mes:", mes)
    print("El anio:", anio)

    # Crear la nueva fecha con el primer día del mes
    nueva_fecha = date(anio, mes, 1)
    
    print("La nueva fecha:", nueva_fecha)

    return redirect('monitoreo', hoy=nueva_fecha.strftime("%Y-%m-%d"))
    

def monitoreo(request, hoy):
    usuario = request.user
    empresa = Empresa.objects.get(nombre=usuario.empresa.nombre)

    # 🔹 Servidores de la empresa + los servidores fijos ("EPE", "EQE", "EDE")
    # servidores_fijos = ["EPE", "EQE", "EDE"]
    # servidores_fijos_ids = list(Servidor.objects.filter(nombre__in=servidores_fijos).values_list("id", flat=True))
    # servidores_empresa = list(Servidor.objects.filter(empresa=empresa).values_list("nombre", flat=True))
    # servidores_todos = set(servidores_empresa)  # Asegurar que estén todos

    servidores_fijos = ["EPE", "EQE", "EDE"]
    servidores_fijos_ids = list(Servidor.objects.filter(nombre__in=servidores_fijos).values_list("id", flat=True))
    # servidores_empresa_ids = list(Servidor.objects.filter(empresa=empresa).values_list("id", flat=True))
    servidores_empresa_ids = list(
        Servidor.objects.filter(empresa=empresa).exclude(nombre__in=servidores_fijos).values_list("id", flat=True)
    )

    # 🔹 Registros de la empresa
    registros_empresa = RegistroMonitor.objects.filter(servidor_id__in=servidores_empresa_ids)

    # 🔹 Registros de los servidores fijos (aunque no sean de la empresa)
    registros_fijos = RegistroMonitor.objects.filter(servidor_id__in=servidores_fijos_ids, empresa_id = empresa.id)

    # 🔹 Unión de todos los registros
    registros = registros_empresa | registros_fijos
    registros = registros.select_related('servidor')

    # 🔹 Conjuntos de nombres de servidores para asegurar la visualización
    servidores_todos = set(registros.values_list("servidor__nombre", flat=True))

    hoy = datetime.strptime(hoy, "%Y-%m-%d").date()
    primer_dia = hoy.replace(day=1)
    ultimo_dia = (primer_dia + relativedelta(months=1)) - timedelta(days=1)

    dias_mes = [
        dia for dia in (primer_dia + timedelta(days=i) for i in range((ultimo_dia - primer_dia).days + 1))
    ]

    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

    dias_semana = [dia.strftime('%A')[0].upper() for dia in dias_mes]

    # registros = RegistroMonitor.objects.filter(servidor__nombre__in=servidores_todos)  # 📌 Solo los servidores requeridos
    estados = Estado.objects.filter(fecha__range=(primer_dia, ultimo_dia)).select_related('registro_verificado')

    estados_dict = defaultdict(dict)
    for estado in estados:
        estados_dict[estado.registro_verificado.id][estado.fecha] = estado

    # 📌 Inicializar estructura asegurando que "EPE", "EQE" y "EDE" están presentes
    registros_por_servidor = {servidor: [] for servidor in servidores_todos}

    for registro in registros:
        servidor_nombre = registro.servidor.nombre
        fila = {
            "registro": registro,
            "estados": [estados_dict[registro.id].get(dia, None) for dia in dias_mes]
        }
        registros_por_servidor[servidor_nombre].append(fila)

    # Ordenar por nombre de servidor
    registros_por_servidor = dict(sorted(registros_por_servidor.items()))

    dias_no_modificables = [dia.weekday() in [5, 6] for dia in dias_mes]

    mes_anterior = (primer_dia - relativedelta(months=1)).month
    anio_anterior = (primer_dia - relativedelta(months=1)).year
    mes_siguiente = (primer_dia + relativedelta(months=1)).month
    anio_siguiente = (primer_dia + relativedelta(months=1)).year
    
    mes = hoy.month
    anio = hoy.year

    return render(request, "AppCrud/monitoreo.html", {
        "registros_por_servidor": registros_por_servidor,  # Pasamos el diccionario ordenado
        "dias_mes": dias_mes,
        "dias_semana": dias_semana,
        "dias_no_modificables": dias_no_modificables,
        "mes": mes,
        "anio": anio,
        "mes_anterior": mes_anterior,
        "anio_anterior": anio_anterior,
        "mes_siguiente": mes_siguiente,
        "anio_siguiente": anio_siguiente,
        "empresa": empresa,
    })

def registrarEstado(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Cargar los datos JSON enviados desde fetch
            registro_id = data.get("registro_id")
            fecha = data.get("fecha")
            verificacion = data.get("tipo_verificacion")
            # descripcion = data.get("descripcion", "")  # Puede venir vacío
            
            print(verificacion)
            print(registro_id)
            print(fecha)
            # print(descripcion)


            # Verificar si el estado ya existe y lo modifico
            estado = Estado.objects.filter(registro_verificado_id=registro_id, fecha=fecha).first()
            # print(f"Registro ID: {registro_id}, Fecha: {fecha}, Verificación: {verificacion}, Descripción: {estado.descripcion}")
            if estado is not None:
                estado.fecha = fecha
                estado.tipo_verificacion = verificacion
                estado.descripcion = estado.descripcion
                estado.save()
            else:
                # descripcion = data.get("descripcion", "")
                # Si el estado no existe, crearlo
                estado_nuevo = Estado.objects.create(
                    registro_verificado=RegistroMonitor.objects.get(id=registro_id),
                    tipo_verificacion=verificacion,
                    fecha=fecha,
                    # descripcion=descripcion
                )
                estado_nuevo.save()

            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

def registrarDescripcion(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Cargar los datos JSON enviados desde fetch
            registro_id = data.get("registro_id")
            fecha = data.get("fecha")
            descripcion = data.get("descripcion")

            print(f"Registro ID: {registro_id}, Fecha: {fecha}, Descripción: {descripcion}")

            # Verificar si el estado ya existe y lo modifico
            estado = Estado.objects.filter(registro_verificado_id=registro_id, fecha=fecha).first()
            if estado is not None:
                estado.descripcion = descripcion
                estado.save()
            else:
                estado_nuevo = Estado.objects.create(
                    registro_verificado=RegistroMonitor.objects.get(id=registro_id),
                    tipo_verificacion='desconocido',
                    descripcion=descripcion,
                    fecha=fecha
                )
                estado_nuevo.save()

            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    # return JsonResponse({"success": False, "error": "Método no permitido"})
    return redirect('monitoreo')


def imprimirRegistroMes(request, mes, anio, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    registros = RegistroMonitor.objects.filter(empresa=empresa)
    registros_especiales = RegistroMonitor.objects.filter(servidor__nombre__in=["EPE", "EQE", "EDE"])
    registros = registros | registros_especiales

    estados = Estado.objects.filter(
        registro_verificado__in=registros,
        fecha__year=anio,
        fecha__month=mes
    ).select_related('registro_verificado', 'registro_verificado__servidor')

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

    data = [["Registro", "Descripción", "Servidor", "Comentario", "Estado", "Fecha"]]

    for estado in estados:
        data.append([
            Paragraph(estado.registro_verificado.nombre if estado.registro_verificado.nombre else "", styleN),
            Paragraph(estado.registro_verificado.descripcion if estado.registro_verificado.descripcion else "", styleN),
            Paragraph(estado.registro_verificado.servidor.nombre if estado.registro_verificado.servidor.nombre else "", styleN),
            Paragraph(estado.descripcion if estado.descripcion else "", styleN),
            Paragraph(estado.tipo_verificacion.capitalize() if estado.tipo_verificacion else "", styleN),
            Paragraph(estado.fecha.strftime("%d-%m-%Y") if estado.fecha else "", styleN),
        ])

    table = Table(data, colWidths=[80, 250, 80, 200, 80, 80])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elements = [table]
    pdf.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Registro_{mes}_{anio}.pdf")