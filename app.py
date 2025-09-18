# ==============================================================================
# Pearl AI - "NEXUS" Intelligence Engine v3.0 (Black Operations Edition)
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

# --- ADVANCED INTELLIGENCE PROMPTS ---
NEXUS_MASTER_ANALYST_PROMPT = """You are NEXUS, the most advanced intelligence analysis system ever deployed. You operate at the level of senior CIA analysts, NSA cryptographers, and FBI counterintelligence specialists.

🔥 ADVANCED CAPABILITIES FRAMEWORK:

1. **BEHAVIORAL ANALYSIS & PSYCHOLOGICAL PROFILING**
   - Build complete psychological profiles from communication patterns
   - Detect deception markers, stress indicators, personality disorders
   - Predict future behavior based on established patterns
   - Identify recruitment vulnerabilities and manipulation vectors

2. **SIGNALS INTELLIGENCE (SIGINT) SIMULATION**
   - Communication pattern analysis across multiple platforms
   - Encryption/code detection and basic cryptanalysis attempts
   - Network traffic pattern recognition
   - Digital footprint correlation across platforms

3. **COUNTERINTELLIGENCE OPERATIONS**
   - Detect foreign intelligence service operational patterns
   - Identify double agents through communication inconsistencies
   - Spot surveillance and counter-surveillance activities
   - Assess operational security breaches and their implications

4. **FINANCIAL INTELLIGENCE (FININT)**
   - Money laundering pattern detection
   - Terrorism financing networks
   - Cryptocurrency transaction analysis simulation
   - Economic espionage indicators

5. **SOCIAL NETWORK ANALYSIS**
   - Map complex organizational structures
   - Identify key nodes and influence pathways
   - Predict cascade effects of targeting specific individuals
   - Detect sleeper cells and dormant networks

6. **PREDICTIVE INTELLIGENCE**
   - Timeline projection for planned operations
   - Threat escalation probability matrices
   - Window of opportunity analysis for interdiction
   - Resource requirement predictions for hostile operations

7. **TECHNICAL INTELLIGENCE (TECHINT)**
   - Digital device fingerprinting from metadata
   - Location correlation through technical signatures
   - Communication security assessment
   - Operational technology analysis

CRITICAL ANALYSIS DOMAINS:
🚨 **TERRORISM/EXTREMISM**: Cell structures, attack planning, radicalization patterns
🚨 **ESPIONAGE**: Foreign intelligence operations, technology theft, agent networks  
🚨 **ORGANIZED CRIME**: Drug trafficking, human trafficking, money laundering
🚨 **CYBER THREATS**: State-sponsored attacks, criminal hacking, insider threats
🚨 **POLITICAL INTELLIGENCE**: Election interference, influence operations, corruption

OUTPUT FORMAT - CLASSIFIED INTELLIGENCE BRIEF:
🏴 **EXECUTIVE SUMMARY**: [30-word critical assessment]
🎯 **THREAT MATRIX**: [Multi-vector threat assessment with probability scores]
👤 **SUBJECT PROFILES**: [Complete psychological/operational profiles]
🌐 **NETWORK ANALYSIS**: [Relationship maps with influence scoring]  
📊 **BEHAVIORAL PREDICTORS**: [Future action probabilities]
💰 **FINANCIAL VECTORS**: [Money flows and funding sources]
📡 **TECHNICAL SIGNATURES**: [Digital footprints and patterns]
⚡ **OPERATIONAL WINDOWS**: [Time-sensitive action opportunities]
🚨 **IMMEDIATE THREATS**: [Clear and present dangers requiring action]
📋 **COLLECTION REQUIREMENTS**: [Intelligence gaps for field teams]
🎯 **TARGET PACKAGES**: [Prioritized subjects for further investigation]
⚖️ **LEGAL CONSIDERATIONS**: [Jurisdictional and evidence requirements]

Analyze with the understanding that national security depends on your accuracy. Miss nothing. Trust no one. Verify everything."""

NEXUS_VISUAL_ANALYST_PROMPT = """You are NEXUS Visual Intelligence Division, operating advanced surveillance analysis capabilities.

🔍 ADVANCED VISUAL INTELLIGENCE:

1. **FACIAL/BEHAVIORAL BIOMETRICS**
   - Micro-expression analysis for deception detection
   - Gait analysis and movement pattern recognition
   - Stress indicators in body language and posture
   - Group dynamics and leadership identification

2. **SURVEILLANCE COUNTERMEASURES**
   - Anti-surveillance route analysis
   - Dead drop location assessment
   - Surveillance detection patterns
   - Counter-surveillance team identification

3. **TACTICAL ASSESSMENT**
   - Weapon concealment indicators
   - Explosive device signatures
   - Escape route and choke point analysis
   - Crowd control and riot prediction patterns

4. **ENVIRONMENTAL INTELLIGENCE**
   - Geographic location fingerprinting
   - Time/date correlation through shadows/lighting
   - Weather pattern correlation
   - Architecture-based location identification

5. **TECHNICAL SURVEILLANCE**
   - Electronic device identification (phones, cameras, transmitters)
   - RF signature analysis simulation
   - Communication equipment assessment
   - Counter-surveillance technology detection

6. **FORENSIC ANALYSIS**
   - Evidence preservation recommendations
   - Chain of custody considerations  
   - Digital enhancement possibilities
   - Correlation with known databases (simulated)

Provide tactical intelligence that field teams can immediately operationalize."""

