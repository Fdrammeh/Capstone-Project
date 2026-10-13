"""
Capstone Backend — FastAPI Application  
===================================================
Run locally:
    uvicorn main:app --reload --port 8000
    
    
    *****python -m uvicorn backend.main:app --reload --port 8000***

This file is intentionally empty. Design your endpoints in the Architecture
Workshop before writing code here.

Required, at minimum:
    - 3+ endpoints (see course-content/Architecture Workshop Designing Your System.md)
    - Pydantic request/response models (put these in schemas.py and import them)
    - JWT-protected routes where appropriate (see auth.py)
    - A /health endpoint that checks your database and RAG dependencies

TODO: create the FastAPI app, add CORS middleware if your frontend needs it,
      and wire up your routes.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text 
import requests
from sqlalchemy.orm import Session
from backend.database import Base, engine, get_db
from backend import models, schemas
from datetime import date
from backend.models import User, Trip, Destination
from backend.auth import (
hash_password,
verify_password,
create_access_token,
get_current_user,
)
from backend.schemas import TokenResponse
from backend.rag import ask_travel_question, ingest_documents
from backend.schemas import QuestionRequest, AnswerResponse
# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="TravelWise AI",
    description="AI-powered travel planning assistant",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to TravelWise AI"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Check the database
    try:
        db.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception:
        database_status = "error"

    # Check ChromaDB
    try:
        from backend.rag import collection
        collection.count()
        chromadb_status = "ok"
    except Exception:
        chromadb_status = "error"

    # Check Ollama
    try:
        from backend.rag import OLLAMA_URL
        response = requests.get(
            f"{OLLAMA_URL.rstrip('/')}/api/tags",
            timeout=3
        )
        response.raise_for_status()
        ollama_status = "ok"
    except Exception:
        ollama_status = "error"

    overall_status = (
        "ok"
        if database_status == "ok"
        and chromadb_status == "ok"
        and ollama_status == "ok"
        else "degraded"
    )

    return {
        "status": overall_status,
        "database": database_status,
        "chromadb": chromadb_status,
        "ollama": ollama_status
    }

# handles the registration for the user.
@app.post("/auth/register", response_model=schemas.UserResponse)
def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # Check whether the username already exists
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Check whether the email already exists
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create the database user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

#This endpoint logs a user in and creates a JWT access token.

@app.post("/auth/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    #after the user submits their username and password, we check if the user exists and if the password is correct. If not, we raise an HTTPException with a 401 status code. If the credentials are valid, we create a JWT access token and return it to the user.
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

#The token contains the user's username as the subject (sub) and an expiration time.
    access_token = create_access_token(
        data={"sub": user.username}
    )

# Return the access token and its type
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
#the get /auth/me asks, who is currentlu logged in and Depends(get_current_user) checks if the token is valid and returns the user otherwise 401 unanthorised.
@app.get("/auth/me", response_model=schemas.UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user


#What this endpoint does
# Requires a valid JWT token through get_current_user.
# Checks that the destination exists.
# Rejects a trip if the end date is earlier than the start date.
# Connects the trip to the logged-in user and Chicago destination ID 1.
# Saves the trip to SQLite and returns its information.

@app.post("/trips", response_model=schemas.TripResponse)
def create_trip(
    trip_data: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that the destination exists
    destination = db.query(Destination).filter(
        Destination.id == trip_data.destination_id
    ).first()

    if destination is None:
        raise HTTPException(
            status_code=404,
            detail="Destination not found"
        )

    # Make sure the end date is not before the start date
    if trip_data.end_date < trip_data.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    # Create the trip for the logged-in user
    new_trip = Trip(
        user_id=current_user.id,
        destination_id=trip_data.destination_id,
        trip_name=trip_data.trip_name,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        notes=trip_data.notes
    )

    # Save the trip to the database
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return new_trip


@app.get("/destinations", response_model=list[schemas.DestinationResponse])
def get_destinations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return available travel destinations."""
    return db.query(Destination).order_by(Destination.name).all()

@app.get("/trips", response_model=list[schemas.TripResponse])
def get_my_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trips = db.query(Trip).filter(
        Trip.user_id == current_user.id
    ).all()
#Trip.user_id == current_user.id ensures users see only their own trips.
#.all() retrieves all matching trips.
    return trips

#This endpoint will let a logged-in user update a trip's name, dates, or notes without replacing every field.
@app.patch("/trips/{trip_id}", response_model=schemas.TripResponse)
def update_trip(
    trip_id: int,
    trip_data: schemas.TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == current_user.id
    ).first()

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    update_data = trip_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(trip, field, value)

    if trip.end_date < trip.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    if "destination_id" in update_data:
        destination = db.query(Destination).filter(
            Destination.id == trip.destination_id
        ).first()

        if destination is None:
            raise HTTPException(
                status_code=404,
                detail="Destination not found"
            )

    db.commit()
    db.refresh(trip)

    return trip


@app.delete("/trips/{trip_id}", response_model=schemas.MessageResponse)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == current_user.id
    ).first()

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    db.delete(trip)
    db.commit()

    return {"message": "Trip deleted successfully"}

@app.post("/ask", response_model=AnswerResponse) 
def ask_question( 
    question_data: QuestionRequest, 
    current_user: User = Depends(get_current_user) ): 
    
    result = ask_travel_question(question_data.question) 
    return result


@app.post("/ingest")
def ingest_travel_documents(
    current_user: User = Depends(get_current_user),
):
    """Ingest travel documents into the ChromaDB knowledge base."""

    try:
        chunks_added = ingest_documents()

        if chunks_added == 0:
            raise HTTPException(
                status_code=404,
                detail="No text documents found in the docs folder.",
            )

        return {
            "message": "Travel documents ingested successfully.",
            "chunks_added": chunks_added,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(exc)}",
        )
