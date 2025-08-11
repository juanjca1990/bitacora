from AppCrud.models import Estado, Registro, Servidor, Empresa
from datetime import datetime
import os
from dotenv import load_dotenv
from paramiko import SSHClient, AutoAddPolicy
import psycopg2

def registrar_estado_tool(registro_id: int, fecha: str, tipo_verificacion: str, servidor_id: int, empresa_id: int) -> str:
    """
    Crea o actualiza un Estado en la base de datos.

    Parámetros:
        registro_id (int): ID del registro.
        fecha (str): Fecha en formato 'YYYY-MM-DD'.
        tipo_verificacion (str): Estado de verificación ('bien', 'fallo', etc).
        servidor_id (int): ID del servidor.
        empresa_id (int): ID de la empresa.

    Retorna:
        str: Mensaje de éxito o error.
    """
    try:
        registro = Registro.objects.get(id=registro_id)
        servidor = Servidor.objects.get(id=servidor_id)
        empresa = Empresa.objects.get(id=empresa_id)
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

        estado, created = Estado.objects.get_or_create(
            registro_verificado=registro,
            servidor=servidor,
            empresa=empresa,
            fecha=fecha_obj,
            defaults={
                'tipo_verificacion': tipo_verificacion,
                'descripcion': ''
            }
        )
        if not created:
            estado.tipo_verificacion = tipo_verificacion
            estado.save()
        return "Estado registrado o actualizado correctamente."
    except Exception as e:
        return f"Error: {str(e)}"

def insert_transaction(nombre: str, descripcion: str) -> str:
    """
    Inserta una nueva transacción o registro en la base de datos.

    Parámetros:
        nombre (str): El nombre de la transacción.
        descripcion (str): Una descripción detallada de la transacción.

    Retorna:
        str: Mensaje de confirmación con el nombre y la descripción de la transacción registrada.
    """
    registro = Registro(nombre=nombre, descripcion=descripcion)
    print(f'Insertando transacción: {registro.nombre} - {registro.descripcion}')
    registro.save()
    return f'Transacción insertada: {registro.nombre} - {registro.descripcion}'

def delete_transaction(nombre: str) -> str:
    """
    Elimina una transacción de la base de datos según el nombre.

    Parámetros:
        nombre (str): El nombre exacto de la transacción a eliminar.

    Retorna:
        str: Mensaje de confirmación o error si no existe.
    """
    try:
        registro = Registro.objects.get(nombre=nombre)
        print(f'Eliminando transacción: {registro.nombre}')
        registro.delete()
        return f'Transacción eliminada: {nombre}'
    except Registro.DoesNotExist:
        return f'No se encontró una transacción con el nombre: {nombre}'

def list_empresas() -> str:
    """
    Lista todas las empresas disponibles en el sistema.

    Retorna:
        str: Un listado con los nombres y IDs de las empresas.
    """
    empresas = Empresa.objects.all()
    if not empresas:
        return "No hay empresas registradas."
    resultado = "Empresas disponibles:\n"
    for empresa in empresas:
        resultado += f"- {empresa.id}: {empresa.nombre}\n"
    return resultado

def list_servidores() -> str:
    """
    Lista todos los servidores disponibles en el sistema.

    Retorna:
        str: Un listado con los nombres y IDs de los servidores.
    """
    servidores = Servidor.objects.all()
    if not servidores:
        return "No hay servidores registrados."
    resultado = "Servidores disponibles:\n"
    for servidor in servidores:
        resultado += f"- {servidor.id}: {servidor.nombre}\n"
    return resultado

def list_registros() -> str:
    """
    Lista todos los registros (transacciones) disponibles en el sistema. 
    Tambien usada para saber de que trata cada registro ya que tiene su descripcion.
    Puede ser usadas tambien por el usuario para buscar alguna transaccion que lo ayude.
    Retorna:
        str: Un listado con los nombres y IDs de los registros.
    """
    registros = Registro.objects.all()
    if not registros:
        return "No hay registros disponibles."
    resultado = "Registros disponibles:\n"
    for registro in registros:
        resultado += f"- {registro.id}: {registro.nombre}\n"
    return resultado

