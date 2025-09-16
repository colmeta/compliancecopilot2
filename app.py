# ==============================================================================
# Pearl AI - "Veritas" Engine v1.2 (Zero-Defect Backend)
# Author: The CEO
# Stack: Python, Flask, Google Generative AI SDK
# Description: A simplified, robust, and definitive backend for Render deployment.
# ==============================================================================

import os
import io
import magic
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import docx
import PyPDF2
from PIL import Image

# --- Configuration ---
# This remains the same. It securely loads the key from Render Secrets.
try:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    raise RuntimeError(f"CRITICAL ERROR during configuration: {e}")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- AI Model Configuration (Simplified & Corrected) ---
text_model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# --- PERSONA PROMPTS ---
# (These remain identical to the previous version)
VERITAS_TEXT_PROMPT = """You are the Clarity Engine from Pearl AI..."""
VERITAS_VISION_SIMULATION_PROMPT = """You are the Clarity Engine from Pearl AI..."""

# --- Helper Function for File Reading (Identical) ---
def read_text_from_file(file_storage):
    # (This function is identical to the previous version)
    filename = file_storage.filename.lower()
    try:
        if filename.endswith('.txt'):
            return file_storage.read().decode('utf-8', errors='ignore')
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_storage.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_storage.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        else:
            return f"[Unsupported Text File Type: {filename}]"
    except Exception as e:
        return f"[Error reading text from file: {filename}. It may be corrupted.]"

# --- API Endpoint Definition ---
@app.route('/process', methods=['POST'])
def process_directive():
    print("Received request...")
    if 'knowledgeBase' not in request.files or 'questionnaire' not in request.files:
        return jsonify({"error": "Request must contain both 'knowledgeBase' and 'questionnaire' file parts."}), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    directive_file = request.files.get('questionnaire')

    file_bytes = directive_file.read(2048)
    directive_file.seek(0)
    mime_type = magic.from_buffer(file_bytes, mime=True)
    is_image = mime_type.startswith('image/')
    
    try:
        if is_image:
            print("Image file detected. Initiating Vision Simulation...")
            image_data = directive_file.read()
            image_part = {'mime_type': mime_type, 'data': image_data}
            response = vision_model.generate_content([VERITAS_VISION_SIMULATION_PROMPT, image_part])
            result_text = response.text
        else:
            print("Text document detected. Initiating Intelligence Analysis...")
            knowledge_base_text = "".join([f"\n--- Start: {f.filename} ---\n{read_text_from_file(f)}\n--- End: {f.filename} ---\n" for f in knowledge_base_files])
            directive_text = read_text_from_file(directive_file)
            full_prompt = (f"{VERITAS_TEXT_PROMPT}\n\n--- START KNOWLEDGE BASE ---\n{knowledge_base_text}\n--- END KNOWLEDGE BASE ---\n\n--- START DIRECTIVE ---\n{directive_text}\n--- END DIRECTIVE ---")
            response = text_model.generate_content(full_prompt)
            result_text = response.text

        print("Successfully generated response.")
        return jsonify({"completedQuestionnaire": result_text})
    except Exception as e:
        print(f"Critical error during processing: {e}")
        return jsonify({"error": f"An error occurred with the AI model: {e}"}), 500

# --- Application Runner for Render ---
if __name__ == '__main__':
    # Gunicorn will run the 'app' object. This is for local testing.
    app.run(host='0.0.0.0', port=8080)
