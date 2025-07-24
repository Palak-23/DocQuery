# DocQuery - PDF Question Answering System

A web application that allows users to upload PDF documents and ask questions about their content using AI-powered search and natural language processing.

## 🚀 Live Demo

[https://docquery-production.up.railway.app](https://docquery-production.up.railway.app)

## 🛠️ Technologies Used

- **Frontend**: Streamlit
- **Backend**: Flask
- **Vector Database**: FAISS
- **AI/ML**: OpenAI API (GPT-3.5-turbo, text-embedding-ada-002)
- **PDF Processing**: PyPDF2
- **Deployment**: Railway
- **Container**: Docker

## 📋 Features

- Upload multiple PDF documents
- Extract and process text from PDFs
- Generate embeddings for semantic search
- Ask questions in natural language
- Get AI-powered answers with source citations
- Real-time document processing

## 🏗️ Architecture

```
┌─────────────────┐    HTTP Requests    ┌──────────────────┐
│   Streamlit     │ ──────────────────> │   Flask API      │
│   (Frontend)    │                     │   (Backend)      │
│   Port: 8501    │ <────────────────── │   Port: 5000     │
└─────────────────┘    JSON Responses   └──────────────────┘
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │   FAISS Index    │
                                        │ (Vector Storage) │
                                        └──────────────────┘
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │   OpenAI API     │
                                        │ (Embeddings/LLM) │
                                        └──────────────────┘
```

## 🔄 Application Flow

1. **Upload**: User uploads PDF files through Streamlit interface
2. **Process**: Flask backend extracts text and creates embeddings using OpenAI
3. **Index**: FAISS creates vector index for semantic search
4. **Query**: User asks questions about the documents
5. **Search**: System finds relevant document chunks using vector similarity
6. **Answer**: OpenAI generates answers based on retrieved context

## 📁 Project Structure

```
docquery/
├── app.py              # Streamlit frontend
├── flask_backend.py    # Flask API backend
├── run.py             # Local development runner
├── Dockerfile         # Container configuration
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## 🚀 Quick Start

1. Clone the repository
2. Set your OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Run locally:
   ```bash
   python run.py
   ```
4. Open [http://localhost:8501](http://localhost:8501)

## 📝 Usage

1. Upload one or more PDF files
2. Click "Process Documents" to extract and index content
3. Ask questions about your documents
4. Get AI-powered answers with source references

## 🔧 Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Application port (set automatically by Railway)

---

Built with ❤️ using modern AI and web technologies
