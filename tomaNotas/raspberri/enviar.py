from funciones import enviar_a_servidor_remoto, mover_a_procesados 

import glob     
from pathlib import Path

def obtener_archivos_wav():
    """
    Lee todos los ficheros con extensión .wav del directorio actual.
    Retorna:
        list: Lista de rutas de archivos .wav encontrados
    """
    audios = glob.glob("*.wav")
    
    for i, audio in enumerate(audios):
        print(f"{i+1}. {audio} \n---------")
        
        if enviar_a_servidor_remoto(audio):
            print(f"Archivo '{audio}' enviado exitosamente.") 
            mover_a_procesados(audio)  
        else:
            print(f"Error al enviar el archivo '{audio}'. No se moverá a 'procesados'.")       
    return audios

obtener_archivos_wav()