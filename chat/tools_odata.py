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

def obtener_rendicion(rend_id: int) -> dict:
    """
    Obtener una rendicion específica por su ID

    rend_id: ID de la rendicion.
    return: Detalles de la rendicion y sus items relacionados.
    """
    print("EJECUTANDO: obtener_rendicion")
    try:
        # Inicializar el cliente OData con autenticación
        session = requests.Session()
        session.auth = (ODATA_USER, ODATA_PASS)
        client = pyodata.Client(ODATA_URL, session)

        # Obtener la rendición (cabecera)
        rendicion = client.entity_sets.RendHeaderSet.get_entity(rend_id).execute()

        # Construir la respuesta con los datos de la cabecera
        resultado = {
            "Cabecera": {
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
        }
        print("CABECERA")
        print(resultado)
        try:
            # Obtener los detalles relacionados usando la propiedad de navegación
            detalles = rendicion.nav('ToRendItem').get_entities().execute()
            print(f"Detalles obtenidos: {detalles}")
            resultado["Detalle"] = []
            for detalle in detalles:
                resultado["Detalle"].append({
                    "RendId": detalle.RendId,
                    "RendItemId": detalle.RendItemId,
                    "RendType": detalle.RendType,
                    "RendTypeText": detalle.RendTypeText,
                    "DocumentDate": detalle.DocumentDate,
                    "PostingDate": detalle.PostingDate,
                    "Amount": detalle.Amount,
                    "Currency": detalle.Currency,
                    "Vendor": detalle.Vendor,
                    "VendorName": detalle.VendorName,
                })
            print("DETALLE")
            print(resultado)
        except Exception as e:
            print(f"Error al obtener los detalles: {str(e)}")
        return resultado
    except Exception as e:
        return {"error": str(e)}

def listar_rendiciones(limit: int = 10) -> list:
    """
    Listar las rendiciones limitando la cantidad a lo que determine el usuario mediante limit

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
        obtener_rendicion,
        listar_rendiciones
    ]

if __name__ == "__main__":
    # Probar la función obtener_rendicion con un ID de ejemplo
    rend_id = 12  # Cambia este ID por uno válido en tu sistema
    print(f"Obteniendo rendición con ID {rend_id}...")
    resultado = obtener_rendicion(rend_id)
    print("Resultado:")
    print(resultado)