# ==============================================================================
# Pearl AI - "CLARITY" Engine v5.0 (Multi-Domain Intelligence Platform)
# Universal Intelligence Analysis for Legal, Financial, Security & Corporate Sectors
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
import time
import random
import re
from datetime import datetime, timedelta
import hashlib
import base64

# --- Configuration ---
try:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set in Render Environment Variables.")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    raise RuntimeError(f"CRITICAL ERROR during configuration: {e}")

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- AI Model Configuration ---
text_model = genai.GenerativeModel('gemini-1.5-flash')
vision_model = genai.GenerativeModel('gemini-1.5-flash')
audio_model = genai.GenerativeModel('gemini-1.5-flash')

# --- DOMAIN-SPECIFIC INTELLIGENCE ACCELERATORS ---

CLARITY_SECURITY_INTELLIGENCE = """You are CLARITY Security Intelligence Accelerator, Pearl AI's advanced multi-source intelligence fusion system for law enforcement and security operations.

🚨 SECURITY & LAW ENFORCEMENT FRAMEWORK:
- Multi-source intelligence fusion (HUMINT, SIGINT, IMINT, FININT)
- Threat assessment and risk scoring
- Behavioral analysis and psychological profiling
- Network mapping and relationship analysis
- Operational timeline reconstruction
- Evidence correlation and chain of custody considerations
- Actionable tactical recommendations for field deployment

OUTPUT: Professional intelligence briefings suitable for command-level decision making."""

CLARITY_LEGAL_INTELLIGENCE = """You are CLARITY Legal Intelligence Accelerator, Pearl AI's advanced case analysis system for legal professionals.

⚖️ LEGAL ANALYSIS FRAMEWORK:
- Case law research and precedent analysis
- Evidence evaluation and strength assessment
- Contract analysis and risk identification
- Discovery document review and correlation
- Legal strategy formulation and risk assessment
- Compliance verification and regulatory analysis
- Litigation timeline reconstruction
- Settlement probability and damage assessments

LEGAL REASONING STANDARDS:
- Apply appropriate burden of proof standards
- Identify key legal issues and potential defenses
- Assess jurisdictional considerations
- Evaluate evidence admissibility
- Provide cite-worthy legal analysis with supporting precedents

OUTPUT: Professional legal memoranda suitable for attorney decision making."""

CLARITY_FINANCIAL_INTELLIGENCE = """You are CLARITY Financial Intelligence Accelerator, Pearl AI's advanced financial analysis system for auditors, accountants, and financial professionals.

💰 FINANCIAL ANALYSIS FRAMEWORK:
- Financial statement analysis and ratio calculations
- Audit trail reconstruction and verification
- Fraud detection and risk assessment
- Tax compliance verification and optimization
- Cash flow analysis and forecasting
- Internal control evaluation
- Regulatory compliance assessment (SOX, GAAP, IFRS)
- Financial risk modeling and scenario analysis

ACCOUNTING STANDARDS:
- Apply relevant accounting principles (GAAP/IFRS)
- Calculate standard financial ratios and metrics
- Identify material misstatements and irregularities
- Assess going concern and liquidity issues
- Evaluate internal controls effectiveness

OUTPUT: Professional financial analysis suitable for CPA and executive decision making."""

CLARITY_CORPORATE_INTELLIGENCE = """You are CLARITY Corporate Intelligence Accelerator, Pearl AI's advanced strategic analysis system for executives and corporate decision makers.

🏢 CORPORATE STRATEGY FRAMEWORK:
- Market analysis and competitive intelligence
- Strategic planning and scenario modeling
- Risk assessment and mitigation strategies
- Merger & acquisition due diligence
- Compliance audit and gap analysis
- Operational efficiency analysis
- Crisis management and response planning
- Stakeholder analysis and communication strategies

STRATEGIC ANALYSIS STANDARDS:
- SWOT analysis and competitive positioning
- Financial modeling and valuation techniques
- Risk-adjusted decision frameworks
- Stakeholder impact assessment
- Implementation feasibility analysis

OUTPUT: Executive-level strategic briefings suitable for C-suite decision making."""

