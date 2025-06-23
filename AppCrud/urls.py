from django.urls import path
from AppCrud.views import *
from django.contrib.auth.views import LogoutView
 

urlpatterns = [
    path('', inicio),
    path('inicio/', inicio,name="inicio"),
    path('job/', job,name="job"),
    path('jobForm', jobForm, name="JobForm"),
    path('editarJob/<id>', editarJob, name="editarJob"),
    path('borrarJob/<id>', borrarJob, name="borrarJob"),

    path('aviso/', aviso,name="aviso"),
    path('avisoForm', avisoForm, name="AvisoForm"),
    path('editarAviso/<id>', editarAviso, name="editarAviso"),
    path('borrarAviso/<id>', borrarAviso, name="borrarAviso"),

    path('contacto/', contacto,name="contacto"),
    path('contactoForm', contactoForm, name="ContactoForm"),
    path('editarContacto/<id>', editarContacto, name="editarContacto"),
    path('borrarContacto/<id>', borrarContacto, name="borrarContacto"),

    path('bitacora/', bitacora,name='bitacora'),
    path('bitacoraForm', bitacoraForm, name="BitacoraForm"),
    path('editarBitacora/<id>', editarBitacora, name="editarBitacora"),
    path('borrarBitacora/<id>', borrarBitacora, name="borrarBitacora"),

    path('empresa/', empresa,name='empresa'),
    path('empresaForm', empresaForm, name="EmpresaForm"),
    path('editarEmpresa/<id>', editarEmpresa, name="editarEmpresa"),
    path('borrarEmpresa/<id>', borrarEmpresa, name="borrarEmpresa"),

    path('login/', login_request, name="Login"),
    path('register', register, name='Register'),
    path('registerOption', registerOption, name='RegisterOption'),
    path('registerAdmin', registerAdmin, name='RegisterAdmin'),
    path('logout', LogoutView.as_view(template_name='AppCrud/logout.html'), name='Logout'),
    path('editarPerfil', editarPerfil, name="EditarPerfil"), 
    path('get_job_description/', get_job_description, name='get_job_description'),

    path('avisar/<id>', avisar, name='avisar'),
    
    path('transacciones', transacciones, name='transacciones'),
    path('registroForm/', registroForm, name="RegistroForm"),
    path('registro/borrar/<int:id>/', borrarRegistro, name='borrar_registro'),
    
    path('servidores/', servidores, name='servidores'),
    path('servidorForm/', servidorForm, name='ServidorForm'),
    path('servidor/borrar/<int:id>/', borrarServidor, name='borrar_servidor'),
    path('servidor/<int:servidor_id>/quitar_registro/<int:registro_id>/', quitar_registro_servidor, name='quitar_registro_servidor'),
    path('servidores/editar/<int:servidor_id>/', editar_servidor, name='editarServidor'),
    
    path('cambiar_usuario/', cambiar_usuario, name='cambiar_usuario'),
    path('logout/', logout_request, name='Logout'),
    
    path('monitoreo/<str:hoy>/', monitoreo, name='monitoreo'),
    path('monitoreo_admin/<str:hoy>/', monitoreo_admin, name='monitoreo_admin'),
    path('obtener_fecha_monitor_admin/', obtener_fecha_monitor_admin, name='obtener_fecha_monitor_admin'),
    path('obtener_fecha/', obtener_fecha, name='obtener_fecha'),
    
    
    path('registrarEstado/', registrarEstado, name='registrarEstado'),
    path('registrarDescripcion/', registrarDescripcion, name='registrarDescripcion'),
    path('imprimirRegistroMes/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMes, name="imprimirRegistroMes"),
    path('cambiar_usuario/', cambiar_usuario, name='cambiar_usuario'),
    path('cambiarFechaMonitor/',cambiarFechaMonitor, name='cambiarFechaMonitor'),
    
    path('imprimirRegistroMesCompleto/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMesCompleto, name="imprimirRegistroMesCompleto"),
    path('habilitar_deshabilitar_edicion_admin/', habilitar_deshabilitar_edicion_admin, name='habilitar_deshabilitar_edicion_admin'),
        path('habilitar_deshabilitar_edicion_otros/', habilitar_deshabilitar_edicion_otros, name='habilitar_deshabilitar_edicion_otros'),
    
    path('usuarios/', lista_usuarios, name='usuarios'),
    path('administradores/', lista_administradores, name='administradores'),
]