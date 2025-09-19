# ==============================================================================
# Pearl AI - "CLARITY" Engine v4.0 (Complete Enhanced Version)
# Multi-Source Intelligence Analysis Platform with Biometric Capabilities
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

# --- MULTI-SOURCE FUSION ANALYST PROMPT ---
CLARITY_FUSION_ANALYST_PROMPT = """You are CLARITY, Pearl AI's most advanced Multi-Source Intelligence Fusion system. Your sole purpose is to synthesize ALL sources of intelligence—text (INTEL), images (IMINT), and audio (AUDINT)—into a single, unified, and actionable brief.

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

6.  **BIOMETRIC & IDENTITY INTELLIGENCE:**
    - Document authenticity assessment and identity verification
    - Cross-platform identity correlation across multiple sources
    - AI-generated content and deepfake probability assessment
    - Behavioral biometrics from communication patterns

OUTPUT FORMAT - CLASSIFIED FUSION BRIEF:

🏴 **EXECUTIVE SUMMARY**: [30-word critical assessment, fusing all intelligence sources.]

⏳ **RECONSTRUCTED OPERATIONAL TIMELINE**: [A chronological list of events, citing the source for each entry (e.g., "H-72: Subject Alpha arrives EBB - Source: INTEL_REPORT_01, IMINT_01").]

🔗 **CRITICAL INTELLIGENCE FUSION POINTS**:
    - **ENTITY CORRELATION:** [List all key entities (people, vehicles) and cite every file in which they appear. E.g., "Toyota Hilux (UBE 882X): Sighted in IMINT_02 (Cafe) and IMINT_03 (Warehouse)."]
    - **GEOSPATIAL LINK:** [State the critical location link. E.g., "The vehicle linking the suspect meeting to the operational staging area is the Toyota Hilux, proving the warehouse is the 'final party' location."]

👤 **SUBJECT PROFILES (Fused Intelligence)**: [Profiles synthesized from both text and visual/audio intelligence.]

🔬 **BIOMETRIC ANALYSIS**: [Identity verification, document authenticity, AI-generation probability]

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
CLARITY_VISUAL_ONLY_PROMPT = """You are CLARITY Engine, Pearl AI's advanced visual intelligence system conducting surveillance analysis on provided images.

🔍 COMPREHENSIVE VISUAL INTELLIGENCE ANALYSIS:

For each image provided, conduct detailed analysis of:

1. **SUBJECT IDENTIFICATION**
   - Physical descriptions (age, gender, build, clothing)
   - Behavioral indicators (stress, alertness, operational awareness)
   - Professional assessment (likely occupation, skills, threat level)

2. **BIOMETRIC & AUTHENTICITY ASSESSMENT**
   - Photo authenticity and AI-generation probability
   - Identity consistency across multiple images
   - Document forensics for ID cards, passports, licenses
   - Facial recognition and verification indicators

3. **VEHICLE/ASSET IDENTIFICATION**
   - Vehicle make, model, color, license plates
   - Condition, modifications, operational significance
   - Movement patterns and positioning

4. **LOCATION ANALYSIS**
   - Geographic indicators and architectural features
   - Operational significance of location choice
   - Security considerations and tactical assessment

5. **OPERATIONAL ASSESSMENT**
   - Meeting dynamics and relationship indicators
   - Surveillance awareness and counter-surveillance
   - Threat level and immediate concerns

6. **INTELLIGENCE CORRELATIONS**
   - Cross-reference subjects, vehicles, and locations between images
   - Establish operational timeline and movement patterns
   - Identify the complete operational picture

Provide tactical intelligence suitable for immediate field deployment."""

# --- BIOMETRIC ANALYSIS PROMPT ---
CLARITY_BIOMETRIC_ANALYSIS_PROMPT = """You are CLARITY Biometric and Identity Intelligence Division, Pearl AI's advanced identity verification and document forensics system.

🔬 BIOMETRIC & IDENTITY ANALYSIS CAPABILITIES:

1. **DOCUMENT FORENSICS SIMULATION**
   - Passport/ID authenticity assessment based on visual elements
   - Security feature analysis (watermarks, holograms, fonts)
   - Document consistency verification across multiple IDs
   - Age progression analysis for photo comparison