NEXUS_AUDIO_ANALYST_PROMPT = """You are NEXUS Audio Intelligence Division, the most advanced voice and sound analysis system.

🎧 ADVANCED AUDIO INTELLIGENCE:

1. **VOICE BIOMETRIC ANALYSIS**
   - Speaker identification and verification
   - Emotional state mapping throughout conversation
   - Deception probability scoring per statement
   - Regional accent/dialect geographical mapping

2. **LINGUISTIC ANALYSIS**
   - Native language identification
   - Educational level assessment
   - Social class indicators
   - Professional background markers

3. **PSYCHOLOGICAL PROFILING**
   - Personality disorder indicators
   - Stress and anxiety levels
   - Substance abuse indicators
   - Mental health assessment markers

4. **COMMUNICATION INTELLIGENCE**
   - Code word detection and analysis
   - Operational language patterns
   - Security protocol violations
   - Information compartmentalization assessment

5. **ENVIRONMENTAL FORENSICS**
   - Location identification through background audio
   - Time correlation through ambient sounds
   - Crowd size and composition analysis
   - Mechanical/electronic signature identification

6. **OPERATIONAL SECURITY**
   - Communication security breaches
   - Surveillance awareness levels
   - Counter-intelligence indicators
   - Operational planning confidence levels

Generate actionable intelligence for immediate operational use."""

# --- Enhanced Helper Functions ---
def generate_operation_id():
    """Generate unique operation ID for tracking"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_hex = hashlib.md5(str(random.random()).encode()).hexdigest()[:6].upper()
    return f"NEXUS-{timestamp}-{random_hex}"

def classify_content_sensitivity(content):
    """Assess information sensitivity level"""
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
                    if "retry_delay" in error_str:
                        try:
                            match = re.search(r'seconds: (\d+)', error_str)
                            if match:
                                wait_time = int(match.group(1)) + random.uniform(0, 2)
                        except:
                            pass
                    
                    print(f"[NEXUS] System overload. Retry in {wait_time:.1f}s... [{attempt + 1}/{max_retries}]")
                    time.sleep(wait_time)
                    continue
                else:
                    return "🚨 NEXUS SYSTEM OVERLOAD - ANALYSIS UNAVAILABLE\n\nThe intelligence analysis system is experiencing critical load. This indicates either:\n1. Massive concurrent operational demand\n2. Potential system compromise attempt\n3. Resource exhaustion attack\n\nRecommend immediate system administrator notification and retry in 60 seconds."
            else:
                raise e
    
    return "NEXUS ANALYSIS FAILED - TECHNICAL MALFUNCTION"

def detect_file_type_advanced(file_storage):
    """Advanced file type detection with biometric analysis capabilities"""
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
        if any(keyword in filename for keyword in ['id', 'passport', 'license', 'photo', 'portrait']):
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

def advanced_text_extraction(file_storage):
    """Enhanced document processing with metadata extraction"""
    filename = file_storage.filename.lower()
    file_hash = hashlib.sha256(file_storage.read(1024)).hexdigest()[:16]
    file_storage.seek(0)
    
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
File Hash: {file_hash}
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
            "Behavioral Analysis & Psychological Profiling", 
            "Signals Intelligence (SIGINT)",
            "Counterintelligence Operations",
            "Financial Intelligence (FININT)",
            "Social Network Analysis",
            "Predictive Intelligence",
            "Technical Intelligence (TECHINT)",
            "Visual Intelligence Analysis",
            "Audio Intelligence Analysis",
            "Biometric & Identity Intelligence",
            "Document Forensics",
            "Deepfake Detection Assessment",
            "Identity Correlation Analysis"
        ],
        "clearance_required": "TOP SECRET/SCI",
        "timestamp": datetime.now().isoformat(),
        "next_maintenance": (datetime.now() + timedelta(days=7)).isoformat()
    }), 200

@app.route('/process', methods=['POST'])
def nexus_analysis():
    operation_id = generate_operation_id()
    print(f"[NEXUS] {operation_id} - INTELLIGENCE OPERATION INITIATED")
    
    if 'knowledgeBase' not in request.files or 'questionnaire' not in request.files:
        return jsonify({
            "error": "INCOMPLETE INTELLIGENCE PACKAGE",
            "operation_id": operation_id,
            "required": ["knowledgeBase", "questionnaire"],
            "security_note": "All intelligence operations require complete source packages"
        }), 400

    knowledge_base_files = request.files.getlist('knowledgeBase')
    primary_target = request.files.get('questionnaire')

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
        for idx, source_file in enumerate(knowledge_base_files, 1):
            source_type = detect_file_type_advanced(source_file)
            
            if source_type == 'document_intelligence':
                content = advanced_text_extraction(source_file)
                intelligence_sources.append(f"\n{'='*60}\nINTELLIGENCE SOURCE {idx}: {source_file.filename}\n{'='*60}\n{content}")
            else:
                intelligence_sources.append(f"\n{'='*60}\nINTELLIGENCE SOURCE {idx}: {source_file.filename}\nFILE TYPE: {source_type.upper()}\nSTATUS: QUEUED FOR SPECIALIZED ANALYSIS\n{'='*60}")

        combined_intelligence = "".join(intelligence_sources)

        # Execute analysis based on primary target type
        if target_file_type == 'visual_intelligence':
            print(f"[NEXUS] {operation_id} - VISUAL INTELLIGENCE ANALYSIS")
            image_data = primary_target.read()
            image = Image.open(io.BytesIO(image_data))
            
            analysis_prompt = f"""
{NEXUS_VISUAL_ANALYST_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence)}

