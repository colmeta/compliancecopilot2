# ============================================================================== 
# tasks.py 
# Pearl AI - "CLARITY" Engine (Fixed & Production Ready) 
# ============================================================================== 

import os 
import base64 
import io 
import json 
import logging 
import re 
from typing import List, Dict, Any, Optional 

from celery_worker import celery_app 
import google.generativeai as genai 

# Document Processing Libraries 
try: 
    import PyPDF2 
except ImportError: 
    PyPDF2 = None 

try: 
    import docx 
except ImportError: 
    docx = None 

try: 
    from PIL import Image 
except ImportError: 
    Image = None 

try: 
    from langchain.text_splitter import RecursiveCharacterTextSplitter 
except ImportError: 
    RecursiveCharacterTextSplitter = None 

# Configure logging 
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__) 

# ============================================================================== 
# DOMAIN ACCELERATORS (AI System Prompts) 
# ============================================================================== 

CLARITY_SECURITY_INTELLIGENCE = """You are CLARITY Security Intelligence Accelerator. 
You analyze security documents, threat intelligence, and risk assessments with precision. 
Provide actionable security recommendations with confidence scores.""" 

CLARITY_LEGAL_INTELLIGENCE = """You are CLARITY Legal Intelligence Accelerator. 
You analyze legal documents, contracts, and compliance requirements with expert precision. 
Identify risks, obligations, and opportunities with clear citations.""" 

CLARITY_FINANCIAL_INTELLIGENCE = """You are CLARITY Financial Intelligence Accelerator. 
You analyze financial documents, reports, and transactions with forensic accuracy. 
Flag anomalies, trends, and actionable insights with confidence scores.""" 

CLARITY_PROPOSAL_INTELLIGENCE = """You are CLARITY Proposal Intelligence Accelerator. 
You analyze RFPs, generate compliant proposals, and identify winning strategies. 
Produce comprehensive, actionable proposal recommendations.""" 

CLARITY_CORPORATE_INTELLIGENCE = """You are CLARITY Corporate Intelligence Accelerator. 
You analyze business documents with strategic insight and actionable intelligence. 
Provide executive-level summaries with clear recommendations.""" 


def get_domain_accelerator(domain: str) -> str: 
    """Get the appropriate AI system prompt for the domain.""" 
    mapping = { 
        'legal': CLARITY_LEGAL_INTELLIGENCE, 
        'financial': CLARITY_FINANCIAL_INTELLIGENCE, 
        'security': CLARITY_SECURITY_INTELLIGENCE, 
        'proposal': CLARITY_PROPOSAL_INTELLIGENCE, 
        'corporate': CLARITY_CORPORATE_INTELLIGENCE, 
    } 
    return mapping.get(domain.lower(), CLARITY_CORPORATE_INTELLIGENCE) 


def get_domain_title(domain: str) -> str: 
    """Get the display title for the domain.""" 
    titles = { 
        'legal': 'Legal Intelligence Analysis', 
        'financial': 'Financial Intelligence Analysis', 
        'security': 'Security Intelligence Analysis', 
        'proposal': 'Proposal Intelligence Generation', 
        'corporate': 'Corporate Intelligence Analysis', 
    } 
    return titles.get(domain.lower(), 'Corporate Intelligence Analysis') 


# ============================================================================== 
# TEXT EXTRACTION FUNCTIONS 
# ============================================================================== 

