#!/bin/bash

# 1. Detener servicios
echo "Deteniendo servicios..."
pkill -f "python api.py"
pkill -f "python web_app.py"

# 2. Procesar nuevos documentos
echo "Procesando documentos..."
cd ~/daniel-ai/app
python pdf_to_text.py
python ingest.py

# 3. Reiniciar servicios
echo "Reiniciando servicios..."
cd ~/daniel-ai/app
python api.py &
cd ~/daniel-ai/web
python web_app.py &

echo "Actualización completada."
