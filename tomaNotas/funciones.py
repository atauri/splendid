import urllib.request
import urllib.error
import subprocess

def esta_conectado_a_internet() -> bool:
    """
    Verifica si hay conexión a internet intentando acceder a google.com.
    
    Retorna:
        bool: True si hay conexión, False si no.
    """
    try:
        urllib.request.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib.error.URLError:
        return False

# fucnion que mueve un fichero a la carpeta procesados
def mover_a_procesados(nombre_archivo: str) -> None:
    """
    Mueve un archivo a la carpeta 'procesados' dentro del directorio actual.
    
    Args:
        nombre_archivo: Nombre del archivo a mover (ej: "transcripcion.txt")
    """
    import shutil
    import os

    carpeta_procesados = "./procesados"
    if not os.path.exists(carpeta_procesados):
        os.makedirs(carpeta_procesados)

    ruta_origen = os.path.join(os.getcwd(), nombre_archivo)
    ruta_destino = os.path.join(os.getcwd(), carpeta_procesados, nombre_archivo)
    print(f"Moviendo '{nombre_archivo}' a '{carpeta_procesados}/'...")
    try:
        shutil.move(ruta_origen, ruta_destino)
        print(f"Archivo '{nombre_archivo}' movido a '{carpeta_procesados}/'")
    except Exception as e:
        print(f"Error al mover el archivo: {e}")


# función que envía un fichero a un servidor remoto usando scp
def enviar_a_servidor_remoto(
    nombre_archivo: str,
    servidor: str = "titi.etsii.urjc.es",
    usuario: str = "tadu",
    destino: str = "/home/tadu/proyectos/splendid/revisiones/Zarzalejo/",
    puerto: int = 222
) -> bool:
    """
    Envía un archivo a un servidor remoto usando SCP.

    Args:
        nombre_archivo: Nombre del archivo a enviar.
        servidor: Dirección del servidor.
        usuario: Usuario en el servidor.
        destino: Ruta de destino en el servidor.
        puerto: Puerto SSH (por defecto 222).
    """
    # Ejemplo de uso: scp -P 222 "2026-05-03 11_23_14.wav" tadu@titi.etsii.urjc.es:/home/tadu/proyectos/splendid/revisiones/Zarzalejo/

    comando = f"scp -P {puerto} \"{nombre_archivo}\" {usuario}@{servidor}:\"{destino}\""
    print(f"Enviando '{nombre_archivo}' a '{servidor}:{destino}'...")
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"Archivo '{nombre_archivo}' enviado a '{servidor}:{destino}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al enviar el archivo: {e}")
        return False
