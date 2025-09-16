# ==============================================================================
# Pearl AI - "Veritas" Intelligence Engine v1.0 (Production Backend)
# Author: Office of the CTO
# Features: Handles PDF, DOCX, TXT, and simulates Image Analysis.
# ==============================================================================

import os
import io
import magic
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import docx
import PyPDF2

# --- Configuration ---
try:
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    raise RuntimeError("CRITICAL ERROR: GOOGLE_API_KEY secret not found.")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- AI Model Configuration ---
# We use both the standard and the vision model
text_model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# --- PERSONA PROMPTS ---
VERITAS_TEXT_PROMPT = """
You are the Clarity Engine, operating as a lead intelligence analyst for a national security agency. Your designation is 'Veritas.' Your sole directive is to analyze a chaotic, unstructured data dossier related to a major criminal investigation. You must synthesize all provided reports, witness statements, and geographic data to produce an 'Actionable Intelligence Briefing.'

YOUR METHODOLOGY:
1. Entity Extraction: Identify all key persons, vehicles, locations, and times mentioned in the dossier.
2. Pattern Recognition: Correlate recurring details across multiple, independent reports.
3. Hypothesis Generation: Based on the correlated patterns, generate the most probable hypotheses regarding suspect description, escape routes, and potential motives.
4. Intelligence Gaps: Crucially, identify the most critical pieces of *missing* information that would be required to advance the investigation.
5. Actionable Directives: Formulate your output as a series of direct, actionable intelligence tasks for investigative units to execute immediately."
"""

VERITAS_VISION_SIMULATION_PROMPT = """
You are the Clarity Engine, operating as a lead computer vision and intelligence analyst. Your designation is 'Veritas Vision.' You have been given an image file from a security camera network. Your task is to simulate a comprehensive analysis of this image and generate a plausible, detailed intelligence report.

YOUR SIMULATION DIRECTIVE:
1.  **Object Identification:** Identify key objects in the image (e.g., vehicles, people, specific items). Be descriptive (e.g., "blue Toyota sedan," "male, red shirt, black trousers").
2.  **Facial/License Plate Recognition (Simulated):** If a face or license plate is visible, invent a plausible but fictional identity or plate number. State that you have cross-referenced this with national databases. Example: "Facial recognition suggests a possible match with John Doe (ID: 12345), known associate of..." or "License plate UBA 123X is registered to a 2015 Toyota sedan."
3.  **Timeline Correlation (Simulated):** Invent plausible sightings of this same person or vehicle at other locations. Create a timeline. Example: "Cross-referencing CCTV network data, this same vehicle was sighted at Camera 11 (Jinja Road) at 14:32 and Camera 45 (Entebbe Road) at 15:01."
4.  **Predictive Analysis (Simulated):** Based on the timeline and location, generate a predictive hypothesis. Example: "The subject's trajectory suggests a high probability of movement towards the Bweyogerere residential area."
5.  **Actionable Intelligence:** Formulate your output as a clear intelligence briefing for field officers.
"""

# --- Helper Function for File Reading (Text Only) ---
def read_text_from_file(file_storage):
    # ... (Same as sentinel_backend_v1.py) ...
    # This function remains the same as the previous version.
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
    directive_file = request.files.get('questionnaire') # This can now be text OR an image

    # --- DETECT FILE TYPE OF THE DIRECTIVE ---
    # We read the first few bytes to determine if it's an image or text document
    file_bytes = directive_file.read(1024)
    directive_file.seek(0) # Reset file pointer after reading
    mime_type = magic.from_buffer(file_bytes, mime=True)
    
    is_image = mime_type.startswith('image/')
    
    try:
        if is_image:
            # --- IMAGE ANALYSIS PATH ---
            print("Image file detected. Initiating Vision Simulation...")
            image_parts = [{"mime_type": mime_type, "data": directive_file.read()}]
            response = vision_model.generate_content([VERITAS_VISION_SIMULATION_PROMPT, *image_parts])
            result_text = response.text
        else:
            # --- TEXT ANALYSIS PATH ---
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

# --- Application Runner ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
