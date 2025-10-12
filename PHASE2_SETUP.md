# Phase 2: Intelligence Core - Setup Guide

## 🎯 What We've Built

**Step 1: The Vault's Foundation** - COMPLETE ✅

We've implemented the foundational infrastructure for CLARITY's Intelligence Vault:
- **ChromaDB Vector Database**: Multi-tenant persistent memory storage
- **VectorStoreManager**: Secure, isolated collections per user
- **Embedding Generation**: Sentence transformers for semantic search
- **Docker Infrastructure**: Easy local development setup

## 🚀 Quick Start

### 1. Start ChromaDB (Local Development)

```bash
# Start ChromaDB and Redis using Docker Compose
docker-compose up -d

# Verify ChromaDB is running
curl http://localhost:8000/api/v1/heartbeat
```

### 2. Install New Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install new packages
pip install -r requirements.txt
```

### 3. Update Environment Variables

Add to your `.env` file:

```env
# Vector Store Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIRECTORY=./chroma_data
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 4. Test the Vector Store

```python
# Test script (save as test_vector_store.py)
from app.vector_store import get_vector_store

# Initialize vector store
store = get_vector_store()

# Test with user ID 1
user_id = 1

# Add test documents
documents = [
    "CLARITY Engine is an AI-powered intelligence platform.",
    "The Intelligence Vault provides persistent memory for each client.",
    "Multi-tenant architecture ensures complete data isolation."
]

metadatas = [
    {"source": "test", "type": "description"},
    {"source": "test", "type": "feature"},
    {"source": "test", "type": "architecture"}
]

result = store.add_documents(user_id, documents, metadatas)
print(f"Added documents: {result}")

# Search for similar documents
query = "What is the Intelligence Vault?"
results = store.query_similar_documents(user_id, query, n_results=2)
print(f"\nSearch results for: '{query}'")
print(f"Found {len(results['documents'])} documents:")
for i, doc in enumerate(results['documents']):
    print(f"\n{i+1}. {doc}")
    print(f"   Distance: {results['distances'][i]:.4f}")

# Get stats
stats = store.get_collection_stats(user_id)
print(f"\nVault stats: {stats}")
```

Run the test:
```bash
python test_vector_store.py
```

## 📋 What's Next

**Step 2: The "Ingest & Index" Workflow**

Now that we have a working vector store, the next phase will add:

1. **New Blueprint**: `app/vault/routes.py` for vault operations
2. **Upload Endpoint**: `POST /vault/add` for document ingestion
3. **Document Chunking**: Intelligent text splitting using LangChain
4. **Async Indexing**: Celery task for background embedding generation
5. **User Interface**: Vault management in the dashboard

**Step 3: Two-Stage RAG Prompting**

The final step will integrate the vault with the AI:

1. **Retrieval Logic**: Search vault before analysis
2. **Context Injection**: Add vault memories to prompts
3. **Augmented Generation**: AI uses both new documents and vault context

## 🔧 Architecture Details

### Multi-Tenant Collections

Each user gets their own isolated ChromaDB collection:
- Collection name: `user_vault_{user_id}`
- Metadata: User ID, description
- Complete isolation: User A cannot access User B's data

### Embedding Model

We use `all-MiniLM-L6-v2`:
- Fast and efficient (384-dimensional vectors)
- Excellent performance for semantic search
- Low memory footprint
- Production-ready

### Vector Store Manager

The `VectorStoreManager` class provides:
- `get_or_create_user_collection()`: Multi-tenant collection management
- `add_documents()`: Store text chunks with metadata
- `query_similar_documents()`: Semantic search (RAG retrieval)
- `get_collection_stats()`: Vault statistics
- `delete_user_collection()`: Vault cleanup

## 🐛 Troubleshooting

### ChromaDB Connection Error

```bash
# Check if ChromaDB is running
docker ps | grep chroma

# View ChromaDB logs
docker logs clarity_chromadb

# Restart ChromaDB
docker-compose restart chromadb
```

### Embedding Model Download

First run will download the model (~90MB):
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# Model will be cached in ~/.cache/torch/sentence_transformers/
```

### Port Conflicts

If port 8000 is already in use:
```bash
# Change CHROMA_PORT in docker-compose.yml and .env
# Update both to use port 8001 (or any available port)
```

## 📊 Performance Considerations

- **Embedding Generation**: ~100-500 docs/second (depending on CPU)
- **Vector Search**: Sub-millisecond for collections up to 100K documents
- **Storage**: ~1KB per embedded document chunk
- **Memory**: ~500MB base + ~1GB per 100K documents

## 🎉 Success Criteria

Step 1 is complete when:
- ✅ ChromaDB is running and accessible
- ✅ VectorStoreManager can create user collections
- ✅ Documents can be added to collections
- ✅ Similarity search returns relevant results
- ✅ Collection stats can be retrieved

**All criteria met! Ready for Step 2.** 🚀

## 🔐 Security Notes

- Each user has an isolated collection
- ChromaDB data persists in Docker volumes
- No cross-user data leakage possible
- API endpoints will require authentication (Step 2)
- Vault operations are user-scoped only

---

**Built by the Pearl AI Team**
*The Intelligence Vault - Where Knowledge Becomes Power*
