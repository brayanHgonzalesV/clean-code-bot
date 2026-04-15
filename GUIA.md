# Clean Code Bot - Guía de Uso

## Requisitos

- Python 3 instalado
- Terminal (CMD, PowerShell o Bash)

---

## Paso 1: Obtener API Key (Gratis)

1. Ve a https://console.groq.com/
2. Crea una cuenta
3. Click en API Keys → Create Key
4. Copia la key

---

## Paso 2: Configurar API Key

Crea un archivo `.env` en la carpeta `clean-code-bot`:

```
GROQ_API_KEY=aqui-tu-key
```

---

## Paso 3: Instalar dependencias

```bash
cd clean-code-bot
pip3 install -r requirements.txt
```

---

## Paso 4: Ejecutar

```bash
python3 clean_code_bot.py entrada.py -o salida.py
```

---

## Ejemplo completo

```bash
# Obtener key en https://console.groq.com/

# Crear archivo .env con:
# GROQ_API_KEY=gsk_xxxxxxxx

# Ejecutar
pip3 install -r requirements.txt
python3 clean_code_bot.py examples/before/user_manager.py -o ejemplo_limpio.py -v
```

---

## Opciones

| Comando | Descripción |
|---------|-------------|
| `-o archivo.py` | Guardar en archivo |
| `-v` | Mostrar progreso |
| `-l javascript` | Lenguaje del código |
| `-p openai` | Usar OpenAI en vez de Groq |