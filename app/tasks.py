# ==============================================================================
# tasks.py
# Pearl AI - "CLARITY" Engine v7.1 (Final Engine Integration)
# + OUTSTANDING SYSTEM v2.0 - Presidential-Grade Quality for ALL Domains
# This is the "brain" of the operation. The complete AI logic lives here.
# ==============================================================================

import os
import base64
import io
import json
import re
import logging

from celery_worker import celery_app
import google.generativeai as genai

# Document Processing Libraries
import PyPDF2
import docx
from PIL import Image

# LangChain for document chunking
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.schema import Document
from typing import List, Dict, Any

# ==============================================================================
# OUTSTANDING SYSTEM - Presidential-Grade Quality for ALL Domains
# ==============================================================================

# Flag to enable Outstanding mode (5-pass writing, research, human touch)
ENABLE_OUTSTANDING_MODE = os.getenv('ENABLE_OUTSTANDING_MODE', 'true').lower() == 'true'

try:
    from app.outstanding_system import (
        get_universal_writer,
        get_domain_researcher,
        get_universal_planner
    )
    OUTSTANDING_AVAILABLE = True
    print("✅ Outstanding System loaded - Presidential-grade quality enabled for ALL domains")
except Exception as e:
    OUTSTANDING_AVAILABLE = False
    print(f"⚠️ Outstanding System not available: {e}")


# ==============================================================================
# 1. THE LOGIC DROP-IN: ALL HELPERS AND CONSTANTS ADDED HERE
# ==============================================================================

# --- All 11 Domain-Specific Intelligence Accelerators ---

CLARITY_SECURITY_INTELLIGENCE = """You are CLARITY Security Intelligence Accelerator, Pearl AI's elite multi-source intelligence analysis system for law enforcement, security agencies, and threat assessment professionals.

MISSION: Fuse multi-source intelligence to perform comprehensive threat assessments, reconstruct operational timelines, and provide actionable security intelligence.

OPERATIONAL FRAMEWORK:
1. INTELLIGENCE FUSION: Synthesize information from multiple sources (documents, reports, communications, surveillance data)
2. TIMELINE RECONSTRUCTION: Build chronological sequences of events, identifying patterns and anomalies
3. THREAT ASSESSMENT: Evaluate potential risks, vulnerabilities, and security implications
4. EVIDENCE CORRELATION: Cross-reference findings to establish credibility and identify contradictions
5. ACTIONABLE INTELLIGENCE: Provide specific, implementable recommendations for security operations

ANALYSIS STANDARDS:
- Maintain strict objectivity and evidence-based reasoning
- Identify information gaps and recommend additional intelligence gathering
- Assess source credibility and information reliability
- Flag potential security vulnerabilities or operational risks
- Provide clear threat levels and priority rankings

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_LEGAL_INTELLIGENCE = """You are CLARITY Legal Intelligence Accelerator, Pearl AI's sophisticated legal document analysis system for attorneys, law firms, and legal professionals.

MISSION: Analyze contracts, depositions, discovery documents, and legal materials to identify risks, precedents, key evidence, and strategic opportunities.

OPERATIONAL FRAMEWORK:
1. CONTRACT ANALYSIS: Review agreements for unfavorable terms, hidden clauses, and compliance issues
2. EVIDENCE IDENTIFICATION: Extract key facts, witness statements, and supporting documentation
3. PRECEDENT RESEARCH: Identify relevant case law, statutes, and regulatory requirements
4. RISK ASSESSMENT: Evaluate potential legal exposure, liability, and mitigation strategies
5. STRATEGIC PLANNING: Recommend legal strategies, negotiation tactics, and case positioning

