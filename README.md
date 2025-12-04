# HustleHub

This guide provides the steps to set up and run the HustleHub application, which uses an Angular frontend and a FastAPI + SQL Alchemy backend with a PostgreSQL database.

## Prerequisites

- PostgreSQL installed
- Python 3 installed
- Node.js & npm installed

## Setup Instructions

### 1. Backend (FastAPI + SQL Alchemy)

Navigate to the backend directory and create a virtual environment:

```bash
cd backend/
python3 -m venv venv
```

Activate the virtual environment:

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
.\venv\Scripts\activate
```

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```bash
cd backend
touch .env
```

Add the following configuration to `backend/.env`:

```bash
# Security (required)
SECRET_KEY=your-secret-key-here-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Note:** The SECRET_KEY is required for the application to run. Use any random string (minimum 32 characters) for development.

### 3. Database Setup

**Update the database connection in `backend/database.py`:**

The database connection string is hardcoded in `database.py`. Update it based on your operating system:

**For macOS/Linux:**
```python
URL_DATABASE = 'postgresql://admin:admin@localhost:5432/hustlehub'
```

**For Windows:**
```python
URL_DATABASE = 'postgresql://postgres:yourpassword@localhost:5432/hustlehub'
```

**Start the server to create the database:**

```bash
cd backend
uvicorn main:app --reload
```

The server will create all necessary tables automatically.

### 4. Seed Database (Optional)

To populate the database with sample data, run the seed script:

```bash
python seed_dummy_users.py
```

### 5. Frontend (Angular)

Install the Angular CLI globally:

```bash
npm install -g @angular/cli
```

Navigate to the frontend directory and install dependencies:

```bash
cd frontend/hustle-hub-app/
npm install
```

## Running the Application

You'll need two separate terminal windows to run the backend and frontend servers simultaneously.

**Terminal 1: Start the Backend**

Make sure the virtual environment is activated (you should see `venv` in your command prompt).

```bash
cd backend/
uvicorn main:app --reload
```

Backend will run at: http://localhost:8000

**Terminal 2: Start the Frontend**

```bash
cd frontend/hustle-hub-app/
ng serve --open
```

Frontend will run at: http://localhost:4200

## Database Management

### Reset Database

If you need to drop and recreate the database:

```bash
psql postgres
\c hustlehub
DROP TABLE users CASCADE;
\q
```

Then restart the server to recreate tables automatically.

## Testing

### Backend Testing

The backend has three types of tests:

**Unit Tests**
```bash
cd backend/
pytest -m unit
```

**Integration Tests**
```bash
cd backend/
pytest -m integration
```

**E2E Tests (Backend)**
```bash
cd backend/
pytest -m e2e
```

**Run All Backend Tests**
```bash
cd backend/
pytest
```

**Run with Coverage**
```bash
cd backend/
pytest --cov
```

### Frontend Testing

Run Angular unit tests:

```bash
cd frontend/hustle-hub-app/
ng test
```

Run tests once (no watch mode):

```bash
cd frontend/hustle-hub-app/
ng test --watch=false
```

### E2E Testing (Playwright)

The `e2e/` folder contains browser-based UI tests using Playwright. These tests verify basic page loading and form interactions.

**Prerequisites:**
- Frontend must be running on http://localhost:4200

**Setup E2E Tests:**
```bash
cd e2e/
npm install
npx playwright install
```

**Run E2E Tests:**
```bash
cd e2e/
npm test
```

**Run with UI (interactive mode):**
```bash
cd e2e/
npm run test:ui
```

## Expected Outcome

When both servers are running, you should see:
- Backend API documentation at: http://localhost:8000/docs
- Frontend application at: http://localhost:4200
- Message from backend: "Welcome to the HustleHub API"