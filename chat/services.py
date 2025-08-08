import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from chat.tools_gemini import get_tools
from chat.tools_openai import functions
import openai

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GPT_API_KEY = os.getenv('GPT_API_KEY')

def gemini_generate(user_input):
    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        ),
    ]
    tools = get_tools()
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

def gpt_generate(user_input):
    client = openai.OpenAI(api_key=GPT_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}],
        functions=functions,
        function_call="auto"
    )
    return response

def process_message(data):
    user_message = data.get('message', '')
    reglas = """
    - Sigue la instrucción exactamente como la da el usuario.
    - El usuario siempre tiene razón. 
    - No hagas sugerencias ni pidas información extra.
    - Solo responder OK o No comprendo tu mensaje o bien lo que retorne la tool.
    - En caso de que mande cosas como:
    'registrar transaccion AN78 que se encarga de generar los repartos de abastecimiento'
    deberia registrar transaccion "AN78" y de descripcion "encargada de generar los repartos de abastecimiento".
    - No incluir razonamiento en la respuesta, solo muy basico y referido a los datos
    - si pregunta sobre estado de un servidor puntutal o sobre una base de datos si retornar un mensaje que de un razonamiento y haga un reporte tecnico/funcional
    """
    user_message = f"{reglas}\n{user_message}"
    provider = data.get('provider', 'gemini')
    if not user_message:
        return {'error': 'No message provided'}
    if provider == "gemini":
        response = gemini_generate(user_message)
    elif provider == "gpt":
        response = gpt_generate(user_message)
    else:
        return {'error': 'Proveedor no soportado'}
    return {'response': response}