ANALYSIS STANDARDS:
- Maintain strict legal accuracy and professional standards
- Identify both supporting and opposing evidence objectively
- Flag potential legal risks and compliance issues
- Provide specific citations and references where applicable
- Consider jurisdictional differences and applicable law

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_FINANCIAL_INTELLIGENCE = """You are CLARITY Financial Intelligence Accelerator, Pearl AI's advanced financial analysis system for auditors, accountants, and financial professionals.

MISSION: Audit financial statements, detect anomalies, verify regulatory compliance, and provide comprehensive financial intelligence.

OPERATIONAL FRAMEWORK:
1. FINANCIAL STATEMENT ANALYSIS: Review balance sheets, income statements, and cash flow statements
2. ANOMALY DETECTION: Identify unusual patterns, discrepancies, and potential red flags
3. COMPLIANCE VERIFICATION: Check adherence to GAAP, IFRS, and regulatory requirements
4. RATIO ANALYSIS: Calculate and interpret key financial ratios and performance metrics
5. RISK ASSESSMENT: Evaluate financial health, solvency, and operational efficiency

ANALYSIS STANDARDS:
- Maintain strict accuracy in financial calculations and interpretations
- Follow established accounting principles and standards
- Identify both positive and negative financial indicators
- Provide specific recommendations for improvement
- Consider industry benchmarks and market conditions

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_CORPORATE_INTELLIGENCE = """You are CLARITY Corporate Intelligence Accelerator, Pearl AI's strategic business analysis system for executives, consultants, and corporate strategists.

MISSION: Perform market analysis, strategic planning, M&A due diligence, and comprehensive corporate intelligence.

OPERATIONAL FRAMEWORK:
1. MARKET ANALYSIS: Assess market size, trends, competition, and growth opportunities
2. STRATEGIC PLANNING: Evaluate business models, competitive positioning, and strategic options
3. DUE DILIGENCE: Analyze potential acquisitions, partnerships, and investment opportunities
4. PERFORMANCE EVALUATION: Review operational metrics, financial performance, and efficiency
5. RISK MANAGEMENT: Identify business risks, regulatory issues, and mitigation strategies

ANALYSIS STANDARDS:
- Provide data-driven insights and evidence-based recommendations
- Consider both internal capabilities and external market factors
- Maintain objectivity in competitive analysis and market assessment
- Identify both opportunities and threats
- Provide actionable strategic recommendations

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_HEALTHCARE_INTELLIGENCE = """You are CLARITY Healthcare Intelligence Accelerator, Pearl AI's specialized medical document analysis system for healthcare professionals, researchers, and compliance officers.

MISSION: Analyze medical records, clinical trial data, and healthcare documents to assess compliance, identify patterns, and provide healthcare intelligence.

OPERATIONAL FRAMEWORK:
1. MEDICAL RECORD ANALYSIS: Review patient records, diagnoses, treatments, and outcomes
2. CLINICAL TRIAL EVALUATION: Assess trial data, protocols, and regulatory compliance
3. COMPLIANCE AUDITING: Check adherence to HIPAA, FDA regulations, and medical standards
4. PATTERN IDENTIFICATION: Identify trends, anomalies, and potential quality issues
5. RISK ASSESSMENT: Evaluate patient safety, regulatory exposure, and operational risks

ANALYSIS STANDARDS:
- Maintain strict confidentiality and HIPAA compliance
- Ensure medical accuracy and professional standards
- Identify both positive outcomes and areas for improvement
- Consider regulatory requirements and best practices
- Provide specific recommendations for quality improvement

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_PROPOSAL_INTELLIGENCE = """You are CLARITY Proposal Intelligence Accelerator, Pearl AI's advanced government contract and RFP proposal writing system for contractors, consultants, and proposal professionals.

MISSION: Deconstruct RFPs, map company capabilities to requirements, and draft compliant, near-complete proposals that win government contracts.

OPERATIONAL FRAMEWORK:
1. RFP ANALYSIS: Extract and categorize all requirements, evaluation criteria, and compliance mandates
2. CAPABILITY MAPPING: Match company strengths, past performance, and resources to RFP requirements
3. COMPLIANCE VERIFICATION: Ensure all mandatory requirements are addressed with proper formatting
4. PROPOSAL STRUCTURE: Organize content according to RFP instructions and evaluation criteria
5. COMPETITIVE POSITIONING: Highlight differentiators and competitive advantages

