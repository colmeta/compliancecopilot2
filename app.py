# ==============================================================================
# Pearl AI - "NEXUS" Intelligence Engine v3.1 (Fixed Visual Intelligence)
# Classified-Level Intelligence Analysis Platform
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

# --- UPDATED FUSION ANALYST PROMPT ---
NEXUS_FUSION_ANALYST_PROMPT = """You are NEXUS, the world's most advanced Multi-Source Intelligence Fusion system. Your sole purpose is to synthesize ALL sources of intelligence—text (INTEL), images (IMINT), and audio (AUDINT)—into a single, unified, and actionable brief.

🔥 CRITICAL FUSION DIRECTIVE:
You will receive a package of mixed-media intelligence files and a primary directive. Your analysis MUST treat all sources as interconnected. A detail in an image may be the key to understanding a text report. A word in a transcript may explain an action in an image.

🚨 **FAILURE TO FUSE ALL SOURCES IS A MISSION-CRITICAL FAILURE.** 🚨

ANALYTICAL FRAMEWORK (APPLY ACROSS ALL SOURCES):

1.  **ENTITY EXTRACTION & CORRELATION:**
    - Identify all persons, organizations, vehicles, locations, and assets from ALL sources.
    - **CRITICAL:** Correlate entities across all files. If a vehicle appears in IMINT, find mentions of it in INTEL. If a person is named in INTEL, find them in IMINT.

2.  **TIMELINE RECONSTRUCTION:**
    - Build a chronological event log. Use timestamps from reports, visual cues from images (shadows, clocks, known events), and conversation times from transcripts. Map the entire operational flow.

3.  **GEOSPATIAL ANALYSIS:**
    - Identify all locations from ALL sources. Use architectural clues in images, location names in reports, and background sounds in audio.
    - **CRITICAL:** Plot the movement of entities between these identified locations to map the operational geography.

4.  **BEHAVIORAL ANALYSIS (Multi-Modal):**
    - Synthesize psychological profiles. Use text reports for background, IMINT for body language and micro-expressions (stress, deception), and AUDINT for vocal stress indicators.

5.  **NETWORK ANALYSIS:**
    - Map the relationships between all identified entities. Use text reports for known affiliations and IMINT/AUDINT to confirm meetings and communications.

OUTPUT FORMAT - CLASSIFIED FUSION BRIEF:

🏴 **EXECUTIVE SUMMARY**: [30-word critical assessment, fusing all intelligence sources.]

⏳ **RECONSTRUCTED OPERATIONAL TIMELINE**: [A chronological list of events, citing the source for each entry (e.g., "H-72: Subject Alpha arrives EBB - Source: INTEL_REPORT_01, IMINT_01").]

🔗 **CRITICAL INTELLIGENCE FUSION POINTS**:
    - **ENTITY CORRELATION:** [List all key entities (people, vehicles) and cite every file in which they appear. E.g., "Toyota Hilux (UBE 882X): Sighted in IMINT_02 (Cafe) and IMINT_03 (Warehouse)."]
    - **GEOSPATIAL LINK:** [State the critical location link. E.g., "The vehicle linking the suspect meeting to the operational staging area is the Toyota Hilux, proving the warehouse is the 'final party' location."]

👤 **SUBJECT PROFILES (Fused Intelligence)**: [Profiles synthesized from both text and visual/audio intelligence.]

🌐 **NETWORK ANALYSIS**: [Relationship map based on all sources.]

🚨 **IMMEDIATE THREATS & OPERATIONAL WINDOWS**: [Fused assessment.]

🎯 **ACTIONABLE RECOMMENDATIONS (Prioritized)**:
    1.  **SURVEILLANCE:** [Specific targets and locations derived from the fusion.]
    2.  **INTERDICTION:** [Specific targets and locations.]
    3.  **WARRANTS/LEGAL:** [Specific evidence points to use for probable cause (e.g., "The visual correlation of the vehicle from a known criminal meeting to the warehouse location...")]

📋 **COLLECTION REQUIREMENTS**: [Intelligence gaps requiring field teams.]

🎯 **TARGET PACKAGES**: [Prioritized subjects for further investigation.]

⚖️ **LEGAL CONSIDERATIONS**: [Jurisdictional and evidence requirements.]

Analyze with the understanding that national security depends on your accuracy."""

