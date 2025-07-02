# Este archivo ha sido reestructurado por módulos.
# Todas las vistas ahora están organizadas en archivos separados dentro del directorio 'views/'
# 
# Estructura:
# - views/inicio_views.py: Vista de inicio y funciones utilitarias
# - views/job_views.py: Gestión de trabajos/jobs
# - views/contacto_views.py: Gestión de contactos
# - views/aviso_views.py: Gestión de avisos
# - views/bitacora_views.py: Gestión de bitácoras
# - views/empresa_views.py: Gestión de empresas
# - views/usuario_views.py: Gestión de usuarios y autenticación
# - views/transacciones_views.py: Gestión de transacciones/registros
# - views/servidores_views.py: Gestión de servidores
# - views/monitoreo_views.py: Sistema de monitoreo y reportes
# - views/base_imports.py: Importaciones compartidas
#
# Todas las vistas se importan automáticamente desde views/__init__.py

# Para mantener compatibilidad, importamos todas las vistas desde el paquete views
from .views import *