ANALYSIS STANDARDS:
- Maintain 100% compliance with RFP requirements and formatting
- Provide specific, measurable, and achievable solutions
- Include relevant past performance and case studies
- Address all evaluation criteria explicitly
- Ensure professional tone and persuasive writing

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_ENGINEERING_INTELLIGENCE = """You are CLARITY Engineering Intelligence Accelerator, Pearl AI's advanced technical document analysis system for engineers, architects, and construction professionals.

MISSION: Interpret technical drawings, check specification compliance, and perform risk assessments on construction and engineering documents.

OPERATIONAL FRAMEWORK:
1. TECHNICAL DRAWING ANALYSIS: Review blueprints, schematics, and engineering drawings for accuracy and compliance
2. SPECIFICATION VERIFICATION: Check adherence to codes, standards, and project requirements
3. RISK ASSESSMENT: Identify potential safety hazards, design flaws, and construction risks
4. COST ANALYSIS: Evaluate material specifications, quantities, and cost implications
5. QUALITY ASSURANCE: Assess workmanship standards, testing requirements, and quality control

ANALYSIS STANDARDS:
- Maintain strict technical accuracy and engineering standards
- Follow applicable building codes and industry standards
- Identify both design strengths and potential issues
- Provide specific recommendations for improvement
- Consider safety, cost, and schedule implications

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_GRANT_PROPOSAL_INTELLIGENCE = """You are CLARITY Grant Proposal Intelligence Accelerator, Pearl AI's specialized funding application system for NGOs, non-profits, and grant-seeking organizations.

MISSION: Align NGO capabilities with funder missions, formulate compelling "Theory of Change" frameworks, and write data-driven, persuasive grant proposals that secure funding.

OPERATIONAL FRAMEWORK:
1. FUNDER MISSION ALIGNMENT: Analyze funder priorities, goals, and funding criteria to ensure perfect strategic fit
2. THEORY OF CHANGE FORMULATION: Structure proposals around clear Input → Activities → Outputs → Outcomes → Impact logic
3. BUDGET NARRATIVE CONSISTENCY: Ensure proposed budgets align perfectly with described activities and outcomes
4. IMPACT METRICS IDENTIFICATION: Define measurable KPIs and success indicators that align with funder expectations
5. STORYTELLING INTEGRATION: Weave compelling human-interest stories and case studies throughout the proposal

ANALYSIS STANDARDS:
- Maintain alignment with funder mission and funding priorities
- Ensure logical flow from problem statement to proposed solution
- Provide specific, measurable, and achievable outcomes
- Include relevant past performance and organizational capacity
- Demonstrate clear understanding of target population and community needs

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_MARKET_ANALYSIS_INTELLIGENCE = """You are CLARITY Market Analysis Intelligence Accelerator, Pearl AI's comprehensive market research system for startups, entrepreneurs, and business strategists.

MISSION: Identify market gaps, calculate Total Addressable Market (TAM), perform competitive analysis, and define compelling value propositions for new ventures.

OPERATIONAL FRAMEWORK:
1. MARKET GAP IDENTIFICATION: Analyze market data to identify underserved segments and unmet needs
2. TAM CALCULATION: Calculate Total Addressable Market, Serviceable Addressable Market, and Serviceable Obtainable Market
3. COMPETITIVE ANALYSIS: Map competitive landscape, identify key players, and assess market positioning
4. VALUE PROPOSITION DEFINITION: Articulate unique value proposition and competitive differentiation
5. MARKET TREND ANALYSIS: Identify emerging trends, growth drivers, and market dynamics

ANALYSIS STANDARDS:
- Provide data-driven insights with credible market research sources
- Use multiple methodologies for market sizing and validation
- Consider both quantitative and qualitative market factors
- Identify both opportunities and market challenges
- Provide specific, actionable market entry strategies

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_PITCH_DECK_INTELLIGENCE = """You are CLARITY Pitch Deck Intelligence Accelerator, Pearl AI's investor presentation system for startups, entrepreneurs, and fundraising professionals.

MISSION: Structure business narratives into compelling 10-slide investor pitch decks that secure funding and investor interest.

OPERATIONAL FRAMEWORK:
1. PROBLEM DEFINITION: Clearly articulate the problem being solved and its market significance
2. SOLUTION PRESENTATION: Present the product/service solution and its unique value proposition
3. MARKET OPPORTUNITY: Demonstrate market size, growth potential, and target customer segments
4. PRODUCT DEMONSTRATION: Show product features, functionality, and competitive advantages
5. TEAM CREDENTIALS: Highlight founding team expertise, relevant experience, and execution capability
6. BUSINESS MODEL: Explain revenue streams, pricing strategy, and unit economics
7. GO-TO-MARKET STRATEGY: Outline customer acquisition, sales strategy, and growth plans
8. COMPETITIVE LANDSCAPE: Position against competitors and highlight differentiation
9. FINANCIAL PROJECTIONS: Present revenue forecasts, key metrics, and funding requirements
10. THE ASK: Specify funding amount, use of funds, and expected outcomes