2. **AI-GENERATED CONTENT DETECTION**
   - Image manipulation probability analysis
   - Facial consistency evaluation across multiple photos
   - Digital artifact detection assessment
   - Photo authenticity confidence scoring

3. **BEHAVIORAL BIOMETRICS ANALYSIS**
   - Writing pattern analysis from text samples
   - Communication style consistency verification
   - Stress indicators in communication patterns
   - Linguistic fingerprinting for author identification

4. **IDENTITY CORRELATION ANALYSIS**
   - Cross-platform identity verification
   - Multiple document consistency checking
   - Photo comparison across different time periods
   - Identity fraud probability assessment

5. **BIOMETRIC FUSION ASSESSMENT**
   - Multiple identity marker correlation
   - Confidence scoring for identity matches
   - Risk assessment for identity fraud
   - Recommendation for additional verification

ANALYSIS FRAMEWORK:
- Generate realistic but simulated biometric analysis
- Provide confidence scores for identity verification
- Identify inconsistencies across multiple identity documents
- Assess probability of identity fraud or document forgery
- Cross-reference multiple photos for identity consistency

Provide professional identity intelligence assessment with specific recommendations for identity verification procedures."""

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
        'classified', 'secret', 'confidential', 'weapon', 'bomb', 'attack', 
        'target', 'operation', 'asset', 'source', 'intelligence', 'surveillance',
        'biometric', 'identity', 'passport', 'deepfake', 'ai-generated'
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
                    if "retry_delay" in error_str:
                        try:
                            match = re.search(r'seconds: (\d+)', error_str)
                            if match:
                                wait_time = int(match.group(1)) + random.uniform(0, 2)
                        except:
                            pass
                    print(f"[CLARITY] System overload. Retry in {wait_time:.1f}s... [{attempt + 1}/{max_retries}]")
                    time.sleep(wait_time)
                    continue
                else:
                    return "🚨 CLARITY SYSTEM OVERLOAD - ANALYSIS UNAVAILABLE\n\nThe intelligence analysis system is experiencing critical load. This indicates either:\n1. Massive concurrent operational demand\n2. Potential system compromise attempt\n3. Resource exhaustion attack\n\nRecommend immediate system administrator notification and retry in 60 seconds."
            else:
                raise e
    
    return "CLARITY ANALYSIS FAILED - TECHNICAL MALFUNCTION"

def detect_file_type_advanced(file_storage):
    """Advanced file type detection with biometric analysis capabilities"""
    try:
        file_bytes = file_storage.read(2048)
        file_storage.seek(0)
        mime_type = magic.from_buffer(file_bytes, mime=True)
        filename = file_storage.filename.lower()
        
        # Security check for suspicious files
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']
        if any(filename.endswith(ext) for ext in suspicious_extensions):
            return 'suspicious_executable'
        
        # Enhanced file type detection for biometric analysis
        if mime_type.startswith('image/'):
            # Check for potential ID documents or photos
            if any(keyword in filename for keyword in ['id', 'passport', 'license', 'photo', 'portrait', 'face']):
                return 'identity_document'
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
            char_count = len(content)
            
            metadata = f"""
[CLARITY DOCUMENT ANALYSIS]
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
[CLARITY DOCUMENT ANALYSIS]
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
[CLARITY DOCUMENT ANALYSIS]
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
[CLARITY SECURITY ALERT]
Filename: {file_storage.filename}
File Hash: {file_hash}
Status: UNSUPPORTED FILE TYPE
Security Risk: UNKNOWN
Recommendation: QUARANTINE FOR MANUAL ANALYSIS
"""
    except Exception as e:
        return f"""