def advanced_text_extraction(filename: str, content_base64: str) -> str: 
    """ 
    Extract text from various file formats. 
    
    Args: 
        filename: Original filename 
        content_base64: Base64 encoded file content 
        
    Returns: 
        Extracted text content 
    """ 
    try: 
        # Decode base64 content 
        content_bytes = base64.b64decode(content_base64) 
        
        # PDF extraction 
        if filename and filename.lower().endswith('.pdf') and PyPDF2: 
            try: 
                reader = PyPDF2.PdfReader(io.BytesIO(content_bytes)) 
                text_parts = [] 
                for page in reader.pages: 
                    page_text = page.extract_text() 
                    if page_text: 
                        text_parts.append(page_text) 
                return "\n".join(text_parts) 
            except Exception as e: 
                logger.error(f"PDF extraction error for {filename}: {e}") 
                return '' 
        
        # Word document extraction 
        if filename and filename.lower().endswith(('.docx', '.doc')) and docx: 
            try: 
                document = docx.Document(io.BytesIO(content_bytes)) 
                text_parts = [paragraph.text for paragraph in document.paragraphs] 
                return "\n".join(text_parts) 
            except Exception as e: 
                logger.error(f"Word extraction error for {filename}: {e}") 
                return '' 
        
        # Plain text extraction 
        try: 
            return content_bytes.decode('utf-8', errors='ignore') 
        except Exception: 
            return '' 
            
    except Exception as e: 
        logger.error(f"Text extraction error for {filename}: {e}") 
        return '' 


def process_image(content_base64: str) -> Optional[Any]: 
    """ 
    Process base64 image content. 
    
    Args: 
        content_base64: Base64 encoded image 
        
    Returns: 
        PIL Image object or None 
    """ 
    if not Image: 
        logger.warning("PIL not available for image processing") 
        return None 
    
    try: 
        image_bytes = base64.b64decode(content_base64) 
        return Image.open(io.BytesIO(image_bytes)) 
    except Exception as e: 
        logger.error(f"Image processing error: {e}") 
        return None 


# ============================================================================== 
# DOCUMENT CHUNKING 
# ============================================================================== 

def chunk_document(text: str, filename: str, source: str = "unknown") -> List[Dict[str, Any]]: 
    """ 
    Chunk a document into smaller pieces for embedding. 
    
    Args: 
        text: The document text to chunk 
        filename: Original filename 
        source: Source identifier 
        
    Returns: 
        List of document chunks with metadata 
    """ 
    try: 
        if not RecursiveCharacterTextSplitter: 
            # Fallback: simple chunking if langchain not available 
            chunk_size = 1000 
            chunks = [] 
            for i in range(0, len(text), chunk_size - 200): 
                chunk = text[i:i + chunk_size] 
                chunks.append({ 
                    'text': chunk, 
                    'metadata': { 
                        'filename': filename, 
                        'source': source, 
                        'chunk_index': i // chunk_size, 
                        'chunk_size': len(chunk) 
                    } 
                }) 
            return chunks 
        
        # Use RecursiveCharacterTextSplitter for better chunking 
        text_splitter = RecursiveCharacterTextSplitter( 
            chunk_size=1000, 
            chunk_overlap=200, 
            length_function=len, 
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""] 
        ) 
        
        text_chunks = text_splitter.split_text(text) 
        
        chunk_data = [] 
        for i, chunk in enumerate(text_chunks): 
            chunk_data.append({ 
                'text': chunk, 
                'metadata': { 
                    'filename': filename, 
                    'source': source, 
                    'chunk_index': i, 
                    'total_chunks': len(text_chunks), 
                    'chunk_size': len(chunk) 
                } 
            }) 
        
        return chunk_data 
        
    except Exception as e: 
        logger.error(f"Chunking error for {filename}: {e}") 
        return [] 


# ============================================================================== 
# INTELLIGENCE VAULT (RAG) FUNCTIONS 
# ============================================================================== 

