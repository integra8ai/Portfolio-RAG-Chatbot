"""
Portfolio RAG Chatbot — Multi-Format Document Loader
Reads all supported files from the data/ folder
"""

import streamlit as st
import os
import glob
from supabase import create_client
from google import genai  # NEW: google-genai SDK (replaces google.generativeai)
import time

# ============================================================
# CONFIGURATION — Read from environment or secrets
# ============================================================

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ============================================================
# INITIALIZE CLIENTS
# ============================================================

# NEW: Create a single client object (google-genai SDK)
client = genai.Client(api_key=GOOGLE_API_KEY)

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================
# MULTI-FORMAT DOCUMENT LOADER (from data/ folder)
# ============================================================

def load_documents_from_folder():
    """
    Read all supported file types from the data/ folder.
    Supported: .md, .txt, .pdf, .docx, .csv, .pptx, .html
    """
    documents = []
    data_dir = "data"
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        return documents
    
    # NEW: Using standalone packages instead of langchain-community
    from langchain_community.document_loaders import (
        TextLoader,
        UnstructuredMarkdownLoader,
        PyPDFLoader,
        UnstructuredWordDocumentLoader,
        CSVLoader,
        UnstructuredPowerPointLoader,
        UnstructuredHTMLLoader
    )
    
    extensions = {
        ".md": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".csv": CSVLoader,
        ".pptx": UnstructuredPowerPointLoader,
        ".html": UnstructuredHTMLLoader,
    }
    
    # Gather all files with supported extensions
    all_files = []
    for ext in extensions:
        all_files.extend(glob.glob(os.path.join(data_dir, f"*{ext}")))
    
    for filepath in all_files:
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            loader_class = extensions.get(ext)
            if loader_class is None:
                continue
            
            # Handle TextLoader special case: it needs encoding
            if loader_class == TextLoader:
                loader = loader_class(filepath, encoding="utf-8")
            else:
                loader = loader_class(filepath)
            
            # Load and combine content
            docs = loader.load()
            content = "\n\n".join([doc.page_content for doc in docs])
            
            documents.append({
                "id": filename.replace(ext, ""),
                "content": content,
                "source": filename
            })
            
        except Exception as e:
            st.warning(f"⚠️ Could not load {filename}: {e}")
    
    return documents

# ============================================================
# VECTOR DATABASE SETUP (Supabase pgvector)
# ============================================================

def get_embedding(text):
    """Generate embedding using the new google-genai SDK"""
    try:
        # NEW: Use client.models.embed_content (google-genai SDK)
        result = client.models.embed_content(
            model="models/text-embedding-004",
            contents=[text]
        )
        return result.embeddings[0].values
    except Exception as e:
        st.error(f"Error generating embedding: {e}")
        return None

def setup_vector_db():
    """Create table and index, then populate with documents from data/ folder"""
    
    # --- STEP 1: ALWAYS CREATE TABLE FIRST ---
    try:
        # Create the table
        supabase.sql("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source TEXT,
                embedding VECTOR(768)
            );
        """).execute()
        
        # Create index for faster search
        supabase.sql("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents USING ivfflat (embedding vector_cosine_ops);
        """).execute()
        
        # Create the match_documents function
        supabase.sql("""
            CREATE OR REPLACE FUNCTION match_documents(
                query_embedding VECTOR(768),
                match_threshold FLOAT,
                match_count INT
            )
            RETURNS TABLE(
                id TEXT,
                content TEXT,
                source TEXT,
                similarity FLOAT
            )
            LANGUAGE SQL STABLE
            AS $$
                SELECT
                    documents.id,
                    documents.content,
                    documents.source,
                    1 - (documents.embedding <=> query_embedding) AS similarity
                FROM documents
                WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
                ORDER BY documents.embedding <=> query_embedding
                LIMIT match_count;
            $$;
        """).execute()
        
        st.success("✅ Table ready")
        
    except Exception as e:
        st.error(f"Error creating table: {e}")
        return
    
    # --- STEP 2: LOAD DOCUMENTS ---
    documents = load_documents_from_folder()
    
    if not documents:
        st.info("No supported documents found in the data/ folder. Add .md, .pdf, .docx, .csv, .txt, .pptx, or .html files.")
        return
    
    # --- STEP 3: INSERT DOCUMENTS ---
    loaded_count = 0
    for doc in documents:
        try:
            # Check if document already exists
            existing = supabase.table("documents").select("id").eq("id", doc["id"]).execute()
            if existing.data:
                continue
            
            embedding = get_embedding(doc["content"])
            if embedding:
                supabase.table("documents").insert({
                    "id": doc["id"],
                    "content": doc["content"],
                    "source": doc["source"],
                    "embedding": embedding
                }).execute()
                loaded_count += 1
                
        except Exception as e:
            st.warning(f"Could not load {doc.get('source', doc['id'])}: {e}")
    
    if loaded_count > 0:
        st.success(f"✅ Loaded {loaded_count} documents from data/ folder")
    else:
        st.info("📁 Documents already loaded or no new documents to add")

def search_documents(query, threshold=0.5, limit=3):
    """Semantic search using pgvector"""
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return []
    
    try:
        response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit
            }
        ).execute()
        return response.data
    except Exception as e:
        st.error(f"Error searching documents: {e}")
        return []

def generate_answer(query, context):
    """Generate an answer using the new google-genai SDK"""
    prompt = f"""You are an AI assistant representing an AI Agent Architect.

    Use the following context to answer the user's question accurately.
    If the answer is not in the context, say "I don't have information about that."
    Always cite the source document.
    
    Context:
    {context}
    
    User Question: {query}
    
    Answer:"""
    
    try:
        # NEW: Use client.models.generate_content (google-genai SDK)
        response = client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating answer: {e}")
        return "I'm having trouble generating a response right now. Please try again."

# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="Integra8 AI — Portfolio Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 700; color: #1a1a2e; }
    .subtitle { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title" style="text-align: center;">🤖 AI Agent Architect</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="text-align: center;">Ask me about my services, case studies, and experience.</p>', unsafe_allow_html=True)

# Sidebar — Show loaded documents
with st.sidebar:
    st.header("📁 Knowledge Base")
    docs = load_documents_from_folder()
    if docs:
        st.success(f"Loaded {len(docs)} documents")
        for doc in docs:
            st.caption(f"• {doc['source']}")
    else:
        st.warning("No documents found. Add supported files to the data/ folder.")

# Initialize knowledge base
with st.spinner("Loading knowledge base..."):
    setup_vector_db()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! I'm an AI assistant representing an AI Agent Architect. I can answer questions about my services, case studies, technical approach, and experience.\n\n**What would you like to know?**"
        }
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about my services..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base..."):
            results = search_documents(prompt)
            
            if results:
                context = "\n\n".join([r["content"] for r in results])
                answer = generate_answer(prompt, context)
                citations = [f"📄 *Source: {r.get('source', r['id'])} (Relevance: {r['similarity']:.2f})*" 
                            for r in results[:3]]
                full_response = answer + "\n\n" + "\n".join(citations)
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.markdown("I couldn't find relevant information in my knowledge base.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I couldn't find relevant information in my knowledge base."
                })

st.divider()
st.caption("Built by Integra8AI with Streamlit · Supabase pgvector · Google GenAI SDK")