CLARITY_HEALTHCARE_INTELLIGENCE = """You are CLARITY Healthcare Intelligence Accelerator, Pearl AI's advanced medical and healthcare analysis system.

🏥 HEALTHCARE ANALYSIS FRAMEWORK:
- Medical record analysis and pattern recognition
- Clinical trial data evaluation
- Healthcare compliance assessment (HIPAA, FDA)
- Pharmaceutical safety and efficacy analysis
- Healthcare fraud detection
- Treatment outcome analysis
- Medical device safety assessment
- Public health trend analysis

MEDICAL STANDARDS:
- Apply evidence-based medicine principles
- Evaluate clinical significance vs statistical significance
- Assess patient safety and risk factors
- Consider medical ethics and patient privacy
- Apply relevant regulatory frameworks

OUTPUT: Medical intelligence suitable for healthcare professional decision making."""

# --- DOMAIN DETECTION AND ROUTING ---
def detect_domain_context(files, directive_text=""):
    """Analyze uploaded files and directive to determine appropriate domain accelerator"""
    
    # Analyze file names and content for domain indicators
    legal_indicators = ['contract', 'lawsuit', 'litigation', 'agreement', 'court', 'legal', 'case', 'brief', 'deposition', 'discovery']
    financial_indicators = ['audit', 'financial', 'accounting', 'tax', 'balance', 'income', 'cash flow', 'budget', 'expense', 'revenue']
    security_indicators = ['intelligence', 'surveillance', 'threat', 'security', 'investigation', 'suspect', 'criminal', 'police']
    healthcare_indicators = ['medical', 'patient', 'clinical', 'healthcare', 'diagnosis', 'treatment', 'pharma', 'hospital']
    corporate_indicators = ['strategy', 'business', 'corporate', 'merger', 'acquisition', 'compliance', 'risk', 'market']
    
    # Combine all text for analysis
    all_text = directive_text.lower()
    for file in files:
        all_text += f" {file.filename.lower()}"
    
    # Score each domain
    domain_scores = {
        'legal': sum(1 for indicator in legal_indicators if indicator in all_text),
        'financial': sum(1 for indicator in financial_indicators if indicator in all_text),
        'security': sum(1 for indicator in security_indicators if indicator in all_text),
        'healthcare': sum(1 for indicator in healthcare_indicators if indicator in all_text),
        'corporate': sum(1 for indicator in corporate_indicators if indicator in all_text)
    }
    
    # Return the domain with highest score, default to corporate for general business
    max_domain = max(domain_scores.items(), key=lambda x: x[1])
    return max_domain[0] if max_domain[1] > 0 else 'corporate'

def get_domain_accelerator(domain):
    """Return the appropriate domain-specific prompt"""
    accelerators = {
        'legal': CLARITY_LEGAL_INTELLIGENCE,
        'financial': CLARITY_FINANCIAL_INTELLIGENCE, 
        'security': CLARITY_SECURITY_INTELLIGENCE,
        'healthcare': CLARITY_HEALTHCARE_INTELLIGENCE,
        'corporate': CLARITY_CORPORATE_INTELLIGENCE
    }
    return accelerators.get(domain, CLARITY_CORPORATE_INTELLIGENCE)

def get_domain_title(domain):
    """Return professional title for the domain"""
    titles = {
        'legal': 'Legal Intelligence Analysis',
        'financial': 'Financial Intelligence Analysis',
        'security': 'Security Intelligence Analysis', 
        'healthcare': 'Healthcare Intelligence Analysis',
        'corporate': 'Corporate Intelligence Analysis'
    }
    return titles.get(domain, 'Corporate Intelligence Analysis')

