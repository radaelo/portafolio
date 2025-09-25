from langchain.fine_tuning import FineTune
from langchain.llms import LlamaCpp
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando proceso de fine-tuning...")
        
        # Cargar modelo base
        model_path = "../models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
        model = LlamaCpp(model_path=model_path)
        
        # Configurar fine-tuner
        fine_tuner = FineTune(model)
        
        # Ajustar modelo con datos de entrenamiento
        fine_tuner.fine_tune(
            training_data="training_data.jsonl",
            epochs=3,
            learning_rate=1e-5
        )
        
        # Guardar modelo ajustado
        output_path = "../models/daniel_rada_finetuned.gguf"
        model.save(output_path)
        logger.info(f"✅ Modelo ajustado guardado en: {output_path}")
        
    except Exception as e:
        logger.error(f"❌ Error en fine-tuning: {str(e)}")

if __name__ == "__main__":
    main()
