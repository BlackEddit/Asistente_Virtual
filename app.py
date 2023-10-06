import os
import openai
from dotenv import load_dotenv # para el uso de archivos ENV, que aplica en seguridad
from flask import Flask, render_template, request
import json
from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand
from threading import Thread


#Cargar llaves del archivo .env / variables seguras APIs, Solo por seguridad propia
load_dotenv()

# configura las llaves de las APIs
openai.api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')

# Crear una instancia de la aplicación Flask / Objeto flask ---- Flask es para creacion de sitios web con python
app = Flask(__name__)

# Definir la ruta raíz que renderiza la página HTML recorder.html
@app.route("/") # '/' representa la direccion inicial de el sitio web
def index(): #/ esta funcion es la que se ejecutara cuando visite la direcion anterior
    return render_template("recorder.html")

# Definir la ruta /audio que acepta solicitudes POST --- solicitudes POST son una manera de enviar datos a un servidor. A diferencia de las solicitudes GET
@app.route("/audio", methods=["POST"])
def audio():
    # Obtener el archivo de audio de la solicitud
    audio = request.files.get("audio") #Obtiene el archivo de audio enviado. --- contiene los datos enviados por el cliente. request.files.get("audio")
    # Transcribir el audio a texto
    text = Transcriber().transcribe(audio)
    
    # Crear una instancia de LLM y procesar el texto para identificar una función y argumentos
    llm = LLM()
    function_name, args, message = llm.process_functions(text)
    
    # Verificar si se identificó una función
    if function_name is not None:
        # Procesar diferentes funciones identificadas
        if function_name == "get_weather":
            # Obtener el clima basado en la ubicación proporcionada
            function_response = Weather().get(args["ubicacion"])
            function_response = json.dumps(function_response)
            print(f"Respuesta de la funcion: {function_response}")
            
            # Procesar la respuesta y generar un archivo de audio con la respuesta
            final_response = llm.process_response(text, message, function_name, function_response)
            tts_file = TTS().process(final_response)
            # Devolver la respuesta y el archivo de audio como un objeto JSON
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        # Procesar otros casos como enviar correo, abrir Chrome, etc.
        if function_name == "send_email":
            final_response = "Tu que estas leyendo el codigo, implementame y envia correos muahaha"
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
        # ... (otros casos)
        ''' Codigo de pruebas para respuestas'''
    
        
        
    # Si no se identifica ninguna función, generar una respuesta por defecto
    else:
        # final_response = "No tengo idea de lo que estás hablando, Edd"
        # tts_file = TTS().process(final_response)
        # return {"result": "ok", "text": final_response, "file": tts_file}
        
        # Obtener respuesta de OpenAI
        openai_response = llm.get_openai_response(text)
        
        # Convertir respuesta a audio
        tts_file = TTS().process(openai_response)
        
        # Devolver la respuesta y el archivo de audio como un objeto JSON
        return {"result": "ok", "text": openai_response, "file": tts_file}
