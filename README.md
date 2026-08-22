# 🤖 Portfolio RAG Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot that answers questions about your portfolio, services, case studies, and experience - using your own documents.

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation (Windows)](#-installation-windows)
- [Configuration](#-configuration)
- [Adding Your Documents](#-adding-your-documents)
- [Running the App](#-running-the-app)
- [Deploy on Render](#-deploy-on-render-free)
- [How It Works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)
- [Customization](#-customization)
- [Project Structure](#-project-structure)
- [Quick Commands](#-quick-commands-reference)
- [License](#-license)

---

## ✨ Features

- 📄 **Multi-Format Document Support** - Drop `.md`, `.txt`, `.pdf`, `.docx`, `.csv`, `.pptx`, `.html` files into the `data/` folder
- 🔍 **Semantic Search** - Powered by Supabase pgvector for fast, accurate retrieval
- 🤖 **AI-Powered Answers** - Uses Google Gemini 1.5 Flash for grounded, context-aware responses
- 📎 **Source Citations** - Every answer includes the source document and relevance score
- 💬 **Chat Interface** - Clean, conversational UI built with Streamlit
- 🔒 **Secure by Design** - Your data stays in your control
- 🆓 **100% Free** - No credit card required for local development or Render deployment
- ☁️ **Easy Deployment** - Deploy to Render, Streamlit Cloud, or any Python hosting

---

## 🧰 Tech Stack

| Component | Technology |
| ----------- | ------------ |
| **Frontend** | Streamlit |
| **LLM** | Google Gemini 1.5 Flash |
| **Vector Database** | Supabase (pgvector) |
| **Document Loaders** | LangChain (multi-format support) |
| **Embeddings** | Google Gemini Embeddings |
| **Hosting** | Render (free tier) or Local |

---

## 📋 Prerequisites

Before you begin, you'll need:

| Requirement | Where to Get It |
| ------------- | ----------------- |
| **Python 3.10+** | [python.org](https://python.org) |
| **Git** | [git-scm.com](https://git-scm.com) |
| **Supabase Account** | [supabase.com](https://supabase.com) — Free tier |
| **Google Gemini API Key** | [aistudio.google.com](https://aistudio.google.com) — Free tier |

---

## 🚀 Installation (Windows)

### Step 1: Clone the Repository

Open your terminal (Command Prompt, PowerShell, or Git Bash) and run:

```bash
git clone https://github.com/integra8ai/portfolio-rag-chatbot.git
cd portfolio-rag-chatbot
```

### Step 2: Create and Activate Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

You'll see `(venv)` appear in your terminal - this means it's active.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

### Step 1: Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. In the **SQL Editor**, run this query:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

1. Go to **Settings** → **API** and copy:
   - `Project URL`
   - `anon public` key

### Step 2: Get Google Gemini API Key

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **"Get API Key"**
3. Create a new API key (free tier: 1.5M tokens/day)
4. Copy the key

### Step 3: Create Secrets File

Create `.streamlit/secrets.toml` with your API keys:

```toml
# .streamlit/secrets.toml
# ⚠️ DO NOT commit this file to GitHub!

SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_key"
GOOGLE_API_KEY = "your_gemini_api_key"
```

> **Important:** This file is already in `.gitignore`, so it won't be committed.

---

## 📄 Adding Your Documents

Place your documents in the `data/` folder. The app will automatically detect and load them.

### Supported File Formats

| Format | Extension | Example |
| -------- | ----------- | --------- |
| Markdown | `.md` | `01_about.md` |
| Plain Text | `.txt` | `02_resume.txt` |
| PDF | `.pdf` | `03_services.pdf` |
| Word | `.docx` | `04_case_studies.docx` |
| CSV | `.csv` | `05_testimonials.csv` |
| PowerPoint | `.pptx` | `06_presentation.pptx` |
| HTML | `.html` | `07_website.html` |

### Example Folder Structure

```
data/
├── 01_about.md                 # Your introduction and background
├── 02_services.pdf             # Your service offerings
├── 03_case_studies.docx        # Case studies and client work
├── 04_testimonials.csv         # Client testimonials
└── 05_approach.txt             # Your methodology or approach
```

---

## Running the App

```bash
streamlit run app.py
```

Open your browser and go to: `http://localhost:8501`

### Sample Questions to Test

| Question | What It Tests |
| ---------- | --------------- |
| "What are your main services?" | Basic portfolio retrieval |
| "Tell me about the HVAC case study" | Case study retrieval |
| "What technologies do you use?" | Technical stack retrieval |
| "Do you have client testimonials?" | Testimonial retrieval |
| "What's your approach to security?" | Security/approach retrieval |

---

## Deploy on Render (Free)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Deploy to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure as follows:

| Setting | Value |
| --------- | ------- |
| **Name** | `portfolio-rag-chatbot` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |
| **Instance Type** | `Free` |

### Step 3: Add Environment Variables

In the Render dashboard, add these Environment Variables:

| Key | Value |
| ----- | ------- |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon key |
| `GOOGLE_API_KEY` | Your Gemini API key |

### Step 4: Deploy

Click **"Create Web Service"**. Your app will be live at `https://your-app-name.onrender.com` in 3-5 minutes.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER ASKS A QUESTION                         │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              1. EMBEDDING (Google Gemini)                       │
│               Converts question to vector                       │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. VECTOR SEARCH (Supabase pgvector)               │
│               Finds semantically similar documents              │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. CONTEXT RETRIEVAL                               │
│               Extracts relevant chunks from matched docs        │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              4. ANSWER GENERATION (Gemini 1.5 Flash)           │
│               Generates grounded answer with citations          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              5. RESPONSE WITH SOURCES                           │
│               Answer + Source attribution + Relevance scores   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### ❌ "module 'google.generativeai' has no attribute 'embedding_models'"

**Fix:** Update your package:

```bash
pip install --upgrade google-generativeai
```

### ❌ "Relation 'documents' does not exist"

**Fix:** The app creates the table automatically on first run. Ensure your Supabase credentials are correct.

### ❌ "Error loading PDF: No module named 'pypdf'"

**Fix:**

```bash
pip install pypdf
```

### ❌ "Error loading DOCX: No module named 'docx2txt'"

**Fix:**

```bash
pip install docx2txt
```

### ❌ "Error loading CSV: No module named 'pandas'"

**Fix:**

```bash
pip install pandas
```

### ❌ "Port 8501 already in use"

**Fix:** Run on a different port:

```bash
streamlit run app.py --server.port 8502
```

### ❌ "Streamlit app won't start on Render"

**Fix:** Ensure your start command is exactly:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## Customization

### Change Branding

Edit `app.py`:

```python
st.set_page_config(
    page_title="Your Brand - Portfolio Chatbot",
    page_icon="🚀",
    layout="wide"
)
```

### Switch LLM Provider

Replace Gemini with OpenAI, Anthropic, or Fireworks AI by modifying the `generate_answer()` and `get_embedding()` functions in `app.py`.

### Add More File Formats

Extend the `load_documents_from_folder()` function in `app.py`:

```python
extensions = {
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".csv": CSVLoader,
    # Add your custom format here
    ".json": CustomJSONLoader,
}
```

---

## Project Structure

```
portfolio-rag-chatbot/
├── .streamlit/
│   └── secrets.toml          # ← Local secrets (DO NOT commit)
├── data/                     # ← Drop your documents here
│   ├── 01_about.md
│   ├── 02_services.pdf
│   └── ...
├── app.py                    # ← Main application
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Requirements (`requirements.txt`)

```txt
streamlit>=1.28.0
supabase>=2.0.0
google-generativeai>=0.8.0
python-dotenv>=1.0.0
langchain>=0.3.0
langchain-community>=0.3.0
pypdf>=4.0.0
docx2txt>=0.8
unstructured>=0.15.0
markdown>=3.5.0
pandas>=2.0.0
```

---

## Security Best Practices

| Best Practice | Why |
| --------------- | ----- |
| **Never commit secrets** | Add `.streamlit/secrets.toml` to `.gitignore` |
| **Use environment variables** | For Render deployment, use the dashboard |
| **Limit file uploads** | Keep the `data/` folder accessible only to you |
| **Consider VPC self-hosting** | For enterprise clients, deploy inside their VPC |

---

## License

MIT — Use it for anything, commercial or personal.

---

## Support

- **Issues:** Open an issue on GitHub
- **Questions:** DM me for consulting inquiries
- **Tutorial:** Check out the video tutorial on YouTube

---

## Quick Commands Reference

| Task | Command |
| ------ | --------- |
| Clone repo | `git clone https://github.com/yourusername/portfolio-rag-chatbot.git` |
| Enter folder | `cd portfolio-rag-chatbot` |
| Activate venv (Windows) | `venv\Scripts\activate` |
| Activate venv (Mac/Linux) | `source venv/bin/activate` |
| Install dependencies | `pip install -r requirements.txt` |
| Run app | `streamlit run app.py` |
| Deploy to Render | Push to GitHub → Connect in Render dashboard |

---

**Built with ❤️ for the AI Agent Architect community**

---

## ⭐ Star This Repository

If you found this helpful, please give it a star ⭐ on GitHub!

---

**Happy Building! 🚀**
