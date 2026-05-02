import urllib.request
import urllib.error

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
