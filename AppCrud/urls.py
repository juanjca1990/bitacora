from django.urls import path
from AppCrud.views import *
from django.contrib.auth.views import LogoutView
 

urlpatterns = [
    
    # INICIO Y DESLOGUEO
    path('', inicio),
    path('inicio/', inicio,name="inicio"),
    path('login/', login_request, name="Login"),
    path('logout', LogoutView.as_view(template_name='AppCrud/logout.html'), name='Logout'),
    path('logout/', logout_request, name='Logout'),
    
    # JOBS
    path('job/', job,name="job"),
    path('jobForm', jobForm, name="JobForm"),
    path('editarJob/<id>', editarJob, name="editarJob"),
    path('borrarJob/<id>', borrarJob, name="borrarJob"),
    path('get_job_description/', get_job_description, name='get_job_description'),

    # AVISOS
    path('aviso/', aviso,name="aviso"),
    path('avisoForm', avisoForm, name="AvisoForm"),
    path('editarAviso/<id>', editarAviso, name="editarAviso"),
    path('borrarAviso/<id>', borrarAviso, name="borrarAviso"),
    path('avisar/<id>', avisar, name='avisar'),

    # CONTACTOS
    path('contacto/', contacto,name="contacto"),
    path('contactoForm', contactoForm, name="ContactoForm"),
    path('editarContacto/<id>', editarContacto, name="editarContacto"),
    path('borrarContacto/<id>', borrarContacto, name="borrarContacto"),

    # BITACORA
    path('bitacora/', bitacora,name='bitacora'),
    path('bitacoraForm', bitacoraForm, name="BitacoraForm"),
    path('editarBitacora/<id>', editarBitacora, name="editarBitacora"),
    path('borrarBitacora/<id>', borrarBitacora, name="borrarBitacora"),

    # EMPRESA
    path('empresa/', empresa,name='empresa'),
    path('empresa_otros/', empresa_otros, name='empresa_otros'),
    path('editarEmpresa_otros/<id>', editarEmpresa_otros, name='editarEmpresa_otros'),
    path('empresaForm', empresaForm, name="EmpresaForm"),
    path('editarEmpresa/<id>', editarEmpresa, name="editarEmpresa"),
    path('borrarEmpresa/<id>', borrarEmpresa, name="borrarEmpresa"),

    # USUARIOS
    path('register', register, name='Register'),
    path('registerOption', registerOption, name='RegisterOption'),
    path('registerAdmin', registerAdmin, name='RegisterAdmin'),
    path('editarPerfil', editarPerfil, name="EditarPerfil"), 
    path('cambiar_usuario/', cambiar_usuario, name='cambiar_usuario'),
    path('usuarios/', lista_usuarios, name='usuarios'),
    path('administradores/', lista_administradores, name='administradores'),
    path('lista_usuarios_empresa/<int:empresa_id>/', lista_usuarios_empresa, name='lista_usuarios_empresa'),
    path('lista_administradores_empresa/<int:empresa_id>/', lista_administradores_empresa, name='lista_administradores_empresa'),
    path('register_user_vista_admin/<int:empresa_id>/', register_user_vista_admin, name='Register_user_vista_admin'),
    
    # TRANSACCIONES
    path('transacciones', transacciones, name='transacciones'),
    path('registroForm/', registroForm, name="RegistroForm"),
    path('registro/borrar/<int:id>/', borrarRegistro, name='borrar_registro'),
    
    # SERVIDORES
    path('servidores/', servidores, name='servidores'),
    path('servidorForm/', servidorForm, name='ServidorForm'),
    path('servidor/borrar/<int:id>/', borrarServidor, name='borrar_servidor'),
    path('servidor/<int:servidor_id>/quitar_registro/<int:registro_id>/', quitar_registro_servidor, name='quitar_registro_servidor'),
    path('servidores/editar/<int:servidor_id>/', editar_servidor, name='editarServidor'),
    
    # MONITOREO
    path('monitoreo/<str:hoy>/', monitoreo, name='monitoreo'),
    path('monitoreo_admin/<str:hoy>/', monitoreo_admin, name='monitoreo_admin'),
    path('obtener_fecha_monitor_admin/', obtener_fecha_monitor_admin, name='obtener_fecha_monitor_admin'),
    path('obtener_fecha/', obtener_fecha, name='obtener_fecha'),
    path('registrarEstado/', registrarEstado, name='registrarEstado'),
    path('registrarDescripcion/', registrarDescripcion, name='registrarDescripcion'),
    path('imprimirRegistroMes/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMes, name="imprimirRegistroMes"),
    path('cambiarFechaMonitor_admin/',cambiarFechaMonitor_admin, name='cambiarFechaMonitor_admin'),
    path('cambiarFechaMonitor_otros/',cambiarFechaMonitor_otros, name='cambiarFechaMonitor_otros'),
    path('cambiarSemanaMonitor_admin/',cambiarSemanaMonitor_admin, name='cambiarSemanaMonitor_admin'),
    path('cambiarSemanaMonitor_otros/',cambiarSemanaMonitor_otros, name='cambiarSemanaMonitor_otros'),
    path('cambiarMesMonitor_admin/',cambiarMesMonitor_admin, name='cambiarMesMonitor_admin'),
    path('cambiarMesMonitor_otros/',cambiarMesMonitor_otros, name='cambiarMesMonitor_otros'),
    path('imprimirRegistroMesCompleto/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMesCompleto, name="imprimirRegistroMesCompleto"),
    path('habilitar_deshabilitar_edicion_admin/', habilitar_deshabilitar_edicion_admin, name='habilitar_deshabilitar_edicion_admin'),
    path('habilitar_deshabilitar_edicion_otros/', habilitar_deshabilitar_edicion_otros, name='habilitar_deshabilitar_edicion_otros'),
    
]