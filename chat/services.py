import os
from dotenv import load_dotenv
from .providers import gpt_response
from google import genai
from google.genai import types
from AppCrud.models import Registro

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GPT_API_KEY = os.getenv('GPT_API_KEY')


def insert_transaction(nombre: str, descripcion: str) -> str:
    """
    Inserta una nueva transacción en la base de datos.

    Parámetros:
        nombre (str): El nombre de la transacción. Ejemplo: "Compra de insumos".
        descripcion (str): Una descripción detallada de la transacción. Ejemplo: "Compra de materiales para el área de producción".

    Retorna:
        str: Mensaje de confirmación con el nombre y la descripción de la transacción registrada.

    Uso:
        Utiliza esta función para registrar una transacción cuando el usuario proporcione ambos datos.
        No requiere otros campos adicionales.
    """
    registro = Registro(nombre=nombre, descripcion=descripcion)
    registro.save()
    return f'Transacción insertada: {registro.nombre} - {registro.descripcion}'


def gemini_generate(user_input):
    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        ),
    ]
    tools = [insert_transaction]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
        tools=tools,
    )
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text or ""
    return response_text


def process_message(data):
    user_message = data.get('message', '')
    reglas = """Sigue la instrucción exactamente como la da el usuario.
    El usuario siempre tiene razón. 
    No hagas sugerencias ni pidas información extra.
    Y solo responder OK o No comprendo bien tu mensaje.
    En caso de que mande cosas como:
    'registrar transaccion AN78 que se encarga de generar los repartos de abastecimiento'
    deberia registrar transaccion "AN78" y de descripcion "encargada de generar los repartos de abastecimiento"
    """
    user_message = f"{reglas}\n{user_message}"
    provider = data.get('provider', 'gemini')
    if not user_message:
        return {'error': 'No message provided'}
    if provider == "gemini":
        response = gemini_generate(user_message)
    elif provider == "gpt":
        api_key = GPT_API_KEY
        response = gpt_response(user_message, api_key)
    else:
        return {'error': 'Proveedor no soportado'}
    return {'response': response}