# # Use official Python 3.10 image
# FROM python:3.10-slim-bookworm

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     swig \
#     git \
#     && apt-get clean

# # Set working directory
# WORKDIR /app

# # Copy everything into the container
# COPY . /app

# # Install Python dependencies
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# # Expose port (change if needed)
# EXPOSE 8501

# # Run the Streamlit app
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Use official Python 3.10 image 
FROM python:3.10-slim-bookworm  

# Install system dependencies 
RUN apt-get update && apt-get install -y \     
    build-essential \     
    swig \     
    git \     
    && apt-get clean  

# Set working directory 
WORKDIR /app  

# Copy everything into the container 
COPY . /app  

# Install Python dependencies 
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt  

# Expose port (Railway will use this)
EXPOSE 8501  

# Create startup script that runs both Flask and Streamlit
RUN echo '#!/bin/bash\n\
echo "Starting Flask backend on port 5000..."\n\
python flask_backend.py &\n\
echo "Waiting for Flask to start..."\n\
sleep 5\n\
echo "Starting Streamlit on port 8501..."\n\
streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run both services
CMD ["/app/start.sh"]
