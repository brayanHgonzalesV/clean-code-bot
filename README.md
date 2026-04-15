# Clean Code Bot

Refactoriza y documenta código sucio.

## Setup

```bash
# 1. Obtener API key gratis en https://console.groq.com/

# 2. Crear .env con tu key
GROQ_API_KEY=tu-key-aqui

# 3. Crear entorno virtual
python3 -m venv venv

# 4. Activar Windows
venv\Scripts\activate

# 5. Instalar
pip3 install -r requirements.txt
```

## Ejecutar

```bash
python3 clean_code_bot.py examples/before/user_manager.py -o examples/resultado.py -v
```

## Opciones

```bash
-o archivo    # Guardar resultado
-v            # Ver progreso
-l javascript # Lenguaje
-p openai     # Usar OpenAI
```