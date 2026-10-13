To run the main.py - *****python -m uvicorn backend.main:app --reload --port 8000***

TravelWise AI is an AI-powered travel planning application that helps users organize trips and ask questions about travel destinations. It combines a FastAPI backend, a SQLite database, and a RAG - Retrieval-Augmented Generation system, to provide travel information using documents stored in a knowledge base.

2. Architecture Diagram

┌─────────────────────────┐
              │   User                  │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Streamlit Frontend      │
              │ Port 8501               │
              └────────────┬────────────┘
                           │ HTTP Requests
                           ▼
              ┌─────────────────────────┐
              │ FastAPI Backend         │
              │ Port 8000               │
              │ JWT Authentication      │
              │ Trip Management         │
              │ RAG Question Answering  │
              └──────┬──────────┬───────┘
                     │          │
             ┌───────▼────┐  ┌──▼────────────────┐
             │ SQLite     │  │ RAG Knowledge Base│
             │ SQLAlchemy │  │ ChromaDB          │
             │ Users      │  │ Travel Documents  │
             │ Trips      │  └────────┬──────────┘
             │ Destinations│          │
             └────────────┘           ▼
                            ┌────────────────────┐
                            │ Ollama             │
                            │ llama3.2:1b        │
                            │ AI Responses       │
                            └────────────────────┘
Docker Compose
       Runs the frontend, backend, and Ollama

3. Prerequisites

Install or have access to the following:
Docker Desktop — runs the application containers.
Docker Compose — starts and connects the application services.
Python 3.9 or newer — used for local development and testing.
Git — used to clone the project repository.
The application uses Ollama with the llama3.2:1b model. Docker Compose manages the Ollama service for the containerized application.

4. Setup Instructions

Step 1: Clone the repository

git clone (https://github.com/CodingTemple-AI-Software-Engineering/module-09-capstone.git)

cd travelwise

If you already have the project on your computer, navigate to the existing project folder instead.

Step 2: Configure environment variables

Copy the example environment file:
cp .env.example .env

Open .env and check that the required environment variables are configured. Keep secrets such as the JWT secret key private. Do not commit .env to GitHub.

Step 3: Start the application

Make sure Docker Desktop is running. From the project root, run:

docker compose up --build -d

This builds the images if necessary and starts the application services in the background.

Step 4: Verify the services

Check the running containers:

docker compose ps

Open the application:

TravelWise AI frontend: http://localhost:8501

FastAPI interactive documentation: http://localhost:8000/docs

API health check: http://localhost:8000/health


To stop the application:
docker compose down

5. Usage Guide

Create an account and log in

-Open the Streamlit frontend at http://localhost:8501.
-Register a user account.
-Log in with your credentials.
-Use the application to create and manage your trips.

Create and manage trips

-Enter a trip name.
-Select an available destination.
-Choose your start and end dates.
-Save the trip.
-View your trips and update or delete them as needed.

Ask travel questions

-Open the AI question-answering section.
-Enter a question about Chicago travel, attractions, transportation, food, or activities.
-Submit the question.
-The RAG system retrieves relevant information from its travel knowledge base and uses the language model to generate an answer.

Travel document ingestion

The project includes travel documents in the docs/ directory:

chicago_overview.txt
attractions.txt
transportation.txt
food_and_activities.txt

These documents provide the information used by the RAG system. Document ingestion loads the text, divides it into chunks, creates embeddings, and stores them in ChromaDB for retrieval.

Note: Confirm how ingestion is triggered in the current implementation—such as automatically at startup or through a separate ingestion command—before documenting a specific command here.


6. API Endpoints

The following endpoints are defined in the FastAPI backend.

Method Endpoint	      Description                              Auth
POST /auth/register	  register a new user                       No
POST /auth/token	  log in/access anew token                  No
GET	 /auth/me	       Retrieve current user info.             Yes
GET	 /destinations	   Retrieve available destination          No
POST /ask	           Ask a travel question using RAG system  No
GET	 /trips	           Retriev current user's trips             Yes
POST /trips	           Create a trip                            Yes
PATCH /trips/{trip_id}  Update an exixting trip	                Yes
DELETE /trips/{trip_id}	Delete a trip                           Yes
GET    /health          Check appliction health                  No
GET   /ingest           Ingest travel documents into chromadb    Yes

Protected endpoints require a valid JWT access token. Register and log in to obtain a token, then use the Authorize control in the interactive API documentation.

For request parameters, validation schemas, and response examples, open:

http://localhost:8000/docs

7. Tech Stack

Python — primary programming language.
FastAPI — REST API backend.
Streamlit — interactive frontend.
SQLAlchemy — database ORM.
SQLite — relational database for users, trips, and destinations.
Pydantic — request and response validation.
JWT — user authentication.
ChromaDB — vector database for document retrieval.
Sentence Transformers — text embeddings.
Ollama — runs the local language model.
llama3.2:1b — language model used for AI responses.
Docker — containerizes application services.
Docker Compose — coordinates the frontend, backend, and Ollama.
Pytest — automated testing.

8. Testing
****docker compose exec backend python -m pytest backend/tests/ -v ****

TravelWise AI uses Pytest to verify authentication, database operations, document retrieval, and AI question answering.

Run the automated test suite from the project root while the backend container is running:

From the project root, run:
docker compose exec backend python -m pytest backend/tests/ -v

The test files are:

Authentication tests: user registration, login, and protected routes.

CRUD tests: creating and listing database records.

RAG tests: retrieving travel documents, generating answers with sources, and applying relevance guardrails.

Latest test results: 8 tests passed, 0 failed.

The test suite completed successfully in 40.67 seconds. Five deprecation warnings were reported; they did not cause any tests to fail.

 Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================= 8 passed, in 40.67s ==================================================================

The -v option displays each test and its result. Confirmed that at least five tests pass before submitting my capstone.

Project Structure

travelwise/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── rag.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
├── frontend/
│   ├── app.py
│   ├── api_client.py
│   ├── requirements.txt
│   └── Dockerfile
├── docs/
├── data/
├── chroma_data/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md

