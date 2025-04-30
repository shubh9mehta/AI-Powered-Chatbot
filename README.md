# IU Research Chatbot

A Flask-based intelligent assistant for the Indiana University Research Data Commons (IURDC), powered by OpenAI's GPT-4o and semantic search using SentenceTransformers.

This project is designed for non-technical users at IU to search institutional research knowledge through natural language. The chatbot can answer general questions, draft emails, and generate research proposals using structured internal documentation.

---

## ✨ Key Features

- 🤖 **AI Chatbot with Natural Language Interface**
- ⚖️ **Semantic Search** over internal documents (Excel, Word)
- ✉️ **Chat Modes:** General, Email, Proposal
- 🔗 **Integrated with OpenAI GPT-4o** for high-quality responses
- ⌚ **Session-based memory** for smooth multi-turn interactions
- ✅ **Editable and expandable knowledge base**

---

## 📚 How It Works

### 1. Knowledge Base Preparation (`prepare_knowledge_new.py`)

This script processes the raw institutional documents and builds a structured knowledge base (`combined_knowledge_base.json`).

- **Inputs:**
  - Excel files (like FAQs, News Posts, People Directory) from `data/raw/`
  - A webinar transcript `.docx` file

- **Steps:**
  1. Each Excel file is parsed sheet-by-sheet.
  2. Text is cleaned, standardized, and structured.
  3. Unique IDs are created for each entry.
  4. A special NLP-powered summary is generated for the webinar transcript (topics, speakers, Q&A).
  5. All data is merged and saved to `data/processed/combined_knowledge_base.json`.

### 2. Chatbot Server (`server.py`)

This Flask app uses the structured JSON to power an AI chatbot.

- Loads the knowledge base
- Uses `SentenceTransformer` to find the most relevant documents
- Uses OpenAI GPT-4o to generate responses
- Modes:
  - **General Mode**: Answers research-related questions
  - **Email Mode**: Drafts professional emails
  - **Proposal Mode**: Builds a research proposal outline
- Logs every chat interaction to the `logs/` folder


## ♻️ Folder Structure (Final Project)

ChatBot/ 
├── app.py (or server.py) ├── prepare_knowledge_new.py ├── .env ├── data/ │ ├── raw/ # Input Excel + docx files │ └── processed/ # JSON knowledge base ├── static/ # UI styling (CSS, JS) ├── templates/ │ └── index.html # Chatbot UI ├── logs/ # Chat history logs └── requirements.txt
