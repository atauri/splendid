# tomaNotas 📝

Aplicación completa para grabar, transcribir y resumir audio usando inteligencia artificial.

## Versiones

### Raspberry pi zero w

Es una version portable para llevar al colmenar y realizar las inspecciones. Graba el audio y si hay conexion a internet (a través del móvil) envía los audios al servidor

   **Tareas Pendientes:**
   
   *  Hacer en el servidor la transcripción del audio, generación de la ficha e inserción de la Base de datos

   * Terminar y Enviar cuando se desconecta el micrófono y apagar la raspi despues de enviar.
   * Añadir el zumabador (listo, enviar, apagar...) 

### Windows

   Verisón que transcribe y genera las fichas en PC

## 🎯 Funcionalidades

- **Grabación de Audio por VAD (Voice Activity Detection)**: Graba automáticamente cuando detecta sonido
- **Transcripción con OpenAI Whisper**: Convierte audio a texto de alta calidad
- **Resumen con ChatGPT**: Analiza y resume las transcripciones


### Dependencias Python

```bash
pip install pyaudio numpy openai
```

### Configuración de API Keys

Debes establecer variables de entorno para las APIs:

   * OPEN_AI

## 🚀 Instalación

### En Windows
1. Instala Python desde [python.org](https://python.org)
2. Abre PowerShell o CMD
3. Navega a la carpeta del proyecto:
   ```bash
   cd tomaNotas
   ```
4. Instala dependencias:
   ```bash
   pip install pyaudio numpy openai
   ```

### En Raspberry Pi Zero 2W
1. Actualiza el sistema:
   ```bash
   sudo apt update && sudo apt upgrade
   ```
2. Instala dependencias del sistema:
   ```bash
   sudo apt install python3-pyaudio portaudio19-dev python3-numpy
   ```
3. Instala dependencias de Python:
   ```bash
   pip3 install pyaudio numpy 
   ```

## 📁 Estructura de Archivos

```
tomaNotas/
├── grabar_audio_windows.py      # Grabación VAD para Windows
├── grabar_audio_Raspi.py        # Grabación VAD para Raspberry Pi
├── trancribir.py                # Transcripción con Whisper
├── resumir.py                   # Resumen con ChatGPT
├── funciones.py                 # Funciones auxiliares
└── README.md                    # Este archivo
```

## 🎤 Uso de Grabación

### Windows
```bash
# Grabar con parámetros por defecto
python grabar_audio_windows.py

# Grabar con umbral personalizado
python grabar_audio_windows.py -u 800

# Especificar dispositivo de micrófono
python grabar_audio_windows.py -d 2

# Listar micrófonos disponibles
python grabar_audio_windows.py --listar

# Nombre de archivo personalizado
python grabar_audio_windows.py -o mi_grabacion.wav
```

### Raspberry Pi
```bash
# Grabar con parámetros por defecto
python3 grabar_audio_Raspi.py

# Grabar con umbral personalizado
python3 grabar_audio_Raspi.py -u 1200

# Listar micrófonos disponibles
python3 grabar_audio_Raspi.py --listar
```

**Parámetros disponibles:**
- `-u, --umbral`: Nivel de amplitud para activar grabación (default: 500-1000)
- `-o, --salida`: Nombre del archivo WAV (default: Audio<timestamp>.wav)
- `-d, --dispositivo`: ID del micrófono (usa --listar para ver disponibles)
- `--listar`: Muestra los micrófonos detectados

## 📝 Uso de Transcripción

```bash
# Transcribir archivo específico
python trancribir.py -f mi_grabacion.wav

# Transcribir todos los WAV en el directorio
python trancribir.py --todos

# Especificar modelo de Whisper
python trancribir.py -f mi_grabacion.wav -m large
```

## 🤖 Uso de Resumen

```bash
# Hacer consulta a ChatGPT
python resumir.py -p "Analiza este texto" -w mi_grabacion.wav

# Solo consulta sin guardar
python resumir.py -p "¿Cuál es el tema principal?"

# Especificar modelo
python resumir.py -p "Resumir" -m gpt-4
```

## 🔧 Configuración Avanzada

### Ajuste de Umbral de Micrófono
El umbral controla cuándo se activa la grabación:
- **Valores bajos (300-500)**: Se activa con sonidos débiles, más falsos positivos
- **Valores medios (700-1000)**: Balance entre sensibilidad y precisión
- **Valores altos (1200+)**: Solo graba sonidos fuertes

Ajusta según tu entorno de ruido de fondo.

### Duración de Silencio
La grabación se detiene después de 10 segundos de silencio. Modifica `SILENCIO_LIMIT` en los scripts para cambiar este valor.

## 📊 Flujo de Trabajo Típico

1. **Grabar** → `grabar_audio_windows.py` o `grabar_audio_Raspi.py`
2. **Transcribir** → `trancribir.py` (genera `.txt`)
3. **Resumir** → `resumir.py` (analiza con ChatGPT)

**Ejemplo completo:**
```bash
# 1. Grabar audio
python grabar_audio_windows.py -o nota.wav

# 2. Transcribir
python trancribir.py -f nota.wav

# 3. Resumir y analizar
python resumir.py -p "Haz una ficha técnica de esta nota" -w nota.wav
```
## 📚 Archivos Generados

- `Audio<YYYY-MM-DD_HH-MM-SS>.wav` → Archivo de audio grabado
- `Audio<YYYY-MM-DD_HH-MM-SS>.txt` → Transcripción en texto
- Salida en consola → Resumen y análisis

## 🐛 Solución de Problemas

### Error: "No se pudo abrir el micrófono"
- Verifica que el micrófono esté conectado
- Usa `--listar` para ver dispositivos disponibles
- Especifica el dispositivo con `-d`

### Error: "Falta OPENAI_API_KEY"
- Asegúrate de tener configurada tu clave de OpenAI
- Verifica la variable de entorno `OPENAI_API_KEY`

### Audio con bajo volumen
- Aumenta el umbral con `-u`. En raspberry usa el comando *alsamixer*

### Error en Raspberry Pi: "No module named 'pyaudio'"
```bash
sudo apt install python3-pyaudio portaudio19-dev
pip3 install pyaudio
```

## 📄 Licencia

Este proyecto es privado y de uso personal.

## 👤 Autor

David Ataurí
