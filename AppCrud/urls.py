from django.urls import path
from AppCrud import views
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
    
    path('registro/', registro, name='registro'),
    path('servidor/', servidor, name='servidor'),
    path('altaServidor/<int:empresa_id>', altaServidor, name='altaServidor'),
    path('eliminarServidor/<int:empresa_id> ,<int:servidor_id>', eliminarServidor, name='eliminarServidor'),
    
    path('altaRegistroMonitor/<int:empresa_id>', altaRegistroMonitor, name='altaRegistroMonitor'),
    path('eliminarRegistroMonitor/<int:empresa_id>,<int:registro_id>', eliminarRegistroMonitor, name='eliminarRegistroMonitor'),
    
    path('monitoreo/<str:hoy>/', monitoreo, name='monitoreo'),
    path('registrarEstado/', views.registrarEstado, name='registrarEstado'),
    path('registrarDescripcion/', views.registrarDescripcion, name='registrarDescripcion'),
    path('obtener_fecha/', views.obtener_fecha, name='obtener_fecha'),
    path('cambiarFechaMonitor/', views.cambiarFechaMonitor, name='cambiarFechaMonitor'),
    
    # path('imprimirRegistroMes/<str:mes>/<str:anio>/<int:empresa_id>', imprimirRegistroMes, name='imprimirRegistroMes'),
    path('imprimirRegistroMes/<int:mes>/<int:anio>/<int:empresa_id>/', imprimirRegistroMes, name="imprimirRegistroMes"),
]