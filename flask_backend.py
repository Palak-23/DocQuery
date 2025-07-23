# flask_backend.py (Flask API Backend)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from dotenv import load_dotenv
import PyPDF2
import faiss
import numpy as np
from openai import OpenAI
import tiktoken
from typing import List, Tuple
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#added for railway deployment
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

# Global variables for document storage
document_chunks = []
document_embeddings = None
faiss_index = None
chunk_metadata = []


class DocumentProcessor:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_chunk_size = 800
        self.chunk_overlap = 100

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n[Page {page_num + 1}]\n{page_text}"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def chunk_text(self, text: str, filename: str) -> List[Tuple[str, dict]]:
        """Split text into chunks with metadata"""
        chunks = []
        tokens = self.encoding.encode(text)

        for i in range(0, len(tokens), self.max_chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.max_chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)

            metadata = {
                'filename': filename,
                'chunk_index': len(chunks),
                'start_token': i,
                'end_token': i + len(chunk_tokens)
            }

            chunks.append((chunk_text, metadata))

        return chunks

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for text chunks using OpenAI"""
        try:
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )

            embeddings = []
            for embedding in response.data:
                embeddings.append(embedding.embedding)

            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return None


class VectorStore:
    def __init__(self):
        self.index = None
        self.dimension = 1536  # OpenAI ada-002 embedding dimension

    def create_index(self, embeddings: np.ndarray):
        """Create FAISS index from embeddings"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar documents"""
        if self.index is None:
            return None, None

        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), k)
        return distances[0], indices[0]


# Initialize components
processor = DocumentProcessor()
vector_store = VectorStore()


@app.route('/upload', methods=['POST'])
def upload_documents():
    """Handle document upload and processing"""
    global document_chunks, document_embeddings, faiss_index, chunk_metadata

    try:
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files provided'}), 400

        # Reset global variables
        document_chunks = []
        chunk_metadata = []
        all_chunks = []

        # Process each uploaded file
        for file in files:
            if file and file.filename.endswith('.pdf'):
                # Extract text from PDF
                text = processor.extract_text_from_pdf(file)
                if text:
                    # Chunk the text
                    chunks = processor.chunk_text(text, file.filename)

                    for chunk_text, metadata in chunks:
                        document_chunks.append(chunk_text)
                        chunk_metadata.append(metadata)
                        all_chunks.append(chunk_text)

        if not all_chunks:
            return jsonify({'error': 'No text extracted from PDFs'}), 400

        # Generate embeddings
        embeddings = processor.get_embeddings(all_chunks)
        if embeddings is None:
            return jsonify({'error': 'Failed to generate embeddings'}), 500

        # Create FAISS index
        vector_store.create_index(embeddings)
        document_embeddings = embeddings

        return jsonify({
            'message': 'Documents processed successfully',
            'num_chunks': len(all_chunks),
            'num_files': len(files)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/query', methods=['POST'])
def query_documents():
    """Handle question answering"""
    try:
        data = request.json
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        if not document_chunks or vector_store.index is None:
            return jsonify({'error': 'No documents processed yet'}), 400

        # Get question embedding
        question_embedding = processor.get_embeddings([question])
        if question_embedding is None:
            return jsonify({'error': 'Failed to generate question embedding'}), 500

        # Search for relevant chunks
        distances, indices = vector_store.search(question_embedding[0], k=3)

        if indices is None:
            return jsonify({'error': 'Search failed'}), 500

        # Retrieve relevant chunks
        relevant_chunks = []
        sources = []

        for idx in indices:
            if idx < len(document_chunks):
                chunk = document_chunks[idx]
                metadata = chunk_metadata[idx]
                relevant_chunks.append(chunk)
                sources.append(
                    f"File: {metadata['filename']}, Chunk: {metadata['chunk_index']}")

        # Generate answer using OpenAI
        context = "\n\n".join(relevant_chunks)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided context. Use only the information from the context to answer questions. If you cannot find the answer in the context, say so."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
                }
            ],
            max_tokens=500,
            temperature=0.1
        )

        answer = response.choices[0].message.content.strip()

        return jsonify({
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
