import os
import pyodata
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# URL y credenciales del servicio OData
ODATA_URL = os.getenv('RENDICION_ODATA_URL')
ODATA_USER = os.getenv('RENDICION_ODATA_USER')
ODATA_PASS = os.getenv('RENDICION_ODATA_PASS')

def obtener_rendicion_por_id(rend_id: int) -> dict:
    """
    Obtiene una rendición específica por su ID.

    rend_id: ID de la rendición.
    return: Detalles de la rendición.
    """
    try:
        # Inicializar el cliente OData con autenticación
        session = requests.Session()
        session.auth = (ODATA_USER, ODATA_PASS)
        client = pyodata.Client(ODATA_URL, session)

        # Obtener la rendición
        rendicion = client.entity_sets.RendHeaderSet.get_entity(rend_id).execute()
        return {
            "RendId": rendicion.RendId,
            "VendorFfName": rendicion.VendorFfName,
            "Type": rendicion.Type,
            "TypeText": rendicion.TypeText,
            "CompanyCode": rendicion.CompanyCode,
            "DocumentNumber": rendicion.DocumentNumber,
            "FiscalYear": rendicion.FiscalYear,
            "CreationDate": rendicion.CreationDate,
            "RendStatus": rendicion.RendStatus,
            "RendStatusText": rendicion.RendStatusText,
        }
    except Exception as e:
        return {"error": str(e)}

def listar_rendiciones(limit: int = 10) -> list:
    """
    Listar las rendiciones disponibles limitando la cantidad a lo que determine el usuario mediante limit

    limit: Número máximo de rendiciones a devolver.
    return: Lista de rendiciones.
    """
    try:
        # Inicializar el cliente OData con autenticación
        session = requests.Session()
        session.auth = (ODATA_USER, ODATA_PASS)
        client = pyodata.Client(ODATA_URL, session)

        # Obtener las rendiciones
        rendiciones = client.entity_sets.RendHeaderSet.get_entities().top(limit).execute()
        resultado = []
        for rendicion in rendiciones:
            resultado.append({
                "RendId": rendicion.RendId,
                "VendorFfName": rendicion.VendorFfName,
                "Type": rendicion.Type,
                "CompanyCode": rendicion.CompanyCode,
                "DocumentNumber": rendicion.DocumentNumber,
                "FiscalYear": rendicion.FiscalYear,
            })
        print(f"Total rendiciones obtenidas: {len(resultado)}")
        print(f"Rendiciones: {resultado}")
        return resultado
    except Exception as e:
        return {"error": str(e)}

def get_tools_sap():
    """
    Obtiene las herramientas ODATA o SAP disponibles para el modelo.

    Retorna:
        list: Lista de herramientas disponibles.
    """
    return [
        obtener_rendicion_por_id,
        listar_rendiciones,
    ]