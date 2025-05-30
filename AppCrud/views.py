from django.http import JsonResponse
from django.shortcuts import render, redirect
from AppCrud.models import Job, Contacto, Aviso, Bitacora, Empresa, Registro,Servidor, User, VisualEmpresa
from AppCrud.forms import JobForm, EmailForm, ContactoForm, AvisoForm, BitacoraForm, RegistroForm,RegistroUsuarioForm, ServidorForm, UserEditForm, EmpresaVisualForm

from django.core.paginator import Paginator

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import login , get_user_model



def inicio(request):
    mensaje = request.GET.get('mensaje', '')
    user = request.user
    admin = 0

    if user.is_staff or user.is_superuser:
        admin = 1
        request.session['admin'] = True  # Add 'admin' to session storage
    else:
        request.session['admin'] = False  # Ensure 'admin' is False for non-staff users

    return render(request, "AppCrud/inicio.html", {"mensaje": mensaje, "admin": admin})

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
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            usernm = form.cleaned_data.get("username")
            empresa = form.cleaned_data.get("empresa")

            # Asignar empresa solo si no es superusuario
            if not user.is_superuser:
                user.empresa = empresa

            user.save()

            # Asignar grupo según la empresa
            if empresa:
                group = Group.objects.get(name=empresa)
                user.groups.add(group)

            return redirect('./inicio/', {"mensaje": f"Usuario {usernm} creado correctamente"})
        else:
            return render(request, "AppCrud/registrarUsuario.html", {"form": form, "mensaje": "Error al crear el usuario", "tipo": "Usuario"})
    else:
        form = RegistroUsuarioForm()
        return render(request, "AppCrud/registrarUsuario.html", {"form": form, "tipo": "Usuario"})

@login_required
@permission_required('AppCrud.add_user', raise_exception=True)
def registerOption(request):
    return render (request, "AppCrud/registroUserOpcion.html")
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
            return render(request, "AppCrud/registrarUsuario.html", {"form": form, "mensaje":"Error al crear el usuario","tipo":"Administrador"})
    else:
        form= RegistroUsuarioForm()
        return render(request, "AppCrud/registrarUsuario.html", {"form": form,"tipo":"Administrador"})
    
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


def registros(request):
    registros = Registro.objects.all()
    return render(request, "AppCrud/registros.html", {"registros": registros})


def registroForm(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            registro = Registro(nombre=form.cleaned_data.get("nombre"),
                               descripcion=form.cleaned_data.get("descripcion"))
            registro.save()
            return redirect('registros')
    else:
        form = RegistroForm()
    return render(request, "AppCrud/registroForm.html", {"formulario": form})


def borrarRegistro(request, id):
    registro = Registro.objects.get(id=id)
    registro.delete()
    return redirect('registros')

@login_required
# @permission_required('AppCrud.view_servidor', raise_exception=True)
def servidores(request):
    empresa = request.user.empresa
    servidores = Servidor.objects.filter(empresa=empresa)
    servidores_con_registros = []
    for servidor in servidores:
        registros = Registro.objects.filter(servidor=servidor)
        servidores_con_registros.append({
            'servidor': servidor,
            'registros': registros
        })
    return render(request, "AppCrud/servidores.html", {"servidores_con_registros": servidores_con_registros})

@login_required
# @permission_required('AppCrud.add_servidor', raise_exception=True)
def servidorForm(request):
    if request.method == 'POST':
        form = ServidorForm(request.POST)
        if form.is_valid():
            servidor = form.save(commit=False)
            servidor.empresa = request.user.empresa  # Asigna la empresa del usuario
            servidor.save()
            form.save_m2m()
            return redirect('servidores')
    else:
        form = ServidorForm()
    return render(request, "AppCrud/servidorForm.html", {"formulario": form})

@login_required
# @permission_required('AppCrud.delete_servidor', raise_exception=True)
def borrarServidor(request, id):
    servidor = Servidor.objects.get(id=id)
    servidor.delete()
    return redirect('servidores')

@login_required
def quitar_registro_servidor(request, servidor_id, registro_id):
    servidor = Servidor.objects.get(id=servidor_id)
    registro = Registro.objects.get(id=registro_id)
    servidor.registos.remove(registro)
    return redirect('servidores')


@login_required
def editar_servidor(request, servidor_id):
    servidor = Servidor.objects.get(id=servidor_id)
    if request.method == 'POST':
        form = ServidorForm(request.POST, instance=servidor)
        if form.is_valid():
            form.save()
            return redirect('servidores')  # Cambia 'servidores' por el nombre de tu vista de lista
    else:
        form = ServidorForm(instance=servidor)
    return render(request, 'AppCrud/editarServidor.html', {'form': form, 'servidor': servidor})


@login_required
def cambiar_usuario(request):
    User = get_user_model()
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        print("el usuario es : ",user_id)
        try:
            nuevo_usuario = User.objects.get(id=user_id)
            login(request, nuevo_usuario)
            request.session['admin'] = True
        except User.DoesNotExist:
            pass
    # return redirect('inicio') 
    admin = 1
    # users = lista_usuarios(request)  # Pass the request argument here
    return render(request, "AppCrud/inicio.html", {
        "admin": admin, 
        'users': User.objects.all() # Pass the dictionary of users
    })
    

@login_required
def logout_request(request):
    logout(request)
    return redirect('Login')