import os
from dotenv import load_dotenv
from .providers import gpt_response
from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GPT_API_KEY = os.getenv('GPT_API_KEY')


def gemini_generate(user_input):
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_input),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
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