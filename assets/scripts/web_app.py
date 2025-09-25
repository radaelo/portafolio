from flask import Flask, request, render_template, session, jsonify
import requests
import uuid
import os
import logging
import pathlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la ruta base del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
template_dir = os.path.join(current_dir, "templates")

# Verificar y crear directorio si es necesario
pathlib.Path(template_dir).mkdir(parents=True, exist_ok=True)

logger.info(f"Directorio actual: {current_dir}")
logger.info(f"Directorio de plantillas: {template_dir}")

app = Flask(__name__, template_folder=template_dir, static_folder='static')
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'session_id' not in session:
        return jsonify({"answer": "Sesión no iniciada"})
    
    user_input = request.form['message']
    try:
        logger.info(f"Enviando pregunta: {user_input}")
        response = requests.post(
            "http://localhost:8000/ask", 
            json={
                "question": user_input,
                "session_id": session['session_id']
            }
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error al conectar con la API: {str(e)}")
        return jsonify({"answer": f"Error al conectar con la API: {str(e)}"})

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        logger.info(f"Recibiendo feedback: {data}")
        
        # Enviar feedback a la API
        response = requests.post(
            "http://localhost:8000/feedback", 
            json=data
        )
        
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error procesando feedback: {str(e)}")
        return jsonify({"status": "error"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
