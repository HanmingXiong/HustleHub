# HustleHub

This guide provides the steps to set up and run the HustleHub application, which uses an Angular frontend and a FastAPI + SQL Alchemy backend with a PostgreSQL database.

## Prerequisites

- PostgreSQL installed

- Python 3 installed

- Node.js & npm installed

## Setup Instructions

### 1. Database (PostgreSQL)
Log into PostgreSQL:

```Bash
psql -U [your_username] -d postgres
```

Create an admin role with the username postgres if you don't already have one. This role will be used by the application to create the database.

```SQL
CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'yourpassword';
```
Exit psql by typing \q.

Run the database creation script to set up the application's database and tables.

```Bash
psql -U postgres -f db/create_db.sql
```

### 2. Backend (FastAPI + SQL Alchemy)
Navigate to the backend directory and create a virtual environment.

```Bash
python3 -m venv venv
```

Activate the virtual environment:

macOS / Linux:

```Bash
source venv/bin/activate
```

Windows:

```Bash
.\venv\Scripts\activate
```

Install the required Python packages:

```Bash
pip install fastapi sqlalchemy uvicorn psycopg2-binary
```

### 3. Frontend (Angular)
Install the Angular CLI globally using npm. This allows you to use the ng command anywhere.

```Bash
npm install -g @angular/cli
```

## Running the Application
You'll need two separate terminal windows to run the backend and frontend servers simultaneously.

Terminal 1: Start the Backend

Make sure the virtual environment is set (should see venv or whatever your virtual env name is in front of command prompt line).

Start the FastAPI server with auto-reloading.

```Bash
uvicorn main:app --reload
```

Terminal 2: Start the Frontend

Make sure you are in the hustble-hub-app directory

```Bash
cd frontend/hustle-hub-app
```
Serve the Angular application. The --open or -o flag will automatically open it in your default browser.

```Bash
ng serve --open
```

## Expected Outcome
You should see this if the ourcome is correct:

Angular + FastAPI Connection 
Message from backend: Welcome to the HustleHub API