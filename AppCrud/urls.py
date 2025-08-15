from django.urls import path
from AppCrud.views import *
from AppCrud.views.usuario_views import google_login, google_callback
from django.contrib.auth.views import LogoutView
 

urlpatterns = [
    
    # INICIO Y DESLOGUEO - Cambiar la URL raíz para que vaya directo al login
    path('', login_request, name="home"),  # Cambio aquí
    path('inicio/', inicio, name="inicio"),
    path('login/', login_request, name="Login"),
    path('auth/google/', google_login, name='google_login'),
    path('auth/google/callback/', google_callback, name='google_callback'),
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
    path('exportar_avisos_pdf/', exportar_avisos_pdf, name='exportar_avisos_pdf'),

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
    path('registerOption', registerOption, name='RegisterOption'),
    path('registerAdmin', registerAdmin, name='RegisterAdmin'),
    path('editarPerfil', editarPerfil, name="EditarPerfil"), 
    path('cambiar_empresa/', cambiar_empresa, name='cambiar_empresa'),
    path('usuarios/', lista_usuarios, name='usuarios'),
    path('usuarios/editar/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('lista_administradores_empresa/<int:empresa_id>/', listaAdministradoresEmpresa, name='listaAdministradoresEmpresa'),
    path('RegistrarUsuario', RegistrarUsuario, name='RegistrarUsuario'),
    
    # ADMINISTRADORES MULTI-EMPRESA
    path('administradores_multi_empresa/', listaAdministradoresMultiEmpresa, name='listaAdministradoresMultiEmpresa'),
    path('admin_multi_empresa/editar/<int:admin_id>/', editarAdminMultiEmpresa, name='editarAdminMultiEmpresa'),
    path('admin_multi_empresa/ver/<int:admin_id>/', detallesAdminMultiEmpresa, name='detallesAdminMultiEmpresa'),
    
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
    path('obtener_fecha/', obtener_fecha, name='obtener_fecha'),
    path('registrarEstado/', registrarEstado, name='registrarEstado'),
    path('registrarDescripcion/', registrarDescripcion, name='registrarDescripcion'),
    path('obtener_comentarios/', obtener_comentarios, name='obtener_comentarios'),
    path('imprimirRegistroMes/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMes, name="imprimirRegistroMes"),
    path('cambiarSemanaMonitor/',cambiarSemanaMonitor, name='cambiarSemanaMonitor'),
    path('cambiarMesMonitor/',cambiarMesMonitor,name='cambiarMesMonitor'),
    path('imprimirRegistroMesCompleto/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMesCompleto, name="imprimirRegistroMesCompleto"),
    path('imprimirRegistroDia/<int:empresa_id>/', imprimirRegistroDia, name='imprimirRegistroDia'),
    path('habilitar_deshabilitar_edicion/', habilitar_deshabilitar_edicion, name='habilitar_deshabilitar_edicion'),
    
]