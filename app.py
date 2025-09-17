# ==============================================================================
# Pearl AI - "Veritas" Intelligence Engine v1.5 (Final Combat Edition)
# Author: Office of the CTO
# Features: Handles PDF, DOCX, TXT, XLSX, and live Image Analysis.
# ==============================================================================

import os
import io
import magic
import pandas as pd
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import docx
import PyPDF2

# --- Configuration & Initialization ---
try:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    raise RuntimeError(f"CRITICAL ERROR during configuration: {e}")

app = Flask(__name__)
CORS(app)

text_model = genai.GenerativeModel('gemini-1.5-flash')
vision_model = genai.GenerativeModel('gemini-1.5-flash')

# --- PERSONA PROMPTS ---
VERITAS_TEXT_PROMPT = """You are the Clarity Engine from Pearl AI, operating as a lead intelligence analyst for a national security agency. Your designation is 'Veritas.' Your sole directive is to analyze a chaotic, unstructured data dossier related to a major criminal investigation. You must synthesize all provided reports, witness statements, and geographic data to produce an 'Actionable Intelligence Briefing.'

YOUR METHODOLOGY:
1. Entity Extraction: Identify all key persons, vehicles, locations, and times mentioned in the dossier.
2. Pattern Recognition: Correlate recurring details across multiple, independent reports.
3. Hypothesis Generation: Based on the correlated patterns, generate the most probable hypotheses regarding suspect description, escape routes, and potential motives.
4. Intelligence Gaps: Crucially, identify the most critical pieces of *missing* information that would be required to advance the investigation.
5. Actionable Directives: Formulate your output as a series of direct, actionable intelligence tasks for investigative units to execute immediately."
"""
# Note: A separate vision simulation prompt is no longer needed with gemini-1.5-flash's native capabilities.

# --- Helper Function for File Reading (Upgraded for Excel) ---
def read_text_from_file(file_storage):
    filename = file_storage.filename.lower()
    try:
        if filename.endswith('.txt'):
            return file_storage.read().decode('utf-8', errors='ignore')
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_storage.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_storage.read()))
            return "".join([page.extract_text() or "" for page in pdf_reader.pages])
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_storage.read()))
            return df.to_string()
        else:
            return f"[Unsupported Text File Type: {filename}]"
    except Exception as e:
        return f"[Error reading text from file: {filename}. It may be corrupted.]"

# --- API ENDPOINTS ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Pearl AI Clarity Engine is online."}), 200

@app.route('/process', methods=['POST'])
def process_directive():
    print("Received request at /process endpoint...")
    
    if 'knowledgeBase' not in request.files or 'questionnaire' not in request.files:
        return jsonify({"error": "Request must contain both 'knowledgeBase' and 'questionnaire' parts."}), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    directive_file = request.files.get('questionnaire')

    file_bytes = directive_file.read(2048)
    directive_file.seek(0)
    mime_type = magic.from_buffer(file_bytes, mime=True)
    is_image = mime_type.startswith('image/')
    
    try:
        if is_image:
            print("Image file detected. Initiating Vision Analysis...")
            image_data = directive_file.read()
            image_part = {'mime_type': mime_type, 'data': image_data}
            # Simple prompt for direct image analysis
            response = vision_model.generate_content(["Describe this image in detail from a security and intelligence perspective.", image_part]) 
            result_text = response.text
        else:
            print("Text/Data document detected. Initiating Intelligence Analysis...")
            knowledge_base_text = "".join([f"\n--- Start: {f.filename} ---\n{read_text_from_file(f)}\n--- End: {f.filename} ---\n" for f in knowledge_base_files])
            directive_text = read_text_from_file(directive_file)
            full_prompt = (f"{VERITAS_TEXT_PROMPT}\n\n--- START KNOWLEDGE BASE ---\n{knowledge_base_text}\n--- END KNOWLEDGE BASE ---\n\n--- START DIRECTIVE ---\n{directive_text}\n--- END DIRECTIVE ---")
            response = text_model.generate_content(full_prompt)
            result_text = response.text

        print("Successfully generated response.")
        return jsonify({"completedQuestionnaire": result_text})
    except Exception as e:
        print(f"Critical error during processing: {e}")
        return jsonify({"error": f"An error occurred with the AI model: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
