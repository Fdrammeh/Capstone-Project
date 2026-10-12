"""
Capstone Backend — Pydantic Schemas  
=================================================
Define request/response models here and import them into main.py.
Every endpoint should validate its input and declare a response_model.

TODO: define schemas for each entity in models.py, plus auth schemas
      (e.g. UserCreate, UserOut, Token).
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# -------------------------
# User schemas
# -------------------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


# -------------------------
# Authentication schemas
# -------------------------

class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# -------------------------
# Destination schemas
# -------------------------

class DestinationResponse(BaseModel):
    id: int
    name: str
    city: str
    country: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------
# Trip schemas
# -------------------------

class TripCreate(BaseModel):
    trip_name: str = Field(min_length=1)
    destination_id: int
    start_date: date
    end_date: date
    notes: Optional[str] = None

    @field_validator("trip_name")
    @classmethod
    def validate_trip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Trip name cannot be empty.")
        return value


class TripUpdate(BaseModel):
    trip_name: Optional[str] = None
    destination_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("trip_name")
    @classmethod
    def validate_trip_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Trip name cannot be empty.")
        return value


class TripResponse(BaseModel):
    id: int
    trip_name: str
    destination_id: int
    start_date: date
    end_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------
# RAG schemas
# -------------------------

class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


# -------------------------
# Health check schema
# -------------------------

class HealthResponse(BaseModel):
    status: str
    database: str
    chromadb: str
    ollama: str


# -------------------------
# General response schema
# -------------------------

class MessageResponse(BaseModel):
    message: str