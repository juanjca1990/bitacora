from .base_imports import *


def inicio(request):
    mensaje = request.GET.get('mensaje', '')
    user = request.user
    admin = 0
    print("Usuario:", user)
    
    # Determinar si el usuario puede cambiar de empresa
    if user.is_authenticated:
        if user.is_superuser:
            # Los superusuarios pueden cambiar entre todas las empresas
            admin = 1
            request.session['admin'] = True
            request.session["bloquear_edicion"] = True
        elif hasattr(user, 'empresas_administradas') and user.empresas_administradas.exists():
            # Los usuarios que administran empresas pueden cambiar entre ellas
            admin = 1
            request.session['admin'] = True
            request.session["bloquear_edicion"] = True
        else:
            # Usuarios regulares no pueden cambiar de empresa
            request.session['admin'] = False
            request.session["bloquear_edicion"] = True
    else:
        request.session['admin'] = False
        request.session["bloquear_edicion"] = True

    return render(request, "AppCrud/inicio.html", {"mensaje": mensaje, "admin": admin})

def get_job_description(request):
    job_id = request.GET.get('job_id')
    job = Job.objects.get(id=job_id)
    description = job.descripcion
    return JsonResponse({'description': description})

def enviar_correo(request):
    subject = 'last prueba'
    message = 'last prueba'
    from_email = 'exerom.eldorado.desarrollo@gmail.com'  # tu dirección de correo electrónico
    recipient_list = ['francogdimartino@gmail.com', 'franco.dimartino@exerom.com']  # lista de destinatarios

    send_mail(subject, message, from_email, recipient_list)
    return JsonResponse({'message': 'Correo enviado correctamente.'})
