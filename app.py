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

# --- PERSONA PROMPTS (Unchanged) ---
VERITAS_TEXT_PROMPT = """You are the Clarity Engine from Pearl AI..."""
VERITAS_VISION_SIMULATION_PROMPT = """You are the Clarity Engine from Pearl AI..."""

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
        # --- NEW EXCEL HANDLING LOGIC ---
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_storage.read()))
            # Convert the entire dataframe to a clean, string representation
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
        return jsonify({"error": "Request must contain 'knowledgeBase' and 'questionnaire' parts."}), 400

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
            # NOTE: We now use the REAL Vision prompt, not a simulation prompt.
            response = vision_model.generate_content(image_part) 
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
```**Note:** In the `app.py` above, I have removed the "Vision Simulation" prompt. With `gemini-1.5-flash`, we no longer need to simulate. It will perform a **real** analysis of the image you provide.

#### **Asset 3: The Final `index.html`**

**Description:** The text has been updated to explicitly mention Excel and Image analysis.

```html
<!-- ... (header and other sections are the same) ... -->
<div class="mb-6">
    <label for="knowledgeBase" class="label-text">1. Upload Knowledge Base</label>
    <p class="label-description">Upload policies, logs, reports, etc. (.txt, .pdf, .docx, .xlsx). Multiple files allowed.</p>
    <input type="file" id="knowledgeBase" multiple required class="custom-file-input" />
</div>

<div id="input-dossier" class="mb-8">
    <label for="questionnaire" class="label-text">2. Upload Your Task File</label>
    <p class="label-description">Upload a questionnaire OR a single image (.jpg, .png) for analysis.</p>
    <input type="file" id="questionnaire" required class="custom-file-input" />
</div>
<!-- ... (rest of the file is the same) ... -->