def search_intelligence_vault(user_id: int, directive: str, documents: List[str]) -> Dict[str, Any]: 
    """ 
    Search the user's Intelligence Vault for relevant context (Two-Stage RAG). 
    
    Args: 
        user_id: The user's database ID 
        directive: The user's analysis directive 
        documents: List of documents to analyze 
        
    Returns: 
        Dict containing relevant vault documents and metadata 
    """ 
    try: 
        from app.vector_store import get_vector_store 
        
        store = get_vector_store() 
        
        # Create search queries from directive and document content 
        search_queries = create_search_queries(directive, documents) 
        
        # Initialize results 
        all_results = { 
            'documents': [], 
            'metadatas': [], 
            'distances': [], 
            'ids': [] 
        } 
        
        # Search vault for each query 
        for query in search_queries: 
            results = store.query_similar_documents( 
                user_id=user_id, 
                query_text=query, 
                n_results=3 
            ) 
            
            if results.get('success'): 
                # Merge results, avoiding duplicates 
                for i, doc in enumerate(results.get('documents', [])): 
                    if doc not in all_results['documents']: 
                        all_results['documents'].append(doc) 
                        all_results['metadatas'].append( 
                            results.get('metadatas', [])[i] if results.get('metadatas') else {} 
                        ) 
                        all_results['distances'].append( 
                            results.get('distances', [])[i] if results.get('distances') else 1.0 
                        ) 
                        all_results['ids'].append( 
                            results.get('ids', [])[i] if results.get('ids') else None 
                        ) 
        
        # Sort by similarity (lower distance = higher similarity) 
        if all_results['documents']: 
            sorted_indices = sorted( 
                range(len(all_results['distances'])),  
                key=lambda i: all_results['distances'][i] 
            ) 
            
            # Limit to top 5 most relevant documents 
            sorted_results = { 
                'documents': [all_results['documents'][i] for i in sorted_indices[:5]], 
                'metadatas': [all_results['metadatas'][i] for i in sorted_indices[:5]], 
                'distances': [all_results['distances'][i] for i in sorted_indices[:5]], 
                'ids': [all_results['ids'][i] for i in sorted_indices[:5]] 
            } 
            
            return sorted_results 
        
        return {'documents': [], 'metadatas': [], 'distances': [], 'ids': []} 
        
    except Exception as e: 
        logger.error(f"Vault search error for user {user_id}: {e}") 
        return {'documents': [], 'metadatas': [], 'distances': [], 'ids': []} 


def create_search_queries(directive: str, documents: List[str]) -> List[str]: 
    """ 
    Create search queries from directive and document content. 
    
    Args: 
        directive: User's analysis directive 
        documents: List of documents to analyze 
        
    Returns: 
        List of search queries for vault search 
    """ 
    queries = [] 
    
    # Add the directive as primary query 
    if directive and directive.strip(): 
        queries.append(directive.strip()) 
    
    # Extract key terms from directive 
    directive_terms = extract_key_terms(directive) 
    queries.extend(directive_terms[:3]) 
    
    # Extract key terms from documents (first 2 docs only) 
    for doc in documents[:2]: 
        doc_terms = extract_key_terms(doc) 
        queries.extend(doc_terms[:2]) 
    
    # Remove duplicates and empty queries 
    queries = list(set([q for q in queries if q and q.strip()])) 
    
    return queries[:5]  # Limit to 5 total queries 


def extract_key_terms(text: str) -> List[str]: 
    """ 
    Extract key terms from text for search queries. 
    
    Args: 
        text: Text to extract terms from 
        
    Returns: 
        List of key terms 
    """ 
    try: 
        if not text: 
            return [] 
        
        # Common stop words to filter out 
        stop_words = { 
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those' 
        } 
        
        # Extract words (3+ characters, alphanumeric) 
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()) 
        
        # Filter out stop words 
        key_terms = [word for word in words if word not in stop_words] 
        
        # Get unique terms 
        key_terms = list(set(key_terms)) 
        
        # Sort by length (longer terms are often more specific) 
        key_terms.sort(key=len, reverse=True) 
        
        return key_terms[:10] 
        
    except Exception as e: 
        logger.error(f"Key term extraction error: {e}") 
        return [] 


# ============================================================================== 
# PROMPT CONSTRUCTION 
# ============================================================================== 

