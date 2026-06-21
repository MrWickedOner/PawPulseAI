# PawPulse Backend

FastAPI-based backend for PawPulse pet health monitoring platform.

## Features

- **User Authentication**: JWT-based auth with signup and login.
- **Pet Management**: Manage pets, breeds, and profiles.
- **Device Ingestion**: Normalization and ingestion of health data from FitBark, Whistle, and Tractive.
- **Health Data API**: Access activity, sleep, vitals, and gait data.
- **Anomaly Detection**: Integrated AI engine for baseline learning and behavioral anomaly detection.
- **Subscription Management**: Tiered billing (Basic, Premium, Pro) with Stripe integration.
- **Mobile Support**: In-App Purchase (IAP) verification and Push Notification token registration.
- **Practice Management**: Dashboard for veterinarians to monitor multiple pet patients.

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite (via Turso/team-db)
- **Authentication**: JWT, Passlib (bcrypt)
- **Validation**: Pydantic v2
- **Testing**: Pytest, Integration test scripts

## Setup

1. Clone the repository.
2. Navigate to `backend/`.
3. Create a virtual environment: `python -m venv venv`.
4. Install dependencies: `pip install -r requirements.txt`.
5. Copy `.env.example` to `.env` and configure your secrets.
6. Run the server: `uvicorn app.main:app --reload`.

## Project Structure

- `app/api/`: API routers and endpoints.
- `app/core/`: Security, config, and utility functions.
- `app/db/`: Database connection and schema management.
- `app/models/`: Pydantic schemas.
- `app/services/`: Business logic, data ingestion, and AI engine integration.
- `pawpulse_ml/`: The anomaly detection engine logic.
- `seed_demo_data.py`: Script to generate synthetic pet data for testing.
