# backend/Dockerfile  (STARTER)
# ================================
# TODO: Complete this Dockerfile so the backend can run inside Docker.
# Refer to Module 8's Dockerfile Creation lesson for guidance.
#
# Steps to implement:
#   1. Choose a base image — python:3.11-slim is a good choice
#   2. Set a working directory (e.g. /app)
#   3. Copy requirements.txt and install dependencies with pip
#   4. Copy the rest of the source code
#   5. Expose the port uvicorn will listen on (8000)
#   6. Set the CMD to start uvicorn
#      Hint: uvicorn main:app --host 0.0.0.0 --port 8000


# Use Python 3.11
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy and install backend dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY backend/ ./backend/

# Copy travel documents
COPY docs/ ./docs/

# Create directories for persistent data
RUN mkdir -p /app/data /app/chroma_data

# Expose the FastAPI port
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