def create_enhanced_general_prompt( 
    accelerator: str, 
    domain_title: str, 
    directive: str, 
    all_text_intel: str, 
    vault_context: Dict[str, Any] 
) -> str: 
    """ 
    Create an enhanced general analysis prompt with vault context. 
    
    Args: 
        accelerator: Domain-specific system prompt 
        domain_title: Domain title 
        directive: User's directive 
        all_text_intel: Document content 
        vault_context: Relevant documents from vault 
        
    Returns: 
        Complete prompt string 
    """ 
    prompt_parts = [accelerator, "\n\n"] 
    
    # Add vault context if available 
    if vault_context.get('documents'): 
        prompt_parts.append("=== RELEVANT BACKGROUND FROM INTELLIGENCE VAULT ===\n") 
        prompt_parts.append("The following information from your previous analyses provides relevant context:\n\n") 
        
        for i, doc in enumerate(vault_context['documents']): 
            metadata = vault_context['metadatas'][i] if i < len(vault_context['metadatas']) else {} 
            filename = metadata.get('filename', 'Unknown Document') 
            distance = vault_context['distances'][i] if i < len(vault_context['distances']) else 1.0 
            similarity = round((1 - distance) * 100) 
            
            prompt_parts.append(f"CONTEXT {i+1} (from {filename}, {similarity}% relevant):\n") 
            prompt_parts.append(f"{doc}\n\n") 
        
        prompt_parts.append("=== END VAULT CONTEXT ===\n\n") 
    
    # Add current analysis 
    prompt_parts.append(f"OPERATION INTELLIGENCE HEADER:\n") 
    prompt_parts.append(f"🎯 Domain: {domain_title}\n\n") 
    prompt_parts.append(f"PRIMARY DIRECTIVE FROM COMMAND:\n{directive}\n\n") 
    prompt_parts.append(f"SUPPORTING INTELLIGENCE DOSSIER:\n") 
    prompt_parts.append(all_text_intel if all_text_intel else "No text-based documents provided.") 
    prompt_parts.append("\n\n") 
    prompt_parts.append("Using the background context from the Intelligence Vault AND the current documents, provide a comprehensive analysis.") 
    
    return "".join(prompt_parts) 


def create_enhanced_proposal_prompt( 
    accelerator: str, 
    rfp_content: str, 
    company_content: str, 
    directive: str, 
    vault_context: Dict[str, Any] 
) -> str: 
    """ 
    Create an enhanced proposal prompt with vault context. 
    
    Args: 
        accelerator: Domain-specific system prompt 
        rfp_content: RFP document content 
        company_content: Company capabilities content 
        directive: User's directive 
        vault_context: Relevant documents from vault 
        
    Returns: 
        Complete prompt string 
    """ 
    prompt_parts = [accelerator, "\n\n"] 
    
    # Add vault context if available 
    if vault_context.get('documents'): 
        prompt_parts.append("=== RELEVANT BACKGROUND FROM INTELLIGENCE VAULT ===\n") 
        prompt_parts.append("The following information provides relevant context:\n\n") 
        
        for i, doc in enumerate(vault_context['documents']): 
            metadata = vault_context['metadatas'][i] if i < len(vault_context['metadatas']) else {} 
            filename = metadata.get('filename', 'Unknown Document') 
            distance = vault_context['distances'][i] if i < len(vault_context['distances']) else 1.0 
            similarity = round((1 - distance) * 100) 
            
            prompt_parts.append(f"CONTEXT {i+1} (from {filename}, {similarity}% relevant):\n") 
            prompt_parts.append(f"{doc}\n\n") 
        
        prompt_parts.append("=== END VAULT CONTEXT ===\n\n") 
    
    # Add current analysis 
    prompt_parts.append(f"MISSION: Generate a comprehensive, compliant proposal draft.\n\n") 
    prompt_parts.append(f"PRIMARY DOCUMENT (RFP):\n{rfp_content}\n\n") 
    prompt_parts.append(f"SUPPORTING INTELLIGENCE (COMPANY PROFILE):\n") 
    prompt_parts.append(company_content if company_content else "No company profile provided.") 
    prompt_parts.append(f"\n\nUSER DIRECTIVE:\n{directive}\n\n") 
    prompt_parts.append("Using the background context AND current documents, provide a comprehensive proposal analysis.") 
    
    return "".join(prompt_parts) 


