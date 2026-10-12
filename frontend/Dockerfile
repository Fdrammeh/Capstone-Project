
# Use Python 3.11
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy and install frontend dependencies
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application
COPY frontend/ ./frontend/

# Expose the Streamlit port
EXPOSE 8501

# Start the Streamlit application
CMD ["streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501"]

