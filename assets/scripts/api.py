import sys
import os
import logging
import traceback
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from model import get_qa_chain

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger(__name__)

# Obtener rutas absolutas
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
embeddings_dir = os.path.join(project_root, "embeddings")

logger.info(f"Ruta del proyecto: {project_root}")
logger.info(f"Directorio de embeddings: {embeddings_dir}")

app = FastAPI()

# Redis configuration
REDIS_URL = "redis://localhost:6379/0"

# Cargar embeddings y vector store
try:
    logger.info("Cargando embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    vector_store = Chroma(
        persist_directory=embeddings_dir,
        embedding_function=embeddings
    )
    logger.info("✅ Embeddings cargados exitosamente")
except Exception as e:
    logger.error(f"❌ Error cargando embeddings: {str(e)}")
    logger.error(traceback.format_exc())
    vector_store = None

class Query(BaseModel):
    question: str
    session_id: str

class Feedback(BaseModel):
    question: str
    response: str
    correct_response: str

@app.post("/ask")
async def ask_question(query: Query):
    try:
        if not vector_store:
            return {"answer": "Sistema no inicializado correctamente"}
        
        logger.info(f"Recibida pregunta: '{query.question}' (Session: {query.session_id})")
        
        # Crear almacenamiento de historial en Redis
        redis_memory = RedisChatMessageHistory(
            session_id=query.session_id,
            url=REDIS_URL,
            key_prefix="danielai:"
        )
        
        # Crear memoria compatible con la cadena
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=redis_memory,
            return_messages=True,
            input_key="question",
            output_key="answer"
        )
        
        # Crear cadena QA con memoria de sesión
        qa_chain = get_qa_chain(vector_store, memory)
        
        # Ejecutar la cadena QA
        result = qa_chain.invoke({"question": query.question})
        
        logger.info(f"Respuesta generada: {result['answer'][:200]}...")
        
        return {"answer": result["answer"]}
        
    except Exception as e:
        logger.error(f"❌ Error procesando pregunta: {str(e)}")
        logger.error(traceback.format_exc())
        return {"answer": "Lo siento, ocurrió un error al procesar tu solicitud"}

@app.post("/feedback")
async def receive_feedback(feedback: Feedback):
    try:
        # Escribir feedback en archivo CSV
        with open("feedback_data.csv", "a") as f:
            f.write(f"{feedback.question},{feedback.response},{feedback.correct_response}\n")
        logger.info(f"Feedback recibido para pregunta: {feedback.question}")
        return {"status": "feedback received"}
    except Exception as e:
        logger.error(f"Error al guardar feedback: {str(e)}")
        return {"status": "error"}

@app.get("/health")
async def health_check():
    return {
        "status": "OK" if vector_store else "ERROR",
        "vector_store": "LOADED" if vector_store else "MISSING"
    }

if __name__ == "__main__":
    import uvicorn
    import socket
    from contextlib import closing

    def find_free_port():
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    port = 8000
    try:
        # Verificar si el puerto está disponible
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
    except OSError:
        port = find_free_port()
        logger.warning(f"⚠️ Puerto 8000 ocupado, usando puerto alternativo: {port}")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
