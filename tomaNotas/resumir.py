import glob

import urllib.request
import urllib.error
from anyio import Path
from openai import OpenAI
import os

import funciones

'''
Página de openAi para meter pasta
(mi cuenta de gmail)
https://platform.openai.com/home
'''

# LEER variable de entorno OPENAI_API_KEY
api_key = os.getenv("OPEN_AI")


PLANTILLA = """Actúa como un apicultor.
Analiza una transcripción de una revisión de unas colmenas generando la siguiente ficha:
el título de la nota debe ser la fecha de la revisión en formato dia (numero) y mes en texto 
seguido del identificador de las colmenas revisadas.

Añade el campo fecha en formato yyyu-mm-dd hh:mm

Para cada colmena haz tres secciones:

    Resumen: del estado general de la colmena como un texto sin viñetas
    Cuadros revisados: Si hay información de los diferentes cuadros haz una viñeta para cada cuadro
    Acciones realizadas en la colmena en formato viñas. Si no se ha tomado ninguna acción no incluyas esta sección

Presenta el resultado como una ficha de inspección clara y breve. No inventes información no mencionada

La transcrición es la siguiente:
"""

def obtener_transcripciones():
    """
    Lee todos los ficheros con extensión .txt del directorio actual.
    
    Retorna:
        list: Lista de rutas de archivos .txt encontrados
    """
    transcripciones = glob.glob("*.txt")
    
    lista = []

    for i, transcripcion in enumerate(transcripciones):

        txt = transcripcion+":\n" + open(transcripcion, "r", encoding="utf-8").read()
        lista.append([transcripcion, txt])
        
    return lista



def consulta_chatgpt(prompt: str, modelo: str = "gpt-4o-mini") -> str:
    """
    Envía una consulta a ChatGPT y devuelve el texto de la respuesta.
    Requiere la variable de entorno OPENAI_API_KEY configurada.
    """

    if not api_key:
        raise RuntimeError("Falta OPENAI_API_KEY en el entorno")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=modelo,
        input=prompt,
    )

    return response.output_text

#funcion que guarda el resultado en un fichero de texto con el mismo nombre que la transcripción pero con extensión .txt
def guardar_ficha(nombre_archivo_txt: str, texto: str) -> None:
    """
    Guarda el texto generado por ChatGPT en un archivo .txt con el mismo nombre que la transcripción.
    
    Args:
        nombre_archivo_txt: Nombre del archivo de transcripción (ej: "transcripcion.txt")
        texto: Texto a guardar
    """
    # Cambiar extensión de .txt a _ficha.md 
    nombre_ficha = nombre_archivo_txt.replace(".txt", "_ficha.md")
    ruta_ficha = Path(nombre_ficha)
    
    with open(ruta_ficha, "w", encoding="utf-8") as f:
        f.write(texto)
    
    print(f"Ficha de inspección guardada en: {ruta_ficha}")



def crear_fichas_inspeccion():
    
    if funciones.esta_conectado_a_internet():
        
        transcripciones = obtener_transcripciones()
        for transcripcion in transcripciones:
            
            print("----------------------------------------\"   \n")
            print(PLANTILLA + transcripcion[1] )
            resultado = consulta_chatgpt(PLANTILLA + transcripcion[1])
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\"   \n  ")
            print(resultado)
            guardar_ficha(transcripcion[0], resultado)  
            funciones.mover_a_procesados(transcripcion[0])
    else:
        print("No hay conexión a internet. No se pueden crear las fichas de inspección.")


crear_fichas_inspeccion()