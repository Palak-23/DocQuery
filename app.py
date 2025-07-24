# app.py (Streamlit Frontend)
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import tempfile
import json

load_dotenv()

# Configuration
# FLASK_API_URL = "http://localhost:5000"
FLASK_API_URL = "https://docquery-production.up.railway.app"

st.set_page_config(
    page_title="DocQuery - PDF Question Answering",
    page_icon="📚",
    layout="wide"
)

def main():
    st.title("📚 DocQuery - PDF Question Answering System")
    st.markdown("Upload multiple PDFs and ask questions about their content!")
    
    # Sidebar for file uploads
    with st.sidebar:
        st.header("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload one or more PDF files to query"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            if st.button("🔄 Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    success = process_documents(uploaded_files)
                    if success:
                        st.success("Documents processed successfully!")
                        st.session_state.docs_processed = True
                    else:
                        st.error("Error processing documents")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Questions")
        
        # Check if documents are processed
        if not st.session_state.get('docs_processed', False):
            st.info("👈 Please upload and process PDF documents first using the sidebar.")
            return
        
        # Question input
        question = st.text_input(
            "Enter your question:",
            placeholder="What is this document about?",
            help="Ask any question about the uploaded documents"
        )
        
        if st.button("🔍 Search Answer", type="primary") and question:
            with st.spinner("Searching for answer..."):
                answer, sources = get_answer(question)
                
                if answer:
                    st.subheader("📋 Answer")
                    st.write(answer)
                    
                    if sources:
                        st.subheader("📖 Sources")
                        for i, source in enumerate(sources, 1):
                            with st.expander(f"Source {i}"):
                                st.write(source)
                else:
                    st.error("Could not find an answer. Please try rephrasing your question.")
    
    with col2:
        st.header("ℹ️ Information")
        st.info("""
        **How to use:**
        1. Upload PDF files using the sidebar
        2. Click 'Process Documents'
        3. Ask questions about the content
        4. Get AI-powered answers with sources
        """)
        
        if st.session_state.get('docs_processed', False):
            st.success("✅ Documents are ready for querying!")

# def process_documents(uploaded_files):
#     """Send documents to Flask API for processing"""
#     try:
#         files = []
#         for uploaded_file in uploaded_files:
#             files.append(('files', (uploaded_file.name, uploaded_file.read(), 'application/pdf')))
        
#         response = requests.post(f"{FLASK_API_URL}/upload", files=files)
#         return response.status_code == 200
#     except Exception as e:
#         st.error(f"Error: {str(e)}")
#         return False

def process_documents(uploaded_files):
    """Send documents to Flask API for processing"""
    try:
        files = []
        for uploaded_file in uploaded_files:
            uploaded_file.seek(0)  # 🔧 Reset file pointer to start
            files.append(('files', (uploaded_file.name, uploaded_file.read(), 'application/pdf')))
        
        response = requests.post(f"{FLASK_API_URL}/upload", files=files)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def get_answer(question):
    """Get answer from Flask API"""
    try:
        response = requests.post(
            f"{FLASK_API_URL}/query",
            json={"question": question}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('answer'), data.get('sources', [])
        else:
            return None, []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, []

if __name__ == "__main__":
    main()