# --- VISUAL-ONLY ANALYSIS PROMPT ---
NEXUS_VISUAL_ONLY_PROMPT = """You are NEXUS Visual Intelligence Division, conducting surveillance analysis on provided images.

🔍 COMPREHENSIVE VISUAL INTELLIGENCE ANALYSIS:

For each image provided, conduct detailed analysis of:

1. **SUBJECT IDENTIFICATION**
   - Physical descriptions (age, gender, build, clothing)
   - Behavioral indicators (stress, alertness, operational awareness)
   - Professional assessment (likely occupation, skills, threat level)

2. **VEHICLE/ASSET IDENTIFICATION**
   - Vehicle make, model, color, license plates
   - Condition, modifications, operational significance
   - Movement patterns and positioning

3. **LOCATION ANALYSIS**
   - Geographic indicators and architectural features
   - Operational significance of location choice
   - Security considerations and tactical assessment

4. **OPERATIONAL ASSESSMENT**
   - Meeting dynamics and relationship indicators
   - Surveillance awareness and counter-surveillance
   - Threat level and immediate concerns

5. **INTELLIGENCE CORRELATIONS**
   - Cross-reference subjects, vehicles, and locations between images
   - Establish operational timeline and movement patterns
   - Identify the complete operational picture

Provide tactical intelligence suitable for immediate field deployment."""

# --- Enhanced Helper Functions ---
def generate_operation_id():
    """Generate unique operation ID for tracking"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_hex = hashlib.md5(str(random.random()).encode()).hexdigest()[:6].upper()
    return f"NEXUS-{timestamp}-{random_hex}"

def classify_content_sensitivity(content):
    """Assess information sensitivity level"""
    if not content:
        return "RESTRICTED"
        
    high_sensitivity_keywords = [
        'classified', 'secret', 'confidential', 'weapon', 'bomb', 'attack', 
        'target', 'operation', 'asset', 'source', 'intelligence', 'surveillance'
    ]
    
    content_lower = content.lower()
    sensitivity_score = sum(1 for keyword in high_sensitivity_keywords if keyword in content_lower)
    
    if sensitivity_score >= 5:
        return "TOP SECRET"
    elif sensitivity_score >= 3:
        return "SECRET"  
    elif sensitivity_score >= 1:
        return "CONFIDENTIAL"
    else:
        return "RESTRICTED"

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
                    print(f"[NEXUS] System overload. Retry in {wait_time:.1f}s... [{attempt + 1}/{max_retries}]")
                    time.sleep(wait_time)
                    continue
                else:
                    return "🚨 NEXUS SYSTEM OVERLOAD - ANALYSIS UNAVAILABLE"
            else:
                raise e
    
    return "NEXUS ANALYSIS FAILED - TECHNICAL MALFUNCTION"

def detect_file_type_advanced(file_storage):
    """Advanced file type detection with security assessment"""
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
        print(f"[NEXUS] File type detection error: {e}")
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
            char_count = len(content)
            
            metadata = f"""
[NEXUS DOCUMENT ANALYSIS]
Filename: {file_storage.filename}
File Hash: {file_hash}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Word Count: {word_count}
Character Count: {char_count}
Classification: {classify_content_sensitivity(content)}
Security Assessment: TEXT FILE - LOW RISK
"""
            return metadata + "\n" + content
            
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_storage.read()))
            content = "\n".join([para.text for para in doc.paragraphs])
            word_count = len(content.split())
            
            metadata = f"""
[NEXUS DOCUMENT ANALYSIS]
Filename: {file_storage.filename}
File Hash: {file_hash}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Document Type: Microsoft Word Document
Word Count: {word_count}
Classification: {classify_content_sensitivity(content)}
Security Assessment: DOCX FILE - METADATA PRESENT (POTENTIAL ATTRIBUTION)
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
[NEXUS DOCUMENT ANALYSIS]
Filename: {file_storage.filename}
File Hash: {file_hash}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Document Type: PDF Document
Page Count: {page_count}
Classification: {classify_content_sensitivity(text)}
Security Assessment: PDF FILE - POTENTIAL METADATA/TRACKING PRESENT
"""
            return metadata + text
            
        else:
            return f"""
[NEXUS SECURITY ALERT]
Filename: {file_storage.filename}
File Hash: {file_hash}
Status: UNSUPPORTED FILE TYPE
Security Risk: UNKNOWN
Recommendation: QUARANTINE FOR MANUAL ANALYSIS
"""
    except Exception as e:
        return f"""