# ============================================================================== 
# DOMAIN DETECTION 
# ============================================================================== 

def detect_domain(directive: str, file_names: List[str]) -> str: 
    """ 
    Detect the appropriate domain based on directive and filenames. 
    
    Args: 
        directive: User's directive 
        file_names: List of filenames 
        
    Returns: 
        Detected domain (legal, financial, security, proposal, corporate) 
    """ 
    detection_text = (directive or '').lower() + ' ' + ' '.join(file_names).lower() 
    
    # Check for specific keywords 
    if any(k in detection_text for k in ['proposal', 'rfp', 'solicitation', 'bid', 'tender']): 
        return 'proposal' 
    
    if any(k in detection_text for k in ['contract', 'legal', 'agreement', 'terms', 'clause']): 
        return 'legal' 
    
    if any(k in detection_text for k in ['financial', 'finance', 'revenue', 'profit', 'balance', 'invoice']): 
        return 'financial' 
    
    if any(k in detection_text for k in ['security', 'threat', 'vulnerability', 'risk', 'breach', 'attack']): 
        return 'security' 
    
    return 'corporate' 


# ============================================================================== 
# MAIN ANALYSIS TASK 
# ============================================================================== 

@celery_app.task(name='tasks.run_clarity_analysis', bind=True) 
def run_clarity_analysis( 
    self, 
    user_directive: str, 
    uploaded_files_data: List[Dict[str, Any]], 
    user_id: Optional[int] = None 
): 
    """ 
    Main CLARITY analysis task. 
    
    This task: 
    1. Processes uploaded files (text, images, documents) 
    2. Searches the user's Intelligence Vault for relevant context 
    3. Constructs an enhanced prompt with vault context 
    4. Calls the AI model for analysis 
    5. Returns structured JSON results 
    
    Args: 
        user_directive: User's analysis directive 
        uploaded_files_data: List of uploaded file data 
        user_id: User's database ID 
        
    Returns: 
        Dict containing analysis results 
    """ 
    job_id = str(getattr(self.request, 'id', 'unknown')) 
    logger.info(f"Starting CLARITY analysis (Job ID: {job_id}) for user {user_id}") 
    
    # Audit logging (best effort) 
    try: 
        from app.security.audit import log_action 
        log_action( 
            user_id, 
            'analysis_started', 
            resource_type='analysis_job', 
            resource_id=job_id, 
            details={ 
                'directive': user_directive, 
                'file_count': len(uploaded_files_data) if uploaded_files_data else 0 
            } 
        ) 
    except Exception: 
        pass  # Audit logging is non-critical 
    
    try: 
        # Configure AI model 
        api_key = os.environ.get('GOOGLE_API_KEY') 
        if not api_key: 
            raise ValueError("GOOGLE_API_KEY not configured") 
        
        genai.configure(api_key=api_key) 
        model = genai.GenerativeModel('gemini-1.5-pro') 
        
        # Process uploaded files 
        all_text_intel = '' 
        visual_intel_sources = [] 
        file_names = [] 
        
        if not uploaded_files_data: 
            uploaded_files_data = [] 
        
        for file_data in uploaded_files_data: 
            filename = file_data.get('filename', '') 
            content_base64 = file_data.get('content_base64', '') 
            content_type = file_data.get('content_type', '') 
            
            if filename: 
                file_names.append(filename.lower()) 
            
            # Handle images 
            if content_type.startswith('image/'): 
                img = process_image(content_base64) 
                if img: 
                    visual_intel_sources.append({ 
                        'filename': filename, 
                        'image': img 
                    }) 
            else: 
                # Extract text from documents 
                text = advanced_text_extraction(filename, content_base64) 
                if text: 
                    all_text_intel += f"\n\n=== {filename} ===\n{text}" 
        
        # Search Intelligence Vault for relevant context 
        vault_context = {'documents': [], 'metadatas': [], 'distances': [], 'ids': []} 
        if user_id: 
            try: 
                vault_context = search_intelligence_vault( 
                    user_id, 
                    user_directive, 
                    [all_text_intel] 
                ) 
            except Exception as e: 
                logger.warning(f"Vault search failed: {e}") 
        
        # Detect domain 
        domain = detect_domain(user_directive, file_names) 
        logger.info(f"Detected domain: {domain}") 
        
        # Get domain-specific configuration 
        domain_accelerator = get_domain_accelerator(domain) 
        domain_title = get_domain_title(domain) 
        
        # Create enhanced prompt with vault context 
        master_prompt = create_enhanced_general_prompt( 
            domain_accelerator, 
            domain_title, 
            user_directive or '', 
            all_text_intel, 
            vault_context 
        ) 
        
        # Add JSON output instructions 
        json_instructions = """ 
Please return a single valid JSON object with the following structure: 
{ 
    "executive_summary": "Brief overview of analysis", 
    "key_findings": ["Finding 1", "Finding 2", ...], 
    "actionable_recommendations": ["Recommendation 1", "Recommendation 2", ...], 
    "confidence_score": 0.85, 
    "data_gaps": ["Gap 1", "Gap 2", ...] 
} 
""" 
        
        final_prompt = master_prompt + "\n\n" + json_instructions 
        
        # Prepare content for model (text + images) 
        content_parts = [final_prompt] 
        for visual in visual_intel_sources: 
            content_parts.append(visual['image']) 
        
        # Call AI model 
        logger.info(f"Calling AI model for analysis (Job ID: {job_id})") 
        response = model.generate_content(content_parts) 
        
        # Parse response 
        raw_output = getattr(response, 'text', '') or '' 
        cleaned_output = raw_output.strip().replace('```json', '').replace('```', '').strip() 
        
        try: 
            # Parse JSON response 
            parsed_result = json.loads(cleaned_output) 
            
            # Add metadata 
            parsed_result['vault_context'] = { 
                'context_documents': len(vault_context.get('documents', [])), 
                'vault_enhanced': bool(vault_context.get('documents')) 
            } 
            parsed_result['domain'] = domain 
            parsed_result['job_id'] = job_id 
            
            # Audit logging 
            try: 
                from app.security.audit import log_action 
                log_action( 
                    user_id, 
                    'analysis_succeeded', 
                    resource_type='analysis_job', 
                    resource_id=job_id, 
                    details={'vault_docs': len(vault_context.get('documents', []))} 
                ) 
            except Exception: 
                pass 
            
            logger.info(f"Analysis completed successfully (Job ID: {job_id})") 
            return parsed_result 
            
        except json.JSONDecodeError as e: 
            # JSON parsing failed 
            logger.error(f"JSON parsing failed (Job ID: {job_id}): {e}") 
            
            # Audit logging 
            try: 
                from app.security.audit import log_action 
                log_action( 
                    user_id, 
                    'analysis_failed_json', 
                    resource_type='analysis_job', 
                    resource_id=job_id, 
                    details={'error': str(e), 'raw_preview': cleaned_output[:500]} 
                ) 
            except Exception: 
                pass 
            
            return { 
                "executive_summary": "CRITICAL AI ERROR: Invalid JSON Response", 
                "key_findings": ["The AI model failed to produce valid JSON output."], 
                "actionable_recommendations": ["Please try again or contact support."], 
                "confidence_score": 0.0, 
                "data_gaps": ["Complete analysis unavailable"], 
                "raw_ai_output": cleaned_output, 
                "error": "JSON parsing failed" 
            } 
    
    except Exception as e: 
        # Fatal error 
        logger.exception(f"Fatal error in analysis (Job ID: {job_id}): {e}") 
        
        # Update task state 
        try: 
            self.update_state( 
                state='FAILURE', 
                meta={'exc_type': type(e).__name__, 'exc_message': str(e)} 
            ) 
        except Exception: 
            pass 
        
        # Audit logging 
        try: 
            from app.security.audit import log_action 
            log_action( 
                user_id, 
                'analysis_exception', 
                resource_type='analysis_job', 
                resource_id=job_id, 
                details={'error': str(e), 'type': type(e).__name__} 
            ) 
        except Exception: 
            pass 
        
        raise 