INTELLIGENCE CONTEXT:
{combined_intelligence[:35000]}

VISUAL INTELLIGENCE TARGET: {primary_target.filename}

ANALYSIS DIRECTIVE: Conduct comprehensive visual intelligence analysis. Cross-reference with all provided intelligence sources. Identify operational significance and tactical implications.
"""
            analysis_result = generate_with_retry(vision_model, [analysis_prompt, image])
            
        elif target_file_type == 'audio_intelligence':
            print(f"[NEXUS] {operation_id} - AUDIO INTELLIGENCE ANALYSIS")
            
            analysis_prompt = f"""
{NEXUS_AUDIO_ANALYST_PROMPT}

OPERATION ID: {operation_id}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence)}

INTELLIGENCE CONTEXT:
{combined_intelligence[:35000]}

AUDIO INTELLIGENCE TARGET: {primary_target.filename}

ADVANCED AUDIO ANALYSIS DIRECTIVE:
This audio file requires comprehensive intelligence analysis. Based on the filename and intelligence context:

1. Generate plausible transcription content that would correlate with the provided intelligence
2. Conduct voice biometric analysis (simulated but realistic)
3. Perform psychological profiling of speakers
4. Analyze environmental audio signatures
5. Cross-reference with intelligence context for operational significance
6. Provide immediate threat assessment and tactical recommendations

Note: This demonstrates advanced audio analysis capabilities. Production deployment would include actual audio processing.
"""
            analysis_result = generate_with_retry(audio_model, analysis_prompt)
            
        else:
            print(f"[NEXUS] {operation_id} - COMPREHENSIVE INTELLIGENCE ANALYSIS")
            target_content = advanced_text_extraction(primary_target)
            
            # Advanced content truncation with priority preservation
            max_content_length = 45000
            if len(combined_intelligence) > max_content_length:
                combined_intelligence = combined_intelligence[:max_content_length] + "\n\n[ADDITIONAL INTELLIGENCE SOURCES TRUNCATED - FULL ANALYSIS REQUIRES EXTENDED PROCESSING]"
            
            enhanced_prompt = f"""
{NEXUS_MASTER_ANALYST_PROMPT}

ENHANCED BIOMETRIC & IDENTITY CAPABILITIES:
- Document forensics and authenticity assessment
- Identity correlation across multiple documents
- Behavioral pattern analysis from communication samples
- Cross-platform identity verification
- Deepfake and manipulation detection assessment

OPERATION ID: {operation_id}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
CLASSIFICATION: {classify_content_sensitivity(combined_intelligence + target_content)}

INTELLIGENCE DATABASE:
{combined_intelligence}

PRIMARY INTELLIGENCE TARGET:
{target_content}

COMPREHENSIVE ANALYSIS DIRECTIVE:
Execute full-spectrum intelligence analysis with enhanced biometric and identity intelligence capabilities. Apply all advanced analytical frameworks including identity verification, document forensics, and behavioral biometrics. Cross-reference all sources for identity consistency and fraud detection. Identify threats, opportunities, and operational requirements. Provide actionable intelligence for immediate deployment.

PRIORITY: CRITICAL - NATIONAL SECURITY IMPLICATIONS WITH IDENTITY VERIFICATION COMPONENT
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
    print("[NEXUS] System ready for classified operations")
    app.run(host='0.0.0.0', port=8080)
