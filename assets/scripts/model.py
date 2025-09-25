from langchain.prompts import PromptTemplate
from langchain.llms import LlamaCpp
from langchain.chains import ConversationalRetrievalChain
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la ruta base del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
model_path = os.path.join(project_root, "models", "mistral-7b-instruct-v0.1.Q4_K_M.gguf")

# Verificar que el archivo del modelo existe
if not os.path.exists(model_path):
    logger.error(f"❌ Archivo de modelo no encontrado en: {model_path}")
    logger.info("👉 Ejecuta primero: ./scripts/download_model.sh")
    raise FileNotFoundError(f"Model file not found at: {model_path}")
else:
    logger.info(f"✅ Modelo encontrado en: {model_path}")

# Formato del prompt mejorado con detección de idioma más estricta
template = """
[INST] <<SYS>>
Eres Daniel Rada vives en Caracas Venezuela y tienes 37 años, experto en infraestructura cloud (AWS, Azure) y ciberseguridad con 10+ años de experiencia.
Estás respondiendo preguntas en una entrevista técnica. Responde SIEMPRE EN PRIMERA PERSONA, de forma concisa y profesional.

**REGLAS ESTRICTAS DE IDIOMA:**
1. Si la pregunta está en ESPAÑOL, responde EXCLUSIVAMENTE en ESPAÑOL
2. Si la pregunta está en INGLÉS, responde EXCLUSIVAMENTE en INGLÉS
3. Para otros idiomas, responde en el mismo idioma de la pregunta
4. NUNCA mezcles idiomas en una respuesta
5. Usa solo información del contexto proporcionado

Si no conoces la respuesta, di "No tengo información sobre eso en mi experiencia".
<</SYS>>

Contexto relevante:
{context}

Historial de la conversación:
{chat_history}

Pregunta actual: {question}
[/INST]
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "chat_history", "question"]
)

# Configuración del modelo
try:
    logger.info("Cargando modelo Mistral-7B...")
    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=33,
        n_batch=512,
        n_ctx=4096,
        temperature=0.3,
        max_tokens=512,
        verbose=False,
        seed=42
    )
    logger.info("✅ Modelo cargado exitosamente")
except Exception as e:
    logger.error(f"❌ Error cargando el modelo: {str(e)}")
    raise

# Crear sistema RAG con memoria
def get_qa_chain(vector_store, memory):
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 20}
        ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        get_chat_history=lambda h: h,
        verbose=True
    )
