import pyodata
import requests

def obtener_orden_de_compra(orden_id: int) -> dict:
    """
    Obtiene una orden de compra específica por su numero de ID.

    orden_id: ID de la orden de compra.
    return: Detalles de la orden de compra.
    """
    try:
        # Inicializar el cliente OData
        session = requests.Session()
        client = pyodata.Client('https://services.odata.org/V2/Northwind/Northwind.svc/', session)

        # Obtener la orden de compra
        orden = client.entity_sets.Orders.get_entity(orden_id).execute()
        return {
            "OrdenID": orden.OrderID,
            "ClienteID": orden.CustomerID,
            "FechaOrden": orden.OrderDate,
            "NombreEnvio": orden.ShipName,
            "PaisEnvio": orden.ShipCountry,
        }
    except Exception as e:
        return {"error": str(e)}

def obtener_ordenes_con_precio_mayor_a(precio_minimo: float) -> list:
    """
    Obtiene las órdenes de compra cuyo precio total sea mayor a un valor dado.

    precio_minimo: Precio mínimo total de la orden.
    return: Lista de órdenes que cumplen la condición.
    """
    try:
        session = requests.Session()
        client = pyodata.Client('https://services.odata.org/V2/Northwind/Northwind.svc/', session)

        # Traer todas las órdenes
        ordenes = client.entity_sets.Orders.get_entities().execute()
        resultado = []

        for orden in ordenes:
            # Obtener los detalles de la orden para calcular el total
            detalles = client.entity_sets.Order_Details.get_entities().filter(f"OrderID eq {orden.OrderID}").execute()
            total = sum(float(detalle.UnitPrice) * int(detalle.Quantity) for detalle in detalles)

            # Verificar si el total es mayor al precio mínimo
            if total > precio_minimo:
                resultado.append({
                    "OrdenID": orden.OrderID,
                    "ClienteID": orden.CustomerID,
                    "FechaOrden": orden.OrderDate,
                    "Total": total,
                    "NombreEnvio": orden.ShipName,
                    "PaisEnvio": orden.ShipCountry,
                })

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
        obtener_orden_de_compra,
        obtener_ordenes_con_precio_mayor_a
    ]