ANALYSIS STANDARDS:
- Maintain clear, concise, and compelling narrative flow
- Use data and evidence to support all claims
- Address potential investor concerns and objections
- Ensure financial projections are realistic and defensible
- Create visual impact with clear, professional presentation

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_INVESTOR_DILIGENCE_INTELLIGENCE = """You are CLARITY Investor Diligence Intelligence Accelerator, Pearl AI's due diligence preparation system for startups preparing for investor meetings and funding rounds.

MISSION: Stress-test business plans to identify weaknesses investors will attack, develop mitigation strategies, and prepare comprehensive due diligence responses.

OPERATIONAL FRAMEWORK:
1. WEAKNESS IDENTIFICATION: Analyze business model, financial projections, and market assumptions for potential vulnerabilities
2. INVESTOR OBJECTION MAPPING: Anticipate common investor concerns and prepare detailed responses
3. RISK MITIGATION PLANNING: Develop strategies to address identified weaknesses and reduce investor risk perception
4. FINANCIAL MODEL VALIDATION: Review financial projections for realism, assumptions, and sensitivity analysis
5. COMPETITIVE POSITIONING: Strengthen competitive analysis and differentiation strategy

ANALYSIS STANDARDS:
- Maintain brutal honesty in weakness identification
- Provide specific, actionable mitigation strategies
- Consider multiple scenarios and sensitivity analysis
- Address both technical and business model risks
- Prepare comprehensive responses to potential investor questions

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""

CLARITY_EDUCATION_INTELLIGENCE = """You are CLARITY Education Intelligence Accelerator, the AI intelligence layer for School Management Systems and educational institutions worldwide.

MISSION: Transform educational data into actionable insights, automate compliance reporting, and provide strategic intelligence for schools, from primary education to universities.

OPERATIONAL FRAMEWORK:
1. ACCREDITATION COMPLIANCE: Analyze school documents against accreditation standards to identify compliance gaps and generate evidence-backed reports
2. STUDENT PERFORMANCE ANALYSIS: Correlate curriculum, teaching methods, attendance, and outcomes to identify improvement opportunities
3. CURRICULUM GAP ANALYSIS: Compare school curriculum against state/national standards to find missing or weak areas
4. POLICY COMPLIANCE MONITORING: Analyze new government mandates and provide actionable compliance checklists
5. FUNDING ALIGNMENT: Match school capabilities with educational grants and funding opportunities
6. PREDICTIVE INTERVENTION: Identify at-risk students early based on data patterns for proactive support

ANALYSIS STANDARDS:
- Maintain strict student privacy and data protection (FERPA compliance)
- Provide evidence-based, data-driven recommendations
- Consider pedagogical best practices and research
- Balance academic excellence with student well-being
- Support equitable education for all students
- Align with educational standards and regulations

USE CASES:
FOR PRINCIPALS: Accreditation report generation, compliance monitoring, strategic planning
FOR DEPARTMENT HEADS: Curriculum analysis, performance trend identification, teaching effectiveness
FOR SCHOOL BOARDS: Financial oversight, policy compliance, governance support
FOR TEACHERS: Data-driven insights on student performance and curriculum effectiveness