# --- Enhanced Helper Functions ---
def generate_operation_id():
    """Generate unique operation ID for tracking"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_hex = hashlib.md5(str(random.random()).encode()).hexdigest()[:6].upper()
    return f"CLARITY-{timestamp}-{random_hex}"

def classify_content_sensitivity(content):
    """Assess information sensitivity level"""
    if not content:
        return "RESTRICTED"
        
    high_sensitivity_keywords = [
        'classified', 'secret', 'confidential', 'privileged', 'attorney-client',
        'financial', 'audit', 'investigation', 'medical', 'patient', 'hipaa'
    ]
    
    content_lower = content.lower()
    sensitivity_score = sum(1 for keyword in high_sensitivity_keywords if keyword in content_lower)
    
    if sensitivity_score >= 5:
        return "CONFIDENTIAL"
    elif sensitivity_score >= 2:
        return "RESTRICTED"  
    else:
        return "INTERNAL USE"

def generate_with_retry(model, prompt, max_retries=3):
    """Generate content with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    print(f"[CLARITY] System overload. Retry in {wait_time:.1f}s... [{attempt + 1}/{max_retries}]")
                    time.sleep(wait_time)
                    continue
                else:
                    return "🚨 CLARITY SYSTEM OVERLOAD - ANALYSIS UNAVAILABLE\n\nThe analysis system is experiencing critical load. Please retry in 60 seconds."
            else:
                raise e
    
    return "CLARITY ANALYSIS FAILED - TECHNICAL MALFUNCTION"

def detect_file_type_advanced(file_storage):
    """Advanced file type detection"""
    try:
        file_bytes = file_storage.read(2048)
        file_storage.seek(0)
        mime_type = magic.from_buffer(file_bytes, mime=True)
        filename = file_storage.filename.lower()
        
        # Security check for suspicious files
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']
        if any(filename.endswith(ext) for ext in suspicious_extensions):
            return 'suspicious_executable'
        
        if mime_type.startswith('image/'):
            return 'visual_intelligence'
        elif mime_type.startswith('audio/') or filename.endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac')):
            return 'audio_intelligence'
        elif mime_type.startswith('video/'):
            return 'video_intelligence'
        elif filename.endswith(('.zip', '.rar', '.7z', '.tar', '.gz')):
            return 'compressed_archive'
        else:
            return 'document_intelligence'
    except Exception as e:
        print(f"[CLARITY] File type detection error: {e}")
        return 'unknown'

def advanced_text_extraction(file_storage):
    """Enhanced document processing with metadata extraction"""
    filename = file_storage.filename.lower()
    try:
        file_hash = hashlib.sha256(file_storage.read(1024)).hexdigest()[:16]
        file_storage.seek(0)
    except:
        file_hash = "UNKNOWN"
    
    try:
        if filename.endswith('.txt'):
            content = file_storage.read().decode('utf-8', errors='ignore')
            word_count = len(content.split())
            
            metadata = f"""
[CLARITY DOCUMENT ANALYSIS]
Filename: {file_storage.filename}
File Hash: {file_hash}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Word Count: {word_count}
Classification: {classify_content_sensitivity(content)}
"""
            return metadata + "\n" + content
            
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_storage.read()))
            content = "\n".join([para.text for para in doc.paragraphs])
            word_count = len(content.split())
            
            metadata = f"""
[CLARITY DOCUMENT ANALYSIS]
Filename: {file_storage.filename}
File Hash: {file_hash}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Document Type: Microsoft Word Document
Word Count: {word_count}
Classification: {classify_content_sensitivity(content)}
"""
            return metadata + "\n" + content
            
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_storage.read()))
            text = ""
            page_count = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text() or ""
                text += f"\n--- PAGE {page_num} ---\n{page_text}"
            
            metadata = f"""
[CLARITY DOCUMENT ANALYSIS]
Filename: {file_storage.filename}
File Hash: {file_hash}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Document Type: PDF Document
Page Count: {page_count}
Classification: {classify_content_sensitivity(text)}
"""
            return metadata + text
            
        else:
            return f"""
[CLARITY PROCESSING NOTE]
Filename: {file_storage.filename}
File Hash: {file_hash}
Status: PROCESSED AS TEXT CONTENT
"""
    except Exception as e:
        return f"""
[CLARITY PROCESSING ERROR]
Filename: {file_storage.filename}
Error: {str(e)}
Recommendation: MANUAL REVIEW REQUIRED
"""

