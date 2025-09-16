# ==============================================================================
# Pearl AI - "Veritas" Intelligence Engine v1.1 (Render Production Backend)
# Author: Office of the CTO
# Stack: Python, Flask, Google Cloud AI Platform
# Features: Handles PDF, DOCX, TXT, and simulates Image Analysis for Render deployment.
# ==============================================================================

import os
import io
import magic
from flask import Flask, request, jsonify
from flask_cors import CORS
import docx
import PyPDF2
from PIL import Image

# --- Import Google Cloud AI Platform Library ---
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

# --- Configuration ---
# For Render, you will set these as Environment Variables in your service dashboard.
# PROJECT_ID = Your Google Cloud Project ID
# LOCATION = The region for your project (e.g., "us-central1")
try:
    PROJECT_ID = os.environ.get('PROJECT_ID')
    LOCATION = os.environ.get('LOCATION')
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    raise RuntimeError(f"CRITICAL ERROR: Google Cloud environment variables not set. {e}")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- AI Model Configuration ---
text_model = GenerativeModel("gemini-pro")
vision_model = GenerativeModel("gemini-pro-vision")

# --- PERSONA PROMPTS (Updated for Pearl AI) ---
VERITAS_TEXT_PROMPT = """
You are the Clarity Engine from Pearl AI, operating as a lead intelligence analyst...
[...The rest of the Veritas Text Prompt is IDENTICAL to the previous version...]
"""

VERITAS_VISION_SIMULATION_PROMPT = """
You are the Clarity Engine from Pearl AI, operating as a lead computer vision and intelligence analyst...
[...The rest of the Veritas Vision Simulation Prompt is IDENTICAL to the previous version...]
"""

# --- Helper Function for File Reading (Text Only) ---
def read_text_from_file(file_storage):
    # ... (This function remains IDENTICAL to the previous version) ...
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
        return jsonify({"error": "Request must contain 'knowledgeBase' and 'questionnaire' parts."}), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    directive_file = request.files.get('questionnaire')

    # --- DETECT FILE TYPE OF THE DIRECTIVE ---
    file_bytes = directive_file.read(2048)
    directive_file.seek(0)
    mime_type = magic.from_buffer(file_bytes, mime=True)
    is_image = mime_type.startswith('image/')
    
    try:
        if is_image:
            # --- IMAGE ANALYSIS PATH (Updated for new library) ---
            print("Image file detected. Initiating Vision Simulation...")
            image_data = directive_file.read()
            image_part = Part.from_data(data=image_data, mime_type=mime_type)
            response = vision_model.generate_content([VERITAS_VISION_SIMULATION_PROMPT, image_part])
            result_text = response.text
        else:
            # --- TEXT ANALYSIS PATH (Updated for new library) ---
            print("Text document detected. Initiating Intelligence Analysis...")
            knowledge_base_text = ""
            for file in knowledge_base_files:
                knowledge_base_text += f"\n--- Start: {file.filename} ---\n"
                knowledge_base_text += read_text_from_file(file)
                knowledge_base_text += f"\n--- End: {file.filename} ---\n"
            
            directive_text = read_text_from_file(directive_file)
            
            full_prompt = (
                f"{VERITAS_TEXT_PROMPT}\n\n"
                f"--- START KNOWLEDGE BASE ---\n{knowledge_base_text}\n--- END KNOWLEDGE BASE ---\n\n"
                f"--- START DIRECTIVE ---\n{directive_text}\n--- END DIRECTIVE ---"
            )
            response = text_model.generate_content(full_prompt)
            result_text = response.text

        print("Successfully generated response.")
        return jsonify({"completedQuestionnaire": result_text})

    except Exception as e:
        print(f"Critical error during processing: {e}")
        return jsonify({"error": f"An error occurred with the AI model: {e}"}), 500

# --- Application Runner for Render ---
# Render's Gunicorn server will automatically find and run this 'app' object.
# A main block is not strictly necessary but good practice.
if __name__ == '__main__':
    # This part is for local testing. Render will use gunicorn.
    app.run(debug=True)
