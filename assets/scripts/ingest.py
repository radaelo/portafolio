import os
import sys
import logging
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Obtener la ruta absoluta del proyecto
        current_dir = Path(os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Directorio del script: {current_dir}")
        
        # Calcular la raíz del proyecto
        project_root = current_dir.parent
        logger.info(f"Ruta del proyecto: {project_root}")
        
        # Configurar rutas absolutas
        data_dir = project_root / "data"
        embeddings_dir = project_root / "embeddings"
        
        logger.info(f"Buscando documentos en: {data_dir}")
        logger.info(f"¿Existe el directorio? {data_dir.exists()}")
        
        # Verificar si el directorio de datos existe
        if not data_dir.exists():
            logger.error(f"❌ Error: El directorio {data_dir} no existe")
            logger.info("👉 Ejecuta primero: python app/pdf_to_text.py")
            return
        
        # Listar archivos en el directorio para diagnóstico
        files = list(data_dir.glob('*.txt'))
        logger.info(f"Archivos encontrados en data: {[f.name for f in files]}")
        
        if not files:
            logger.error("⚠️ ¡No se encontraron archivos .txt en el directorio de datos!")
            return
        
        logger.info("Cargando documentos...")
        loader = DirectoryLoader(str(data_dir), glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        
        if not documents:
            logger.error("⚠️ ¡No se encontraron documentos cargables!")
            return
        
        logger.info(f"Se cargaron {len(documents)} documentos")
        
        logger.info("Dividiendo documentos...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,          # Reduce el tamaño
            chunk_overlap=150,       # Aumenta el solapamiento
            separators=["\n\n", "\n", ". ", "! ", "? ", ", "],  # Mejores puntos de corte
            length_function=len,
        )
        texts = text_splitter.split_documents(documents)
        logger.info(f"Se crearon {len(texts)} fragmentos de texto")
        
        logger.info("Creando embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        logger.info("Almacenando vectores en ChromaDB...")
        vector_db = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=str(embeddings_dir)
        )
        
        logger.info("✅ ¡Embeddings creados exitosamente!")
        logger.info(f"Ubicación: {embeddings_dir}")
    except Exception as e:
        logger.error(f"❌ Error crítico en ingest.py: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