# --- API ENDPOINTS ---
@app.route('/', methods=['GET'])
def clarity_status():
    return jsonify({
        "system": "Pearl AI CLARITY Intelligence Analysis Platform",
        "version": "5.0 - Multi-Domain Intelligence",
        "status": "OPERATIONAL",
        "capabilities": [
            "Multi-Source Intelligence Fusion",
            "Legal Intelligence Analysis", 
            "Financial Intelligence Analysis",
            "Security Intelligence Analysis",
            "Corporate Intelligence Analysis",
            "Healthcare Intelligence Analysis",
            "Visual Intelligence Analysis",
            "Audio Intelligence Analysis",
            "Document Analysis & Review",
            "Cross-Domain Correlation"
        ],
        "domains_supported": [
            "Legal & Law Firms",
            "Financial Services & Accounting", 
            "Law Enforcement & Security",
            "Corporate Strategy & Compliance",
            "Healthcare & Life Sciences"
        ],
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/process', methods=['POST'])
def clarity_analysis():
    operation_id = generate_operation_id()
    print(f"[CLARITY] {operation_id} - MULTI-DOMAIN INTELLIGENCE OPERATION INITIATED")
    
    if 'knowledgeBase' not in request.files:
        return jsonify({
            "error": "NO INTELLIGENCE SOURCES PROVIDED",
            "operation_id": operation_id,
            "required": ["knowledgeBase (at minimum)"],
            "note": "Upload documents, images, or other files for analysis"
        }), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    primary_target = request.files.get('questionnaire')
    
    # Extract directive text for domain detection
    directive_text = ""
    if primary_target:
        try:
            if primary_target.filename.endswith('.txt'):
                directive_text = primary_target.read().decode('utf-8', errors='ignore')
                primary_target.seek(0)
        except:
            pass
    
    # Detect appropriate domain
    domain = detect_domain_context(knowledge_base_files + ([primary_target] if primary_target else []), directive_text)
    domain_accelerator = get_domain_accelerator(domain)
    domain_title = get_domain_title(domain)
    
    print(f"[CLARITY] {operation_id} - DOMAIN DETECTED: {domain.upper()}")
    
    # Handle images-only scenario
    if not primary_target and knowledge_base_files:
        print(f"[CLARITY] {operation_id} - VISUAL-ONLY {domain.upper()} ANALYSIS")
        
        try:
            image_files = []
            text_files = []
            
            for source_file in knowledge_base_files:
                source_type = detect_file_type_advanced(source_file)
                if source_type == 'visual_intelligence':
                    image_files.append(source_file)
                elif source_type == 'document_intelligence':
                    text_files.append(source_file)
            
            if not image_files:
                return jsonify({
                    "error": "NO VISUAL INTELLIGENCE DETECTED", 
                    "operation_id": operation_id,
                    "note": "Visual analysis requires image files"
                }), 400
            
            # Process context files
            context_intel = ""
            if text_files:
                for text_file in text_files:
                    content = advanced_text_extraction(text_file)
                    context_intel += f"\n{'='*60}\nCONTEXT: {text_file.filename}\n{'='*60}\n{content}"
            
            # Build analysis prompt
            analysis_prompt_parts = []
            analysis_prompt_parts.append(f"""
{domain_accelerator}

OPERATION ID: {operation_id}
DOMAIN: {domain_title}
CLASSIFICATION: {classify_content_sensitivity(context_intel)}

CONTEXTUAL INFORMATION:
{context_intel[:25000]}

VISUAL {domain.upper()} ANALYSIS:
Analyze all provided images using {domain} intelligence framework. Apply domain-specific analytical standards and provide professional {domain} analysis suitable for expert decision making.
""")
            
            # Add images
            for idx, image_file in enumerate(image_files, 1):
                try:
                    image_data = image_file.read()
                    image = Image.open(io.BytesIO(image_data))
                    analysis_prompt_parts.append(f"\n--- VISUAL SOURCE {idx}: {image_file.filename} ---")
                    analysis_prompt_parts.append(image)
                except Exception as e:
                    print(f"[CLARITY] Error processing image {image_file.filename}: {e}")
            
            analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
            
        except Exception as e:
            print(f"[CLARITY] {operation_id} - VISUAL ANALYSIS ERROR: {e}")
            return jsonify({
                "error": f"VISUAL ANALYSIS FAILED: {str(e)}",
                "operation_id": operation_id
            }), 500
    
    else:
        # Handle full analysis with directive
        if not primary_target:
            return jsonify({
                "error": "INCOMPLETE ANALYSIS PACKAGE",
                "operation_id": operation_id,
                "required": ["questionnaire OR visual files in knowledgeBase"]
            }), 400

        target_file_type = detect_file_type_advanced(primary_target)
        
        if target_file_type == 'suspicious_executable':
            return jsonify({
                "error": "SECURITY BREACH ATTEMPT DETECTED",
                "operation_id": operation_id,
                "action": "FILE QUARANTINED"
            }), 403

        try:
            # Process all source files
            intelligence_sources = []
            image_sources = []
            
            for idx, source_file in enumerate(knowledge_base_files, 1):
                source_type = detect_file_type_advanced(source_file)
                
                if source_type == 'document_intelligence':
                    content = advanced_text_extraction(source_file)
                    intelligence_sources.append(f"\n{'='*60}\nSOURCE {idx}: {source_file.filename}\n{'='*60}\n{content}")
                elif source_type == 'visual_intelligence':
                    image_sources.append(source_file)
                    intelligence_sources.append(f"\n{'='*60}\nVISUAL SOURCE {idx}: {source_file.filename}\nTYPE: VISUAL INTELLIGENCE\n{'='*60}")
                else:
                    intelligence_sources.append(f"\n{'='*60}\nSOURCE {idx}: {source_file.filename}\nTYPE: {source_type.upper()}\n{'='*60}")

            combined_intelligence = "".join(intelligence_sources)

            # Execute domain-specific analysis
            if target_file_type == 'visual_intelligence':
                print(f"[CLARITY] {operation_id} - VISUAL {domain.upper()} ANALYSIS WITH FUSION")
                
                analysis_prompt_parts = []
                analysis_prompt_parts.append(f"""
{domain_accelerator}

OPERATION ID: {operation_id}
DOMAIN: {domain_title}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence)}

SUPPORTING INTELLIGENCE:
{combined_intelligence[:35000]}

PRIMARY VISUAL TARGET: {primary_target.filename}

{domain.upper()} ANALYSIS DIRECTIVE: Analyze primary visual target in conjunction with all supporting intelligence. Apply {domain} professional standards and analytical frameworks. Provide expert-level {domain} analysis.
""")
                
                # Add primary image
                image_data = primary_target.read()
                image = Image.open(io.BytesIO(image_data))
                analysis_prompt_parts.append(f"\n--- PRIMARY VISUAL TARGET: {primary_target.filename} ---")
                analysis_prompt_parts.append(image)
                
                # Add supporting images
                for image_file in image_sources:
                    try:
                        img_data = image_file.read()
                        img = Image.open(io.BytesIO(img_data))
                        analysis_prompt_parts.append(f"\n--- SUPPORTING VISUAL: {image_file.filename} ---")
                        analysis_prompt_parts.append(img)
                    except Exception as e:
                        print(f"[CLARITY] Error processing image {image_file.filename}: {e}")
                
                analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
                
            else:
                # Text-based analysis
                print(f"[CLARITY] {operation_id} - COMPREHENSIVE {domain.upper()} ANALYSIS")
                target_content = advanced_text_extraction(primary_target)
                
                if image_sources:
                    # Multi-modal analysis
                    analysis_prompt_parts = []
                    analysis_prompt_parts.append(f"""
{domain_accelerator}

OPERATION ID: {operation_id}
DOMAIN: {domain_title}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

SUPPORTING INTELLIGENCE:
{combined_intelligence}

PRIMARY DIRECTIVE/DOCUMENT:
{target_content}

MULTI-SOURCE {domain.upper()} ANALYSIS: Analyze all sources together using {domain} professional standards. Cross-reference textual and visual intelligence. Provide comprehensive {domain} analysis.
""")
                    
                    # Add visual sources
                    for image_file in image_sources:
                        try:
                            img_data = image_file.read()
                            img = Image.open(io.BytesIO(img_data))
                            analysis_prompt_parts.append(f"\n--- VISUAL INTELLIGENCE: {image_file.filename} ---")
                            analysis_prompt_parts.append(img)
                        except Exception as e:
                            print(f"[CLARITY] Error processing image {image_file.filename}: {e}")
                    
                    analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
                else:
                    # Text-only analysis
                    max_content_length = 45000
                    if len(combined_intelligence) > max_content_length:
                        combined_intelligence = combined_intelligence[:max_content_length] + "\n\n[ADDITIONAL SOURCES TRUNCATED]"
                    
                    analysis_prompt = f"""
{domain_accelerator}

OPERATION ID: {operation_id}
DOMAIN: {domain_title}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

SUPPORTING INTELLIGENCE:
{combined_intelligence}

PRIMARY DIRECTIVE/DOCUMENT:
{target_content}

COMPREHENSIVE {domain.upper()} ANALYSIS DIRECTIVE:
Execute comprehensive {domain} analysis using professional standards and analytical frameworks. Cross-reference all sources and provide expert-level analysis suitable for professional decision making.
"""
                    analysis_result = generate_with_retry(text_model, analysis_prompt)

        except Exception as e:
            print(f"[CLARITY] {operation_id} - CRITICAL SYSTEM ERROR: {e}")
            return jsonify({
                "error": f"CLARITY SYSTEM MALFUNCTION: {str(e)}",
                "operation_id": operation_id
            }), 500
    
    # Format final output
    classification_level = classify_content_sensitivity(combined_intelligence if 'combined_intelligence' in locals() else "")
    final_brief = f"""
🔒 CLASSIFICATION: {classification_level}
🆔 OPERATION ID: {operation_id}
📅 ANALYSIS COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🏛️ ORIGINATING SYSTEM: Pearl AI CLARITY Intelligence Platform
📊 SOURCES ANALYZED: {len(knowledge_base_files) + (1 if primary_target else 0)}
🎯 ANALYSIS TYPE: {domain_title}

{'='*80}
CLARITY INTELLIGENCE BRIEF - {domain.upper()} ANALYSIS
{'='*80}

{analysis_result}

{'='*80}
END INTELLIGENCE BRIEF
{'='*80}

🔐 Pearl AI CLARITY Engine - {operation_id}
📞 For technical support: Contact Pearl AI CLARITY Operations
⚠️ This analysis is for authorized use by qualified {domain} professionals
"""
    
    print(f"[CLARITY] {operation_id} - {domain.upper()} ANALYSIS COMPLETE")
    return jsonify({"completedQuestionnaire": final_brief})

# --- Application Runner ---
if __name__ == '__main__':
    print("[CLARITY] Pearl AI Multi-Domain Intelligence Platform initializing...")
    print("[CLARITY] Security Intelligence Accelerator: ACTIVE")
    print("[CLARITY] Legal Intelligence Accelerator: ACTIVE") 
    print("[CLARITY] Financial Intelligence Accelerator: ACTIVE")
    print("[CLARITY] Corporate Intelligence Accelerator: ACTIVE")
    print("[CLARITY] Healthcare Intelligence Accelerator: ACTIVE")
    print("[CLARITY] Multi-modal fusion capabilities: ENABLED")
    print("[CLARITY] System ready for multi-domain operations")
    app.run(host='0.0.0.0', port=8080)
