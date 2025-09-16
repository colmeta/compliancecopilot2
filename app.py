# ==============================================================================
# PearlAI - Clarity Engine™ v2.0 (Production Backend)
# Author: Office of the CTO
# Stack: Python 3.10+, Flask, Requests, Google Gemini API
# Update: Switched to a direct requests-based API call for stability and
#         compatibility with the latest Google AI endpoints.
# ==============================================================================

import os
import io
import requests  # We will use this for direct API calls
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Import Document Parsing Libraries ---
import docx
import PyPDF2

# --- Configuration ---
try:
    GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
except KeyError:
    raise RuntimeError("CRITICAL ERROR: GOOGLE_API_KEY secret not found.")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Enables cross-origin requests from our Vercel frontend.

# --- AI Model Configuration ---
# We now define the endpoint URL and the model name here
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}"

MASTER_PROMPT = """
CONTEXT (Knowledge Base):
---
{knowledge_base_content}
---

YOUR TASK:
You are an expert AI assistant named Clarity Engine. You have been given the CONTEXT above from a company's internal documents. Now, analyze the following QUESTIONNAIRE, question by question. For each question, provide a detailed, accurate answer based ONLY on the information found in the CONTEXT. At the end of each answer, you MUST provide a confidence score in the format (Confidence: Low/Medium/High).

If you cannot find a relevant answer in the CONTEXT, you MUST state: "FLAG FOR HUMAN REVIEW: No information found in Knowledge Base for this question. (Confidence: Low)"

After answering all questions, provide a final summary list of all questions that were flagged for human review.

QUESTIONNAIRE:
---
{questionnaire_content}
"""

# --- Helper Function for File Reading ---
def read_file_content(file_storage):
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
            return f"[Unsupported File Type: {filename}]"
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return f"[Error reading file: {filename}. It may be corrupted.]"

# --- API Endpoint Definition ---
@app.route('/process', methods=['POST'])
def process_questionnaire():
    print("Received request...")

    if 'knowledgeBase' not in request.files or 'questionnaire' not in request.files:
        return jsonify({"error": "Request must contain both 'knowledgeBase' and 'questionnaire' file parts."}), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    questionnaire_file = request.files.get('questionnaire')

    try:
        knowledge_base_text = ""
        for file in knowledge_base_files:
            knowledge_base_text += f"\n\n--- FILE: {file.filename} ---\n{read_file_content(file)}"
        
        questionnaire_text = read_file_content(questionnaire_file)
        print("Successfully extracted text from all files.")
    except Exception as e:
        print(f"Critical error during file processing: {e}")
        return jsonify({"error": f"Could not process files: {e}"}), 500

    try:
        full_prompt = MASTER_PROMPT.format(
            knowledge_base_content=knowledge_base_text,
            questionnaire_content=questionnaire_text
        )

        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}

        print("Sending direct request to Google API...")
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            # Pass Google's error message directly to the client for better debugging
            error_message = f"Google API request failed: {response.status_code} {response.text}"
            print(error_message)
            raise Exception(error_message)
            
        response_data = response.json()
        print("Received successful response from Google API.")
        
        completed_questionnaire = response_data['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        print(f"Error during Google API call: {e}")
        return jsonify({"error": f"An error occurred with the AI model: {e}"}), 500

    print("Sending successful response back to client.")
    return jsonify({"completedQuestionnaire": completed_questionnaire})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
