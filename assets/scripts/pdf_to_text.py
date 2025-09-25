import os
import re
import argparse
import time
import logging
from pathlib import Path
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytesseract
from pdf2image import convert_from_path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_text(text):
    """Limpia el texto extraído"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'-\n', '', text)  # Une palabras divididas
    return text.strip()

def is_pdf_scanned(pdf_path):
    """Verifica si un PDF es escaneado (basado en imágenes)"""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                if page.extract_text().strip():
                    return False
            return True
    except Exception:
        return True

def ocr_pdf(pdf_path):
    """Realiza OCR en un PDF escaneado"""
    try:
        logger.info(f"Realizando OCR en {Path(pdf_path).name}")
        images = convert_from_path(pdf_path, dpi=300)
        text = ""
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(img, lang='spa')
            text += f"--- Página {i+1} ---\n{page_text}\n\n"
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error en OCR: {str(e)}")
        return ""

def pdf_to_text(pdf_path, txt_path):
    """Convierte un archivo PDF a texto"""
    pdf_name = Path(pdf_path).name
    try:
        start_time = time.time()
        logger.info(f"Procesando: {pdf_name}")
        
        # Verificar si es un PDF escaneado
        scanned = is_pdf_scanned(pdf_path)
        
        if scanned:
            logger.info(f"PDF escaneado detectado: {pdf_name}")
            text = ocr_pdf(pdf_path)
        else:
            # Método para PDFs normales
            try:
                with open(pdf_path, 'rb') as pdf_file:
                    reader = PdfReader(pdf_file)
                    text = '\n\n'.join([page.extract_text() for page in reader.pages])
            except Exception:
                text = extract_text(pdf_path)
        
        text = clean_text(text)
        
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        
        proc_time = time.time() - start_time
        logger.info(f"✅ Convertido: {pdf_name} -> {Path(txt_path).name} ({proc_time:.2f}s)")
        return True
    except Exception as e:
        logger.error(f"❌ Error procesando {pdf_name}: {str(e)}")
        return False

def batch_convert(input_dir, output_dir):
    """Convierte todos los PDFs en un directorio a texto"""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(input_dir.glob('*.pdf'))
    
    if not pdf_files:
        logger.warning(f"⚠️ No se encontraron archivos PDF en {input_dir}")
        return
    
    logger.info(f"🔍 Encontrados {len(pdf_files)} archivos PDF para convertir...")
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for pdf_file in pdf_files:
            txt_path = output_dir / f"{pdf_file.stem}.txt"
            # CORRECCIÓN: Paréntesis correctamente cerrados
            future = executor.submit(
                pdf_to_text, 
                str(pdf_file), 
                str(txt_path)
            )
            futures.append(future)
        
        success_count = 0
        for future in as_completed(futures):
            if future.result():
                success_count += 1
    
    logger.info(f"\n🎉 Conversión completa: {success_count}/{len(pdf_files)} archivos convertidos exitosamente")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convierte archivos PDF a texto')
    parser.add_argument('--input', type=str, default='pdfs', help='Directorio con archivos PDF')
    parser.add_argument('--output', type=str, default='data', help='Directorio para archivos de texto')
    
    args = parser.parse_args()
    batch_convert(args.input, args.output)