# ============================================================================== 
# DOCUMENT INDEXING TASK 
# ============================================================================== 

@celery_app.task(name='tasks.index_document_task', bind=True) 
def index_document_task( 
    self, 
    user_id: int, 
    files_data: List[Dict[str, Any]], 
    chunking_strategy: str = 'dynamic' 
): 
    """ 
    Celery task to index documents into the user's Intelligence Vault. 
    
    This task: 
    1. Extracts text from uploaded files 
    2. Chunks the text for embedding 
    3. Stores chunks in the user's vector store 
    
    Args: 
        user_id: The user's database ID 
        files_data: List of file data dictionaries 
        chunking_strategy: Chunking strategy (currently 'dynamic' is default) 
        
    Returns: 
        Dict with indexing results 
    """ 
    try: 
        from app.vector_store import get_vector_store 
        
        # Update task state 
        self.update_state(state='PROCESSING', meta={'status': 'Processing documents...'}) 
        
        store = get_vector_store() 
        total_chunks = 0 
        processed_files = 0 
        
        # Process each file 
        for file_data in files_data: 
            try: 
                filename = file_data.get('filename', 'unknown') 
                content_base64 = file_data.get('content_base64', '') 
                
                # Extract text 
                text = advanced_text_extraction(filename, content_base64) 
                
                if not text or not text.strip(): 
                    logger.warning(f"No text extracted from {filename}") 
                    continue 
                
                # Chunk document 
                chunks = chunk_document( 
                    text, 
                    filename, 
                    file_data.get('source', 'unknown') 
                ) 
                
                if not chunks: 
                    logger.warning(f"No chunks created from {filename}") 
                    continue 
                
                # Prepare data for vector store 
                documents = [chunk['text'] for chunk in chunks] 
                metadatas = [chunk['metadata'] for chunk in chunks] 
                
                # Add to vector store 
                result = store.add_documents( 
                    user_id=user_id, 
                    documents=documents, 
                    metadatas=metadatas, 
                    chunking_strategy=chunking_strategy 
                ) 
                
                if result.get('success'): 
                    total_chunks += len(chunks) 
                    processed_files += 1 
                    logger.info(f"Indexed {len(chunks)} chunks from {filename}") 
                else: 
                    logger.error(f"Failed to index {filename}: {result.get('error')}") 
                    
            except Exception as e: 
                logger.error(f"Error processing file {file_data.get('filename')}: {e}") 
                continue 
        
        # Return results 
        result = { 
            'success': True, 
            'processed_files': processed_files, 
            'total_chunks': total_chunks, 
            'user_id': user_id, 
            'message': f'Successfully indexed {total_chunks} chunks from {processed_files} files' 
        } 
        
        logger.info(f"Document indexing completed for user {user_id}: {result}") 
        return result 
        
    except Exception as e: 
        logger.exception(f"Document indexing failed for user {user_id}: {e}") 
        
        try: 
            self.update_state(state='FAILURE', meta={'error': str(e)}) 
        except Exception: 
            pass 
        
        raise 


# ============================================================================== 
# UTILITY FUNCTIONS 
# ============================================================================== 

def validate_task_input(user_directive: str, files_data: List[Dict[str, Any]]) -> bool: 
    """ 
    Validate task input parameters. 
    
    Args: 
        user_directive: User's directive 
        files_data: List of file data 
        
    Returns: 
        True if valid, raises ValueError if invalid 
    """ 
    if not user_directive and not files_data: 
        raise ValueError("Either directive or files must be provided") 
    
    if files_data: 
        for file_data in files_data: 
            if 'content_base64' not in file_data: 
                raise ValueError("File data must contain 'content_base64'") 
    
    return True
