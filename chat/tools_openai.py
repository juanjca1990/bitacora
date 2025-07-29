functions = [
    {
        "name": "insert_transaction",
        "description": "Inserta una nueva transacción en la base de datos.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "El nombre de la transacción."},
                "descripcion": {"type": "string", "description": "Una descripción detallada de la transacción."}
            },
            "required": ["nombre", "descripcion"]
        }
    },
    {
        "name": "delete_transaction",
        "description": "Elimina una transacción de la base de datos según el nombre.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "description": "El nombre exacto de la transacción a eliminar."}
            },
            "required": ["nombre"]
        }
    },
]