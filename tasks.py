# ==============================================================================
# tasks.py
# Pearl AI - "CLARITY" Engine v7.0 (Asynchronous Production Edition)
# This file contains the "brain" of the operation.
# All heavy AI processing happens here, in the background.
# ==============================================================================

import os
import base64
import time
import io
import json

from celery_worker import celery_app
import google.generativeai as genai

# Document Processing Libraries
import PyPDF2
import docx
from PIL import Image

# --- The "Heart Transplant" Begins: All Intelligence Logic Moves Here ---

# Step 2: Upgrade advanced_text_extraction
def advanced_text_extraction(filename, content_base64):
    """
    The REAL, powerful text extraction function, now upgraded to work inside Celery.
    It takes a base64 string, decodes it, and processes the file based on its type.
    """
    print(f"WORKER: Extracting text from '{filename}'...")
    try:
        # Step 1: Decode from Base64 string back into raw bytes.
        content_bytes = base64.b64decode(content_base64)
        
        content = ""
        metadata = f"[CLARITY DOCUMENT INTELLIGENCE REPORT]\nFilename: {filename}\n"

        # Step 2: Use io.BytesIO to treat the in-memory bytes as a file.
        file_stream = io.BytesIO(content_bytes)

        if filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file_stream)
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or "[No text found on this page]"
                content += f"\n--- PAGE {i+1} ---\n{page_text}"
            metadata += f"Document Type: PDF ({len(pdf_reader.pages)} pages)\n"
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(file_stream)
            content = "\n".join([para.text for para in doc.paragraphs])
            metadata += "Document Type: DOCX\n"
        else: # Default to text
            content = content_bytes.decode('utf-8', errors='ignore')
            metadata += "Document Type: Plain Text\n"
            
        metadata += "Status: SUCCESSFULLY EXTRACTED\n"
        return metadata + content
    except Exception as e:
        print(f"WORKER ERROR: Failed to extract text from {filename}. Reason: {e}")
        return f"[CLARITY DOCUMENT INTELLIGENCE ERROR REPORT]\nFilename: {filename}\nError: {e}\nStatus: EXTRACTION FAILED\n"

# Helper function for image processing
def process_image(content_base64):
    """Decodes a base64 image and prepares it for the AI model."""
    try:
        image_bytes = base64.b64decode(content_base64)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print(f"WORKER ERROR: Could not process image file. Reason: {e}")
        return None

# Your existing helper functions from v6.1 go here...
# (detect_domain_context, get_domain_accelerator, etc.)
# ...

# Step 1: The AI "Engine" (your v6.1 logic) is placed inside the task.
@celery_app.task(name='tasks.run_clarity_analysis', bind=True)
def run_clarity_analysis(self, user_directive, uploaded_files_data):
    """
    This is the heart of the engine. It runs in a separate 'worker' process.
    """
    print(f"WORKER (Job ID: {self.request.id}): Starting clarity analysis.")

    try:
        # Re-initialize services inside the task
        if not os.environ.get('GOOGLE_API_KEY'):
            raise ValueError("WORKER ERROR: GOOGLE_API_KEY not set.")
        genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-pro')

        all_text_intel = ""
        visual_intel_sources = []
        file_names = []

        # --- Reconstruct and process files ---
        for file_data in uploaded_files_data:
            filename = file_data['filename']
            content_base64 = file_data['content_base64']
            content_type = file_data['content_type']
            
            file_names.append(filename.lower())
            
            if content_type.startswith('image/'):
                img = process_image(content_base64)
                if img:
                    visual_intel_sources.append({'filename': filename, 'image': img})
            else:
                all_text_intel += advanced_text_extraction(filename, content_base64) + "\n" + "="*80 + "\n"
        
        # --- v6.1 "True Intelligence" Task Identification ---
        all_intel_for_detection = user_directive.lower() + " ".join(file_names)
        is_proposal_task = any(keyword in all_intel_for_detection for keyword in ['proposal', 'rfp', 'solicitation', 'bid'])
        
        master_prompt = ""
        # You will add your full get_domain_accelerator, detect_domain_context, etc. here

        # For this example, we build a simple prompt, then add the JSON instructions.
        master_prompt = f"""
        PRIMARY DIRECTIVE FROM COMMAND:
        {user_directive}

        SUPPORTING INTELLIGENCE DOSSIER (TEXT & DOCUMENT ANALYSIS):
        {all_text_intel if all_text_intel else "No text-based documents provided. Rely on the user's directive and any visual intelligence."}
        """

        # --- Step 3: Implement the JSON Output ---
        JSON_OUTPUT_INSTRUCTIONS = """
        IMPORTANT: Your final output MUST be a valid JSON object.
        Do not include any text, notes, or markdown formatting like ```json before or after the JSON object.
        The JSON object must have the following structure:
        {
          "executive_summary": "A concise, one-paragraph summary of your complete analysis and key findings.",
          "key_findings": [
            "A bulleted list of the most critical insights derived from the data.",
            "Each bullet point should be a complete, actionable sentence."
          ],
          "actionable_recommendations": [
            "A bulleted list of clear next steps or strategic recommendations.",
            "If the directive was a question, provide the direct answer here."
          ],
          "confidence_score": "A percentage (e.g., '95%') indicating your confidence in the analysis based on the provided data.",
          "data_gaps": [
            "A bulleted list of any missing information that, if provided, would improve the analysis."
          ]
        }
        """
        
        final_prompt = master_prompt + "\n" + JSON_OUTPUT_INSTRUCTIONS

        # --- Prepare the final prompt parts for the model ---
        final_prompt_parts = [final_prompt]
        if visual_intel_sources:
            print(f"WORKER: Integrating {len(visual_intel_sources)} visual sources.")
            final_prompt_parts.append("\n--- VISUAL INTELLIGENCE ANALYSIS ---\n")
            for vis in visual_intel_sources:
                final_prompt_parts.append(f"Analyzing visual source: {vis['filename']}")
                final_prompt_parts.append(vis['image'])

        print("WORKER: Master prompt constructed. Calling Google AI...")
        response = model.generate_content(final_prompt_parts)

        print("WORKER: Received response from AI. Parsing JSON output...")
        
        # --- Parse and Validate the AI's JSON Output ---
        raw_output = response.text
        # Clean the output to remove potential markdown backticks
        cleaned_output = raw_output.strip().replace('```json', '').replace('```', '').strip()
        
        try:
            parsed_json = json.loads(cleaned_output)
            print("WORKER: Successfully parsed JSON.")
            return parsed_json
        except json.JSONDecodeError:
            print("WORKER CRITICAL ERROR: AI did not return valid JSON.")
            # If the AI fails, we still return a structured error
            error_json = {
                "executive_summary": "CRITICAL AI ERROR",
                "key_findings": ["The AI model failed to produce a valid JSON output."],
                "actionable_recommendations": ["This usually happens due to content safety filters or an unexpected model response. Try rephrasing your directive."],
                "confidence_score": "0%",
                "data_gaps": [],
                "raw_ai_output": cleaned_output # Include the malformed output for debugging
            }
            return error_json

    except Exception as e:
        print(f"WORKER FATAL ERROR (Job ID: {self.request.id}): {e}")
        # When a task fails, Celery needs to know about it.
        # This will set the task state to 'FAILURE'
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        # This custom exception will be propagated to the status check endpoint.
        raise Exception(f"An unexpected error occurred in the analysis worker: {e}")
