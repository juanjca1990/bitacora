from .base_imports import *


def inicio(request):
    mensaje = request.GET.get('mensaje', '')
    user = request.user
    admin = 0
    print("Usuario:", user)
    if user.is_superuser or request.session.get('admin', True):
        admin = 1
        request.session['admin'] = True  # Add 'admin' to session storage
        request.session["bloquear_edicion"] = True
    else:
        request.session['admin'] = False  # Ensure 'admin' is False for non-staff users
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