[NEXUS CRITICAL ERROR]
Filename: {file_storage.filename}
Error: {str(e)}
Security Assessment: POTENTIALLY MALICIOUS OR CORRUPTED
Recommendation: IMMEDIATE ISOLATION AND FORENSIC ANALYSIS
"""

# --- API ENDPOINTS ---
@app.route('/', methods=['GET'])
def nexus_status():
    return jsonify({
        "system": "NEXUS Intelligence Analysis Platform",
        "status": "OPERATIONAL",
        "security_level": "CLASSIFIED",
        "capabilities": [
            "Multi-Source Intelligence Fusion",
            "Visual Intelligence Analysis",
            "Audio Intelligence Analysis",
            "Behavioral Analysis & Psychological Profiling", 
            "Signals Intelligence (SIGINT)",
            "Counterintelligence Operations",
            "Financial Intelligence (FININT)",
            "Social Network Analysis",
            "Predictive Intelligence",
            "Technical Intelligence (TECHINT)"
        ],
        "clearance_required": "TOP SECRET/SCI",
        "timestamp": datetime.now().isoformat(),
        "next_maintenance": (datetime.now() + timedelta(days=7)).isoformat()
    }), 200

@app.route('/process', methods=['POST'])
def nexus_analysis():
    operation_id = generate_operation_id()
    print(f"[NEXUS] {operation_id} - INTELLIGENCE OPERATION INITIATED")
    
    # Handle the case where only knowledgeBase is provided (images only scenario)
    if 'knowledgeBase' not in request.files:
        return jsonify({
            "error": "NO INTELLIGENCE SOURCES PROVIDED",
            "operation_id": operation_id,
            "required": ["knowledgeBase (at minimum)"],
            "security_note": "Intelligence operations require source materials"
        }), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    primary_target = request.files.get('questionnaire')
    
    # NEW: Handle images-only scenario
    if not primary_target and knowledge_base_files:
        print(f"[NEXUS] {operation_id} - VISUAL-ONLY INTELLIGENCE ANALYSIS")
        
        try:
            # Check if we have visual intelligence files
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
                    "files_received": [f.filename for f in knowledge_base_files],
                    "note": "Visual intelligence analysis requires image files"
                }), 400
            
            # Process any text files for context
            context_intel = ""
            if text_files:
                for text_file in text_files:
                    content = advanced_text_extraction(text_file)
                    context_intel += f"\n{'='*60}\nCONTEXT FILE: {text_file.filename}\n{'='*60}\n{content}"
            
            # Build multi-modal prompt for visual analysis
            analysis_prompt_parts = []
            
            if context_intel:
                analysis_prompt_parts.append(f"""
{NEXUS_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: TOP SECRET

CONTEXTUAL INTELLIGENCE:
{context_intel[:20000]}

VISUAL INTELLIGENCE ANALYSIS:
Analyze all provided images in conjunction with the above intelligence context. Correlate all visual elements with the textual intelligence to provide a comprehensive operational assessment.
""")
            else:
                analysis_prompt_parts.append(f"""
{NEXUS_VISUAL_ONLY_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: CONFIDENTIAL

VISUAL INTELLIGENCE ANALYSIS:
No contextual intelligence provided. Conduct standalone visual intelligence analysis of all provided surveillance images. Extract maximum intelligence value from visual sources alone.
""")
            
            # Add all images to the analysis
            print(f"[NEXUS] {operation_id} - Processing {len(image_files)} visual intelligence sources")
            for idx, image_file in enumerate(image_files, 1):
                try:
                    image_data = image_file.read()
                    image = Image.open(io.BytesIO(image_data))
                    analysis_prompt_parts.append(f"\n--- VISUAL INTELLIGENCE SOURCE {idx}: {image_file.filename} ---")
                    analysis_prompt_parts.append(image)
                except Exception as e:
                    print(f"[NEXUS] {operation_id} - Error processing image {image_file.filename}: {e}")
                    continue
            
            # Generate analysis
            analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
            
            # Format final intelligence brief
            classification_level = "TOP SECRET" if context_intel else "CONFIDENTIAL"
            final_brief = f"""
🔒 CLASSIFICATION: {classification_level}
🆔 OPERATION ID: {operation_id}
📅 ANALYSIS COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🏛️ ORIGINATING AGENCY: NEXUS Intelligence Division
📊 SOURCES ANALYZED: {len(knowledge_base_files)}
🎯 PRIMARY TARGET TYPE: Visual Intelligence

{'='*80}
NEXUS INTELLIGENCE BRIEF
{'='*80}

{analysis_result}

{'='*80}
END INTELLIGENCE BRIEF
{'='*80}

🚨 SECURITY NOTICE: This intelligence product is classified {classification_level}. 
Distribution is restricted to authorized personnel with appropriate security clearances.
Unauthorized disclosure is prohibited and punishable under applicable law.

🔐 NEXUS-{operation_id}
📞 For technical support or escalation: Contact NEXUS Operations Center
⚠️ Report security incidents immediately to Counter-Intelligence Division
"""
            
            print(f"[NEXUS] {operation_id} - VISUAL ANALYSIS COMPLETE - CLASSIFICATION: {classification_level}")
            return jsonify({"completedQuestionnaire": final_brief})
            
        except Exception as e:
            print(f"[NEXUS] {operation_id} - VISUAL ANALYSIS ERROR: {e}")
            return jsonify({
                "error": f"VISUAL INTELLIGENCE ANALYSIS FAILED: {str(e)}",
                "operation_id": operation_id,
                "classification": "SYSTEM ERROR"
            }), 500

    # EXISTING: Handle cases with questionnaire file
    if not primary_target:
        return jsonify({
            "error": "INCOMPLETE INTELLIGENCE PACKAGE",
            "operation_id": operation_id,
            "required": ["questionnaire OR visual intelligence in knowledgeBase"],
            "security_note": "Intelligence operations require target specification"
        }), 400

    # Advanced file analysis
    target_file_type = detect_file_type_advanced(primary_target)
    
    if target_file_type == 'suspicious_executable':
        return jsonify({
            "error": "SECURITY BREACH ATTEMPT DETECTED",
            "operation_id": operation_id,
            "threat_level": "CRITICAL",
            "action": "FILE QUARANTINED - SECURITY TEAM NOTIFIED"
        }), 403

    try:
        # Process intelligence sources
        intelligence_sources = []
        image_sources = []
        
        for idx, source_file in enumerate(knowledge_base_files, 1):
            source_type = detect_file_type_advanced(source_file)
            
            if source_type == 'document_intelligence':
                content = advanced_text_extraction(source_file)
                intelligence_sources.append(f"\n{'='*60}\nINTELLIGENCE SOURCE {idx}: {source_file.filename}\n{'='*60}\n{content}")
            elif source_type == 'visual_intelligence':
                image_sources.append(source_file)
                intelligence_sources.append(f"\n{'='*60}\nVISUAL SOURCE {idx}: {source_file.filename}\nTYPE: VISUAL INTELLIGENCE\nSTATUS: PROCESSED IN MULTI-MODAL ANALYSIS\n{'='*60}")
            else:
                intelligence_sources.append(f"\n{'='*60}\nINTELLIGENCE SOURCE {idx}: {source_file.filename}\nFILE TYPE: {source_type.upper()}\nSTATUS: QUEUED FOR SPECIALIZED ANALYSIS\n{'='*60}")

        combined_intelligence = "".join(intelligence_sources)

        # Execute analysis based on primary target type with multi-modal fusion
        if target_file_type == 'visual_intelligence':
            print(f"[NEXUS] {operation_id} - VISUAL INTELLIGENCE ANALYSIS WITH FUSION")
            
            analysis_prompt_parts = []
            analysis_prompt_parts.append(f"""
{NEXUS_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence)}

INTELLIGENCE CONTEXT:
{combined_intelligence[:35000]}

PRIMARY VISUAL TARGET: {primary_target.filename}

MULTI-SOURCE FUSION DIRECTIVE: Analyze primary visual target in conjunction with all intelligence sources. Cross-reference subjects, vehicles, locations between visual and textual intelligence. Provide comprehensive operational assessment.
""")
            
            # Add primary target image
            image_data = primary_target.read()
            image = Image.open(io.BytesIO(image_data))
            analysis_prompt_parts.append(f"\n--- PRIMARY VISUAL TARGET: {primary_target.filename} ---")
            analysis_prompt_parts.append(image)
            
            # Add additional visual sources
            for image_file in image_sources:
                try:
                    img_data = image_file.read()
                    img = Image.open(io.BytesIO(img_data))
                    analysis_prompt_parts.append(f"\n--- SUPPORTING VISUAL INTELLIGENCE: {image_file.filename} ---")
                    analysis_prompt_parts.append(img)
                except Exception as e:
                    print(f"[NEXUS] Error processing supporting image {image_file.filename}: {e}")
            
            analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
            
        else:
            # Handle text-based analysis (existing functionality)
            print(f"[NEXUS] {operation_id} - COMPREHENSIVE INTELLIGENCE ANALYSIS")
            target_content = advanced_text_extraction(primary_target)
            
            if image_sources:
                # Multi-modal analysis with text primary and visual supporting
                analysis_prompt_parts = []
                analysis_prompt_parts.append(f"""
{NEXUS_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

INTELLIGENCE DATABASE:
{combined_intelligence}

PRIMARY INTELLIGENCE TARGET:
{target_content}

MULTI-SOURCE FUSION DIRECTIVE: Analyze all sources together. Cross-reference textual intelligence with visual sources. Correlate subjects, vehicles, locations across all intelligence types.
""")
                
                # Add visual sources
                for image_file in image_sources:
                    try:
                        img_data = image_file.read()
                        img = Image.open(io.BytesIO(img_data))
                        analysis_prompt_parts.append(f"\n--- VISUAL INTELLIGENCE: {image_file.filename} ---")
                        analysis_prompt_parts.append(img)
                    except Exception as e:
                        print(f"[NEXUS] Error processing image {image_file.filename}: {e}")
                
                analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
            else:
                # Text-only analysis (original functionality)
                max_content_length = 45000
                if len(combined_intelligence) > max_content_length:
                    combined_intelligence = combined_intelligence[:max_content_length] + "\n\n[ADDITIONAL INTELLIGENCE SOURCES TRUNCATED]"
                
                analysis_prompt = f"""
{NEXUS_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

INTELLIGENCE DATABASE:
{combined_intelligence}

PRIMARY INTELLIGENCE TARGET:
{target_content}

COMPREHENSIVE ANALYSIS DIRECTIVE:
Execute full-spectrum intelligence analysis. Cross-reference all sources. Provide actionable intelligence for immediate deployment.
"""
                analysis_result = generate_with_retry(text_model, analysis_prompt)

        # Format final intelligence brief
        classification_level = classify_content_sensitivity(combined_intelligence)
        final_brief = f"""
🔒 CLASSIFICATION: {classification_level}
🆔 OPERATION ID: {operation_id}
📅 ANALYSIS COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🏛️ ORIGINATING AGENCY: NEXUS Intelligence Division
📊 SOURCES ANALYZED: {len(knowledge_base_files) + 1}
🎯 PRIMARY TARGET TYPE: {target_file_type.replace('_', ' ').title()}

{'='*80}
NEXUS INTELLIGENCE BRIEF
{'='*80}

{analysis_result}

{'='*80}
END INTELLIGENCE BRIEF
{'='*80}

🚨 SECURITY NOTICE: This intelligence product is classified {classification_level}. 
Distribution is restricted to authorized personnel with appropriate security clearances.
Unauthorized disclosure is prohibited and punishable under applicable law.

🔐 NEXUS-{operation_id}
📞 For technical support or escalation: Contact NEXUS Operations Center
⚠️ Report security incidents immediately to Counter-Intelligence Division
        """
        
        print(f"[NEXUS] {operation_id} - ANALYSIS COMPLETE - CLASSIFICATION: {classification_level}")
        return jsonify({"completedQuestionnaire": final_brief})
        
    except Exception as e:
        print(f"[NEXUS] {operation_id} - CRITICAL SYSTEM ERROR: {e}")
        return jsonify({
            "error": f"NEXUS SYSTEM MALFUNCTION: {str(e)}",
            "operation_id": operation_id,
            "classification": "SYSTEM ERROR",
            "action": "Contact NEXUS Technical Support immediately"
        }), 500

# --- Application Runner ---
if __name__ == '__main__':
    print("[NEXUS] Intelligence Analysis Platform initializing...")
    print("[NEXUS] Security protocols active")
    print("[NEXUS] Multi-modal fusion capabilities enabled")
    print("[NEXUS] System ready for classified operations")
    app.run(host='0.0.0.0', port=8080)
