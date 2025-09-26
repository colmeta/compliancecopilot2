# ==============================================================================
# tasks.py
# Pearl AI - "CLARITY" Engine v7.1 (Final Engine Integration)
# This is the "brain" of the operation. The complete AI logic lives here.
# ==============================================================================

import os
import base64
import io
import json
import re

from celery_worker import celery_app
import google.generativeai as genai

# Document Processing Libraries
import PyPDF2
import docx
from PIL import Image


# ==============================================================================
# 1. THE LOGIC DROP-IN: ALL HELPERS AND CONSTANTS ADDED HERE
# ==============================================================================

# --- All 7 Domain-Specific Intelligence Accelerators ---

CLARITY_SECURITY_INTELLIGENCE = """You are CLARITY Security Intelligence Accelerator...""" # (Your full prompt text)
CLARITY_LEGAL_INTELLIGENCE = """You are CLARITY Legal Intelligence Accelerator...""" # (Your full prompt text)
CLARITY_FINANCIAL_INTELLIGENCE = """You are CLARITY Financial Intelligence Accelerator...""" # (Your full prompt text)
CLARITY_CORPORATE_INTELLIGENCE = """You are CLARITY Corporate Intelligence Accelerator...""" # (Your full prompt text)
CLARITY_HEALTHCARE_INTELLIGENCE = """You are CLARITY Healthcare Intelligence Accelerator...""" # (Your full prompt text)
CLARITY_PROPOSAL_INTELLIGENCE = """You are CLARITY Proposal Intelligence Accelerator, Pearl AI's advanced government contract and RFP proposal writing system...""" # (Your full prompt text)
CLARITY_ENGINEERING_INTELLIGENCE = """You are CLARITY Engineering Intelligence Accelerator, Pearl AI's advanced technical document analysis system for engineers and construction professionals...""" # (Your full prompt text)


def detect_domain_context(filenames, directive_text=""):
    """Enhanced v6.0 domain detection for all document types"""
    legal_indicators = ['contract', 'lawsuit', 'litigation', 'agreement', 'court', 'legal', 'case', 'brief', 'deposition', 'discovery', 'attorney']
    financial_indicators = ['audit', 'financial', 'accounting', 'tax', 'balance', 'income', 'cash flow', 'gaap']
    security_indicators = ['intelligence', 'surveillance', 'threat', 'security', 'investigation', 'suspect', 'police']
    healthcare_indicators = ['medical', 'patient', 'clinical', 'healthcare', 'diagnosis', 'treatment', 'pharma', 'hipaa']
    proposal_indicators = ['request for proposal', 'rfp', 'solicitation', 'bid', 'tender', 'statement of work', 'sow', 'government contract']
    engineering_indicators = ['blueprint', 'technical specification', 'engineering drawing', 'construction document', 'schematic']
    corporate_indicators = ['strategy', 'business', 'corporate', 'merger', 'acquisition', 'compliance', 'market', 'stakeholder']

    all_text = directive_text.lower() + " ".join(filenames)

    domain_scores = {
        'legal': sum(1 for indicator in legal_indicators if indicator in all_text),
        'financial': sum(1 for indicator in financial_indicators if indicator in all_text),
        'security': sum(1 for indicator in security_indicators if indicator in all_text),
        'healthcare': sum(1 for indicator in healthcare_indicators if indicator in all_text),
        'proposal': sum(1 for indicator in proposal_indicators if indicator in all_text),
        'engineering': sum(1 for indicator in engineering_indicators if indicator in all_text),
        'corporate': sum(1 for indicator in corporate_indicators if indicator in all_text)
    }

    max_domain = max(domain_scores, key=domain_scores.get)
    return max_domain if domain_scores[max_domain] > 0 else 'corporate'


def get_domain_accelerator(domain):
    """Return the appropriate domain-specific intelligence accelerator"""
    accelerators = {
        'legal': CLARITY_LEGAL_INTELLIGENCE, 'financial': CLARITY_FINANCIAL_INTELLIGENCE,
        'security': CLARITY_SECURITY_INTELLIGENCE, 'healthcare': CLARITY_HEALTHCARE_INTELLIGENCE,
        'corporate': CLARITY_CORPORATE_INTELLIGENCE, 'proposal': CLARITY_PROPOSAL_INTELLIGENCE,
        'engineering': CLARITY_ENGINEERING_INTELLIGENCE,
    }
    return accelerators.get(domain, CLARITY_CORPORATE_INTELLIGENCE)


def get_domain_title(domain):
    """Return professional domain title"""
    titles = {
        'legal': 'Legal Intelligence Analysis', 'financial': 'Financial Intelligence Analysis',
        'security': 'Security Intelligence Analysis', 'healthcare': 'Healthcare Intelligence Analysis',
        'corporate': 'Corporate Intelligence Analysis', 'proposal': 'Proposal Intelligence Generation',
        'engineering': 'Engineering Document Analysis',
    }
    return titles.get(domain, 'Corporate Intelligence Analysis')


def advanced_text_extraction(filename, content_base64):
    """Processes a Base64 encoded file and returns its text content."""
    # (This function is from the previous step, unchanged)
    print(f"WORKER: Extracting text from '{filename}'...")
    try:
        content_bytes = base64.b64decode(content_base64)
        file_stream = io.BytesIO(content_bytes)
        content, metadata_type = "", ""
        if filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file_stream)
            content = "".join([f"\n--- PAGE {i+1} ---\n{page.extract_text() or ''}" for i, page in enumerate(pdf_reader.pages)])
            metadata_type = f"PDF ({len(pdf_reader.pages)} pages)"
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(file_stream)
            content = "\n".join([para.text for para in doc.paragraphs])
            metadata_type = "DOCX"
        else:
            content = content_bytes.decode('utf-8', errors='ignore')
            metadata_type = "Plain Text"
        return f"[CLARITY DOCUMENT: {filename} | TYPE: {metadata_type}]\n{content}\n"
    except Exception as e:
        return f"[ERROR EXTRACTING {filename}: {e}]\n"


