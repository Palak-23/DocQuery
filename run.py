# run.py (Script to run both services)
import subprocess
import sys
import os
import time
from threading import Thread

def run_flask():
    """Run Flask backend"""
    print("Starting Flask backend...")
    subprocess.run([sys.executable, "flask_backend.py"])

def run_streamlit():
    """Run Streamlit frontend"""
    print("Starting Streamlit frontend...")
    time.sleep(3)  # Wait for Flask to start
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        sys.exit(1)
    
    print("🚀 Starting DocQuery Application...")
    print("📚 Flask API will run on: http://localhost:5000")
    print("🌐 Streamlit app will run on: http://localhost:8501")
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Streamlit in main thread
    run_streamlit()