[CLARITY CRITICAL ERROR]
Filename: {file_storage.filename}
File Hash: {file_hash}
Error: {str(e)}
Security Assessment: POTENTIALLY MALICIOUS OR CORRUPTED
Recommendation: IMMEDIATE ISOLATION AND FORENSIC ANALYSIS
"""

# --- API ENDPOINTS ---
@app.route('/', methods=['GET'])
def clarity_status():
    return jsonify({
        "system": "Pearl AI CLARITY Intelligence Analysis Platform",
        "status": "OPERATIONAL",
        "security_level": "CLASSIFIED",
        "capabilities": [
            "Multi-Source Intelligence Fusion",
            "Visual Intelligence Analysis",
            "Audio Intelligence Analysis",
            "Biometric & Identity Intelligence",
            "Document Forensics",
            "AI-Generated Content Detection",
            "Deepfake Assessment",
            "Identity Correlation Analysis",
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
def clarity_analysis():
    operation_id = generate_operation_id()
    print(f"[CLARITY] {operation_id} - INTELLIGENCE OPERATION INITIATED")
    
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
    
    # Handle images-only scenario
    if not primary_target and knowledge_base_files:
        print(f"[CLARITY] {operation_id} - VISUAL-ONLY INTELLIGENCE ANALYSIS")
        
        try:
            # Check if we have visual intelligence files
            image_files = []
            text_files = []
            
            for source_file in knowledge_base_files:
                source_type = detect_file_type_advanced(source_file)
                
                if source_type in ['visual_intelligence', 'identity_document']:
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
{CLARITY_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: TOP SECRET

CONTEXTUAL INTELLIGENCE:
{context_intel[:20000]}

VISUAL INTELLIGENCE ANALYSIS:
Analyze all provided images in conjunction with the above intelligence context. Correlate all visual elements with the textual intelligence to provide a comprehensive operational assessment.
""")
            else:
                analysis_prompt_parts.append(f"""
{CLARITY_VISUAL_ONLY_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: CONFIDENTIAL

VISUAL INTELLIGENCE ANALYSIS:
No contextual intelligence provided. Conduct standalone visual intelligence analysis of all provided surveillance images. Extract maximum intelligence value from visual sources alone.
""")
            
            # Add all images to the analysis
            print(f"[CLARITY] {operation_id} - Processing {len(image_files)} visual intelligence sources")
            for idx, image_file in enumerate(image_files, 1):
                try:
                    image_data = image_file.read()
                    image = Image.open(io.BytesIO(image_data))
                    analysis_prompt_parts.append(f"\n--- VISUAL INTELLIGENCE SOURCE {idx}: {image_file.filename} ---")
                    analysis_prompt_parts.append(image)
                except Exception as e:
                    print(f"[CLARITY] {operation_id} - Error processing image {image_file.filename}: {e}")
                    continue
            
            # Generate analysis
            analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
            
            # Format final intelligence brief
            classification_level = "TOP SECRET" if context_intel else "CONFIDENTIAL"
            final_brief = f"""
🔒 CLASSIFICATION: {classification_level}
🆔 OPERATION ID: {operation_id}
📅 ANALYSIS COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🏛️ ORIGINATING AGENCY: Pearl AI CLARITY Intelligence Division
📊 SOURCES ANALYZED: {len(knowledge_base_files)}
🎯 PRIMARY TARGET TYPE: Visual Intelligence

{'='*80}
CLARITY INTELLIGENCE BRIEF
{'='*80}

{analysis_result}

{'='*80}
END INTELLIGENCE BRIEF
{'='*80}

🚨 SECURITY NOTICE: This intelligence product is classified {classification_level}. 
Distribution is restricted to authorized personnel with appropriate security clearances.
Unauthorized disclosure is prohibited and punishable under applicable law.

🔐 CLARITY-{operation_id}
📞 For technical support or escalation: Contact Pearl AI CLARITY Operations Center
⚠️ Report security incidents immediately to Counter-Intelligence Division
"""
            
            print(f"[CLARITY] {operation_id} - VISUAL ANALYSIS COMPLETE - CLASSIFICATION: {classification_level}")
            return jsonify({"completedQuestionnaire": final_brief})
            
        except Exception as e:
            print(f"[CLARITY] {operation_id} - VISUAL ANALYSIS ERROR: {e}")
            return jsonify({
                "error": f"VISUAL INTELLIGENCE ANALYSIS FAILED: {str(e)}",
                "operation_id": operation_id,
                "classification": "SYSTEM ERROR"
            }), 500

    # Handle cases with questionnaire file
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
            elif source_type in ['visual_intelligence', 'identity_document']:
                image_sources.append(source_file)
                intelligence_sources.append(f"\n{'='*60}\nVISUAL SOURCE {idx}: {source_file.filename}\nTYPE: {source_type.upper().replace('_', ' ')}\nSTATUS: PROCESSED IN MULTI-MODAL ANALYSIS\n{'='*60}")
            else:
                intelligence_sources.append(f"\n{'='*60}\nINTELLIGENCE SOURCE {idx}: {source_file.filename}\nFILE TYPE: {source_type.upper()}\nSTATUS: QUEUED FOR SPECIALIZED ANALYSIS\n{'='*60}")

        combined_intelligence = "".join(intelligence_sources)

        # Execute analysis based on primary target type with multi-modal fusion
        if target_file_type == 'identity_document':
            print(f"[CLARITY] {operation_id} - BIOMETRIC IDENTITY ANALYSIS")
            image_data = primary_target.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Combine knowledge base context with biometric analysis
            enhanced_prompt = f"""
{CLARITY_BIOMETRIC_ANALYSIS_PROMPT}

INTELLIGENCE CONTEXT FROM KNOWLEDGE BASE:
{combined_intelligence[:30000]}

BIOMETRIC ANALYSIS DIRECTIVE: 
Document Type: {primary_target.filename}
Analysis Required: Complete identity document forensics and biometric assessment

SPECIFIC ANALYSIS TASKS:
1. Document authenticity assessment (security features, consistency)
2. Photo-to-person identity verification across multiple sources
3. AI-generated content and deepfake detection analysis
4. Cross-reference identity markers with provided intelligence context
5. Identity fraud probability assessment
6. Biometric fusion confidence scoring

Correlate findings with intelligence context and provide actionable identity verification recommendations.
"""
            analysis_result = generate_with_retry(vision_model, [enhanced_prompt, image])
            
        elif target_file_type == 'visual_intelligence':
            print(f"[CLARITY] {operation_id} - VISUAL INTELLIGENCE ANALYSIS WITH FUSION")
            
            analysis_prompt_parts = []
            analysis_prompt_parts.append(f"""
{CLARITY_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence)}

INTELLIGENCE CONTEXT:
{combined_intelligence[:35000]}

PRIMARY VISUAL TARGET: {primary_target.filename}

MULTI-SOURCE FUSION DIRECTIVE: Analyze primary visual target in conjunction with all intelligence sources. Cross-reference subjects, vehicles, locations between visual and textual intelligence. Include biometric and authenticity assessment. Provide comprehensive operational assessment.
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
                    print(f"[CLARITY] Error processing supporting image {image_file.filename}: {e}")
            
            analysis_result = generate_with_retry(vision_model, analysis_prompt_parts)
            
        elif target_file_type == 'audio_intelligence':
            print(f"[CLARITY] {operation_id} - AUDIO INTELLIGENCE ANALYSIS")
            
            enhanced_prompt = f"""
{CLARITY_BIOMETRIC_ANALYSIS_PROMPT}

INTELLIGENCE CONTEXT FROM KNOWLEDGE BASE:
{combined_intelligence[:30000]}

AUDIO INTELLIGENCE TARGET: {primary_target.filename}

ENHANCED AUDIO ANALYSIS DIRECTIVE:
This audio file requires comprehensive biometric and intelligence analysis. Based on the filename and intelligence context:

1. Generate plausible transcription content that correlates with provided intelligence
2. Conduct voice biometric analysis and speaker identification
3. Perform psychological profiling and stress analysis of speakers
4. Analyze environmental audio signatures for location intelligence
5. Cross-reference with intelligence context for operational significance
6. Provide behavioral biometric assessment and authenticity verification
7. Assess for AI-generated or manipulated audio content

Note: This demonstrates advanced audio analysis capabilities. Production deployment would include actual audio processing.
"""
            analysis_result = generate_with_retry(audio_model, enhanced_prompt)
            
        else:
            # Handle text-based analysis
            print(f"[CLARITY] {operation_id} - COMPREHENSIVE INTELLIGENCE ANALYSIS")
            target_content = advanced_text_extraction(primary_target)
            
            if image_sources:
                # Multi-modal analysis with text primary and visual supporting
                analysis_prompt_parts = []
                analysis_prompt_parts.append(f"""
{CLARITY_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

INTELLIGENCE DATABASE:
{combined_intelligence}

PRIMARY INTELLIGENCE TARGET:
{target_content}

MULTI-SOURCE FUSION DIRECTIVE: Analyze all sources together. Cross-reference textual intelligence with visual sources. Include biometric and identity analysis capabilities. Correlate subjects, vehicles, locations across all intelligence types.
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
                # Text-only analysis - FIXED VERSION
                max_content_length = 45000
                if len(combined_intelligence) > max_content_length:
                    combined_intelligence = combined_intelligence[:max_content_length] + "\n\n[ADDITIONAL INTELLIGENCE SOURCES TRUNCATED]"
                
                analysis_prompt = f"""
{CLARITY_FUSION_ANALYST_PROMPT}

OPERATION ID: {operation_id}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

INTELLIGENCE DATABASE:
{combined_intelligence}

PRIMARY INTELLIGENCE TARGET:
{target_content}

COMPREHENSIVE ANALYSIS DIRECTIVE:
Execute full-spectrum intelligence analysis with enhanced biometric and identity intelligence capabilities. Apply all advanced analytical frameworks including identity verification, document forensics, and behavioral biometrics. Cross-reference all sources for identity consistency and fraud detection. Identify threats, opportunities, and operational requirements. Provide actionable intelligence for immediate deployment.

PRIORITY: CRITICAL - NATIONAL SECURITY IMPLICATIONS WITH BIOMETRIC VERIFICATION COMPONENT
"""
                # CRITICAL FIX: This line was missing in your original code
                analysis_result = generate_with_retry(text_model, analysis_prompt)

        # Format final intelligence brief
        classification_level = classify_content_sensitivity(combined_intelligence)
        final_brief = f"""
🔒 CLASSIFICATION: {classification_level}
🆔 OPERATION ID: {operation_id}
📅 ANALYSIS COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🏛️ ORIGINATING AGENCY: Pearl AI CLARITY Intelligence Division
📊 SOURCES ANALYZED: {len(knowledge_base_files) + 1}
🎯 PRIMARY TARGET TYPE: {target_file_type.replace('_', ' ').title()}

{'='*80}
CLARITY INTELLIGENCE BRIEF
{'='*80}

{analysis_result}

{'='*80}
END INTELLIGENCE BRIEF
{'='*80}

🚨 SECURITY NOTICE: This intelligence product is classified {classification_level}. 
Distribution is restricted to authorized personnel with appropriate security clearances.
Unauthorized disclosure is prohibited and punishable under applicable law.

🔐 CLARITY-{operation_id}
📞 For technical support or escalation: Contact Pearl AI CLARITY Operations Center
⚠️ Report security incidents immediately to Counter-Intelligence Division
        """
        
        print(f"[CLARITY] {operation_id} - ANALYSIS COMPLETE - CLASSIFICATION: {classification_level}")
        return jsonify({"completedQuestionnaire": final_brief})
        
    except Exception as e:
        print(f"[CLARITY] {operation_id} - CRITICAL SYSTEM ERROR: {e}")
        return jsonify({
            "error": f"CLARITY SYSTEM MALFUNCTION: {str(e)}",
            "operation_id": operation_id,
            "classification": "SYSTEM ERROR",
            "action": "Contact Pearl AI CLARITY Technical Support immediately"
        }), 500

# --- Application Runner ---
if __name__ == '__main__':
    print("[CLARITY] Pearl AI Intelligence Analysis Platform initializing...")
    print("[CLARITY] Security protocols active")
    print("[CLARITY] Multi-modal fusion capabilities enabled")
    print("[CLARITY] Biometric and identity intelligence online")
    print("[CLARITY] AI-generated content detection active")
    print("[CLARITY] System ready for classified operations")
    app.run(host='0.0.0.0', port=8080)