def list_estados() -> str:
    """
    Lista todos los estados disponibles en el sistema.

    Retorna:
        str: Un listado con los IDs y tipo de verificación de los estados.
    """
    estados = Estado.objects.all()
    if not estados:
        return "No hay estados registrados."
    resultado = "Estados disponibles:\n"
    for estado in estados:
        resultado += f"- {estado.id}: {estado.tipo_verificacion} (Registro: {estado.registro_verificado_id}, Servidor: {estado.servidor_id}, Empresa: {estado.empresa_id}, Fecha: {estado.fecha})\n"
    return resultado

def consultar_estado_servidor(server_id: int) -> dict:
    """
    Consulta el estado de un servidor remoto (RAM, CPU, almacenamiento, uptime, carga, red, procesos).
    """
    if not isinstance(server_id, int):
        return {"error": "El parámetro server_id debe ser un entero."}
    load_dotenv()
    server_host = os.getenv(f"SERVER_{server_id}_HOST")
    server_user = os.getenv(f"SERVER_{server_id}_USER")
    server_password = os.getenv(f"SERVER_{server_id}_PASSWORD")
    if not server_host or not server_user or not server_password:
        return {"error": "Credenciales del servidor no encontradas."}
    try:
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(server_host, username=server_user, password=server_password)
        # Un solo bloque de comandos para obtener todo el reporte
        commands = '''
        echo 'CPU:'; top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}';
        echo 'RAM:'; free -m | awk 'NR==2{printf "Uso: %.2f%%", $3*100/$2 }';
        echo 'DISK:'; df -h / | awk 'NR==2{printf "Uso: %s", $5}';
        echo 'UPTIME:'; uptime -p;
        '''
        stdin, stdout, stderr = client.exec_command(commands)
        output = stdout.read().decode().strip()
        client.close()
        return {"report": output}
    except Exception as e:
        return {"error": str(e)}

def consultar_base_datos(server_id: int, database: str) -> dict:
    """
    Consulta solo la versión de PostgreSQL en un servidor específico.

    Parámetros:
        server_id (int): ID del servidor PostgreSQL.
        database (str): Nombre de la base de datos a consultar.

    Retorna:
        dict: Versión de PostgreSQL o un mensaje de error.
    """
    if not isinstance(server_id, int):
        return {"error": "El parámetro server_id debe ser un entero."}

    load_dotenv()

    # Cargar credenciales del servidor desde el archivo .env
    server_host = os.getenv(f"POSTGRES_{server_id}_HOST")
    server_user = os.getenv(f"POSTGRES_{server_id}_USER")
    server_password = os.getenv(f"POSTGRES_{server_id}_PASSWORD")

    if not server_host or not server_user or not server_password:
        return {"error": "Credenciales del servidor no encontradas."}

    try:
        # Conexión a la base de datos PostgreSQL
        connection = psycopg2.connect(
            host=server_host,
            user=server_user,
            password=server_password,
            database=database
        )
        cursor = connection.cursor()

        # Consultar versión de PostgreSQL
        cursor.execute("SELECT version();")
        postgres_version = cursor.fetchone()

        connection.close()

        return {"postgres_version": postgres_version[0]}

    except Exception as e:
        return {"error": str(e)}

def get_tools():
    """
    Obtiene las herramientas disponibles para el modelo.

    Retorna:
        list: Lista de herramientas disponibles.
    """
    return [
        insert_transaction,
        delete_transaction,
        list_empresas,
        list_servidores,
        list_registros,
        list_estados,
        registrar_estado_tool,
        consultar_estado_servidor,
        consultar_base_datos
    ]