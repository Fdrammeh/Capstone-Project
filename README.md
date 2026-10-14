***The recommended way to run TravelWise AI is with Docker Compose:docker compose up --build -d***
***For local development outside Docker, run the following command from the project root with the required Python dependencies installed:

python -m uvicorn backend.main:app --reload --port 8000***

TravelWise AI is an AI-powered travel planning application that helps users organize trips and ask questions about travel destinations. It combines a FastAPI backend, SQLite database, JWT authentication, and a Retrieval-Augmented Generation (RAG) system to provide document-grounded travel information.

The application uses Streamlit for its user interface, ChromaDB for document retrieval, Sentence Transformers for embeddings, and Ollama to generate AI responses.

1. Features

-User registration and JWT authentication
-Create, view, update, and delete personal trips
-Browse available travel destinations
-Ask natural-language questions about travel information
-Retrieve relevant travel document chunks from ChromaDB
-Generate answers using the Ollama llama3.2:1b model
-Run the frontend, backend, and language model with Docker Compose

2. Architecture Diagram
User
  |
  v
Streamlit Frontend (8501)
  |
  | HTTP requests
  v
FastAPI Backend (8000)
  |
  +------ SQLite / SQLAlchemy
  |       Users, Trips, Destinations
  |
  +------ ChromaDB
  |       Travel document chunks
  |
  +------ Ollama
          llama3.2:1b



Docker Compose
       Runs the frontend, backend, and Ollama. The backend handles authentication, trip management, document retrieval, and AI question answering.

3. Prerequisites

Install or have access to the following:
Docker Desktop — runs the application containers.
Docker Compose — starts and connects the application services.
Python 3.9 or newer — used for local development and testing.
Git — used to clone the project repository.
The application uses Ollama with the llama3.2:1b model. Docker Compose manages the Ollama service for the containerized application.
A configured .env file

4. Setup Instructions

Step 1: Clone the repository

git clone https://github.com/Fdrammeh/Capstone-Project

cd Capstone-Project/travelwise

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
Frontend: http://localhost:8501
FastAPI Documentation:http://localhost:8000/docs
API health check: http://localhost:8000/health

To stop the application:
docker compose down

5. Database Setup and Destinations

TravelWise stores users, trips, and destinations in SQLite using SQLAlchemy.

Destinations must exist in the database before users can select them when creating trips. Creating the database tables does not, by itself, guarantee that destination records have been added.

The project currently includes travel documents for Chicago, Milwaukee, and Minneapolis. Ensure that the corresponding destination records exist in the database before using those destinations in trips.Verify the available destinations in the frontend or by calling GET /destinations with a valid access token.

6. Usage Guide

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
-Submit the question, fior example "What are the top attractions in Chicago, and what public transportation options can visitors use?"
-The RAG system retrieves relevant information from its travel knowledge base and uses the language model to generate an answer.

Travel document ingestion

Travel documents are stored in the root docs/ directory. The knowledge base is populated or refreshed through the authenticated POST /ingest endpoint.
ngestion is triggered through /ingest; starting Docker Compose does not automatically re-indexes the documents.

To ingest or refresh the documents:

Open http://localhost:8000/docs.
-Register or log in through the authentication endpoints.
-Authorize the API documentation with a valid JWT access token.
-Find POST /ingest and execute the request.
-Check the response to confirm whether ingestion succeeded.


-The project includes the following travel documents in the docs/ directory:
chicago_overview.txt
chicago_attractions.txt
chicago_transportation.txt
chicago_food_and_activities.txt
milwaukee_overview.txt
milwaukee_attractions.txt
milwaukee_transportation.txt
milwaukee_food_and_activities.txt
minneapolis_overview.txt
minneapolis_attractions.txt
minneapolis_transportation.txt
minneapolis_food_and_activities.txt

During ingestion, the application reads the text files, divides their content into chunks, generates embeddings using Sentence Transformers, and stores the chunks in ChromaDB for semantic retrieval.

The backend also automatically seeds the SQLite database with default destinations for Chicago, Milwaukee, and Minneapolis if they are missing.

To start the application and trigger initialization, run this command from the project root:

docker compose up --build -d

6. API Endpoints

The following endpoints are defined in the FastAPI backend.

Method Endpoint	      Description                             Auth
POST   /auth/register	    register a new user                No
POST   /auth/token	    log in & obtain access token              No
GET	 /auth/me	    Retrieve current user info.               Yes
GET	 /destinations    Retrieve available destination            Yes
POST   /ask	           Ask a travel question using RAG system    Yes
GET	 /trips	    Retriev current user's trips              Yes
POST   /trips	           Create a trip                             Yes
PATCH  /trips/{trip_id}  Update an exixting trip	                  Yes
DELETE /trips/{trip_id} Delete a trip                              Yes
GET    /health          Check appliction health                    No
POST   /ingest          Ingest travel documents into chromadb      Yes
GET    /                 Welcome message                            No     

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

-test_auth.py — tests user registration, login, and protected routes.
-test_crud.py — tests database operations.
-test_rag.py — tests document retrieval, question answering, sources, and relevance guardrails.

Latest recorded test results: 9 tests passed, 0 failed, with 5 deprecation warnings. These warnings did not cause any tests to fail.

The test suite completed successfully in 40.67 seconds. Five deprecation warnings were reported; they did not cause any tests to fail.

 Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================= 9 passed, 5 warnings in 40.67s ==================================================================

The -v option displays each test and its result. Confirmed that at least five tests pass before submitting my capstone.

Project Structure:
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

10. troubleshooting
Docker services are not running
Check the service status:
       docker compose ps
View backend logs for errors:
       docker compose logs --tail=80 backend

If you changed backend code or dependencies, rebuild the backend:
       docker compose up -d --build backend

TravelWise cannot find relevant documents:

Confirm that the expected files exist in docs/, then trigger the authenticated POST /ingest endpoint through http://localhost:8000/docs. Check the endpoint response and backend logs.

The AI assistant is unavailable:
       Check the service status and backend logs:

docker compose ps
docker compose logs --tail=80 backend
docker compose logs --tail=80 ollama

Confirm that Ollama is running, that the configured model is available, and that the backend uses the correct Ollama service URL when running inside Docker.