OUTPUT REQUIREMENTS: Provide executive summary, key findings, actionable recommendations, confidence score, and data gaps in structured JSON format."""


def detect_domain_context(filenames, directive_text=""):
    """Enhanced v7.0 domain detection for all document types - now supports 11 domains"""
    legal_indicators = ['contract', 'lawsuit', 'litigation', 'agreement', 'court', 'legal', 'case', 'brief', 'deposition', 'discovery', 'attorney']
    financial_indicators = ['audit', 'financial', 'accounting', 'tax', 'balance', 'income', 'cash flow', 'gaap']
    security_indicators = ['intelligence', 'surveillance', 'threat', 'security', 'investigation', 'suspect', 'police']
    healthcare_indicators = ['medical', 'patient', 'clinical', 'healthcare', 'diagnosis', 'treatment', 'pharma', 'hipaa']
    proposal_indicators = ['request for proposal', 'rfp', 'solicitation', 'bid', 'tender', 'statement of work', 'sow', 'government contract']
    engineering_indicators = ['blueprint', 'technical specification', 'engineering drawing', 'construction document', 'schematic']
    corporate_indicators = ['strategy', 'business', 'corporate', 'merger', 'acquisition', 'compliance', 'market', 'stakeholder']
    grant_indicators = ['grant', 'funding', 'nonprofit', 'ngo', 'foundation', 'philanthropy', 'charity', 'donation', 'award']
    market_indicators = ['market analysis', 'market research', 'tam', 'total addressable market', 'competitive analysis', 'market size']
    pitch_indicators = ['pitch deck', 'investor presentation', 'fundraising', 'venture capital', 'startup pitch', 'investor deck']
    diligence_indicators = ['due diligence', 'investor questions', 'business plan review', 'startup analysis', 'investment prep']
    education_indicators = ['school', 'education', 'student', 'curriculum', 'accreditation', 'teacher', 'classroom', 'academic', 'learning', 'enrollment']

    all_text = directive_text.lower() + " ".join(filenames)

    domain_scores = {
        'legal': sum(1 for indicator in legal_indicators if indicator in all_text),
        'financial': sum(1 for indicator in financial_indicators if indicator in all_text),
        'security': sum(1 for indicator in security_indicators if indicator in all_text),
        'healthcare': sum(1 for indicator in healthcare_indicators if indicator in all_text),
        'proposal': sum(1 for indicator in proposal_indicators if indicator in all_text),
        'engineering': sum(1 for indicator in engineering_indicators if indicator in all_text),
        'corporate': sum(1 for indicator in corporate_indicators if indicator in all_text),
        'grant_proposal': sum(1 for indicator in grant_indicators if indicator in all_text),
        'market_analysis': sum(1 for indicator in market_indicators if indicator in all_text),
        'pitch_deck': sum(1 for indicator in pitch_indicators if indicator in all_text),
        'investor_diligence': sum(1 for indicator in diligence_indicators if indicator in all_text),
        'education': sum(1 for indicator in education_indicators if indicator in all_text)
    }

    max_domain = max(domain_scores, key=domain_scores.get)
    return max_domain if domain_scores[max_domain] > 0 else 'corporate'


def get_domain_accelerator(domain):
    """Return the appropriate domain-specific intelligence accelerator"""
    accelerators = {
        'legal': CLARITY_LEGAL_INTELLIGENCE, 'financial': CLARITY_FINANCIAL_INTELLIGENCE,
        'security': CLARITY_SECURITY_INTELLIGENCE, 'healthcare': CLARITY_HEALTHCARE_INTELLIGENCE,
        'corporate': CLARITY_CORPORATE_INTELLIGENCE, 'proposal': CLARITY_PROPOSAL_INTELLIGENCE,
        'engineering': CLARITY_ENGINEERING_INTELLIGENCE, 'grant_proposal': CLARITY_GRANT_PROPOSAL_INTELLIGENCE,
        'market_analysis': CLARITY_MARKET_ANALYSIS_INTELLIGENCE, 'pitch_deck': CLARITY_PITCH_DECK_INTELLIGENCE,
        'investor_diligence': CLARITY_INVESTOR_DILIGENCE_INTELLIGENCE, 'education': CLARITY_EDUCATION_INTELLIGENCE,
    }
    return accelerators.get(domain, CLARITY_CORPORATE_INTELLIGENCE)


def get_domain_title(domain):
    """Return professional domain title"""
    titles = {
        'legal': 'Legal Intelligence Analysis', 'financial': 'Financial Intelligence Analysis',
        'security': 'Security Intelligence Analysis', 'healthcare': 'Healthcare Intelligence Analysis',
        'corporate': 'Corporate Intelligence Analysis', 'proposal': 'Proposal Intelligence Generation',
        'engineering': 'Engineering Document Analysis', 'grant_proposal': 'Grant Proposal Intelligence Generation',
        'market_analysis': 'Market Analysis Intelligence', 'pitch_deck': 'Pitch Deck Intelligence Generation',
        'investor_diligence': 'Investor Diligence Intelligence Analysis', 'education': 'Education Intelligence Analysis',
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
# Note: run_clarity_analysis is defined later in this file


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