def process_image(content_base64):
    """Decodes a base64 image for the AI model."""
    try:
        return Image.open(io.BytesIO(base64.b64decode(content_base64)))
    except Exception: return None


# ==============================================================================
# THE ASYNCHRONOUS "HEART" OF THE CLARITY ENGINE
# ==============================================================================

@celery_app.task(name='tasks.run_clarity_analysis', bind=True)
def run_clarity_analysis(self, user_directive, uploaded_files_data):
    """
    This is the definitive, all-powerful background task.
    """
    print(f"WORKER (Job ID: {self.request.id}): Starting clarity analysis.")

    try:
        genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-pro')

        all_text_intel, visual_intel_sources, file_names = "", [], []
        for file_data in uploaded_files_data:
            filename, content_base64, content_type = file_data['filename'], file_data['content_base64'], file_data['content_type']
            file_names.append(filename.lower())
            if content_type.startswith('image/'):
                img = process_image(content_base64)
                if img: visual_intel_sources.append({'filename': filename, 'image': img})
            else:
                all_text_intel += advanced_text_extraction(filename, content_base64)

        # ==============================================================================
        # 2. CONNECT THE WIRES: The "True Intelligence" Logic Block Starts Here
        # ==============================================================================
        
        master_prompt = ""
        all_intel_for_detection = user_directive.lower() + " ".join(file_names)
        
        # Heuristic to detect a proposal-writing task
        is_proposal_task = any(keyword in all_intel_for_detection for keyword in ['proposal', 'rfp', 'solicitation', 'bid']) and len(uploaded_files_data) > 0

        if is_proposal_task:
            print(f"WORKER: Detected PROPOSAL task.")
            # Find RFP doc, assuming it has a keyword or is the first file
            rfp_doc_index = next((i for i, name in enumerate(file_names) if any(kw in name for kw in ['rfp', 'solicitation'])), 0)
            
            rfp_data = uploaded_files_data[rfp_doc_index]
            rfp_content = advanced_text_extraction(rfp_data['filename'], rfp_data['content_base64'])
            
            company_content = "".join([advanced_text_extraction(f['filename'], f['content_base64']) for i, f in enumerate(uploaded_files_data) if i != rfp_doc_index])

            master_prompt = f"""
            {CLARITY_PROPOSAL_INTELLIGENCE}

            MISSION: Generate a comprehensive, compliant, and near-complete proposal draft.
            PRIMARY DOCUMENT (RFP): {rfp_content}
            SUPPORTING INTELLIGENCE (COMPANY PROFILE): {company_content if company_content else "No company profile provided. Identify all areas where company information is required."}
            """
        else:
            print(f"WORKER: Detected GENERAL INTELLIGENCE task.")
            domain = detect_domain_context(file_names, user_directive)
            domain_accelerator = get_domain_accelerator(domain)
            domain_title = get_domain_title(domain)

            if not user_directive: user_directive = f"Provide a comprehensive {domain} intelligence analysis of the provided documents."

            master_prompt = f"""
            {domain_accelerator}

            OPERATION INTELLIGENCE HEADER:
            🎯 Domain: {domain_title}
            
            PRIMARY DIRECTIVE FROM COMMAND:
            {user_directive}

            SUPPORTING INTELLIGENCE DOSSIER (TEXT & DOCUMENT ANALYSIS):
            {all_text_intel if all_text_intel else "No text-based documents provided."}
            """

        # Define the required JSON output structure
        JSON_OUTPUT_INSTRUCTIONS = """
        IMPORTANT: Your final output MUST be a valid JSON object. Do not include any text, notes, or markdown formatting like ```json before or after the JSON object.
        The JSON object must have this exact structure:
        {"executive_summary": "string", "key_findings": ["string"], "actionable_recommendations": ["string"], "confidence_score": "string", "data_gaps": ["string"]}
        """
        
        final_prompt = master_prompt + "\n" + JSON_OUTPUT_INSTRUCTIONS
        final_prompt_parts = [final_prompt]

        if visual_intel_sources:
            final_prompt_parts.append("\n--- VISUAL INTELLIGENCE ANALYSIS ---\n")
            for vis in visual_intel_sources:
                final_prompt_parts.extend([f"Analyzing visual source: {vis['filename']}", vis['image']])

        print("WORKER: Master prompt constructed. Calling Google AI...")
        response = model.generate_content(final_prompt_parts)

        # --- Parse and Validate the AI's JSON Output ---
        cleaned_output = response.text.strip().replace('```json', '').replace('```', '').strip()
        try:
            parsed_json = json.loads(cleaned_output)
            print("WORKER: Successfully parsed JSON.")
            return parsed_json
        except json.JSONDecodeError:
            error_json = {"executive_summary": "CRITICAL AI ERROR", "key_findings": ["The AI model failed to produce valid JSON."], "raw_ai_output": cleaned_output}
            return error_json

    except Exception as e:
        print(f"WORKER FATAL ERROR (Job ID: {self.request.id}): {e}")
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise
