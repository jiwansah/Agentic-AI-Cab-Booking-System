# RidePilot Backend Setup Guide

This directory contains the core Python backend, database configurations, and LLM orchestration layers for RidePilot.

---

## 🛠️ Prerequisites & Environment Setup

### 1. LLM Provider Configuration
RidePilot supports both cloud-based and local LLM engines. Choose one of the options below:

#### Option A: OpenAI (Cloud)
1. Create an account and add credits at the [OpenAI Platform](https://platform.openai.com/home).
2. Generate a new API Key and save it securely. You will paste this into your `.env` file.

#### Option B: Ollama (Local & Free)
1. Install Ollama by running the following command:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. Pull and run the required model:
   ```bash
   ollama pull gpt-oss:20b
   ollama run gpt-oss:20b
   ```
3. Verify that your local instance is active by visiting: `http://localhost:11434/v1`

---

### 2. Database Initialization
Log into your PostgreSQL instance and execute the following SQL commands to create the database and user:

```sql
-- Create a dedicated user
CREATE USER ridepilot_user WITH PASSWORD 'replace_with_a_secure_password';

-- Create the database and assign ownership
CREATE DATABASE ridepilot OWNER ridepilot_user;
```

To test your connection locally:
```bash
psql -U ridepilot_user -d ridepilot
```

---

### 3. Database Migrations (Alembic)
Initialize the database version tracking and apply the schema:

1. **Initialize Environment:** Sets up a dedicated migration directory.
   ```bash
   alembic init migrations
   ```
2. **Generate First Migration:** Detects schema changes automatically.
   ```bash
   alembic revision --autogenerate -m "add users and auth sessions"
   ```
3. **Apply Changes:** Upgrades the database to the latest schema head.
   ```bash
   alembic upgrade head
   ```
4. **Verify Status:** Confirms current migration version.
   ```bash
   alembic current
   ```

---

## 📄 Environment Configuration (`.env`)

Create a `.env` file in the root backend directory (`ridepilot/`) and populate it with your credentials:

```ini
# Active LLM provider selection (choices: ollama, openai)
LLM_PROVIDER=ollama

# Ollama Local Configuration
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=gpt-oss:20b

# OpenAI Cloud Configuration (Required only if LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-proj-W...
OPENAI_MODEL=gpt-5-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# Database Connection String
DATABASE_URL=postgresql+psycopg://ridepilot_user:replace_with_a_secure_password@localhost:5432/ridepilot

# Ride Provider Toggles
MOCK_PROVIDER_ENABLED=true

UBER_ENABLED=false
UBER_ACCESS_TOKEN=

OLA_ENABLED=false
OLA_ACCESS_TOKEN=
OLA_APP_TOKEN=
```

---

## 🚀 Running the Application

Start the local development server using Uvicorn:

*   **Local Host Only:**
    ```bash
    uvicorn app.main:app --reload
    ```
*   **Network Accessible (LAN):**
    ```bash
    uvicorn app.main:app --host 192.168.29.7 --port 8000 --reload
    ```

---

## 📐 Database Schema & Architecture

The application implements the following entity relationships:

*   **User Identity:**
    ├── **AuthSession** *(Tracks user authentication sessions)*
    ├── **ChatSession**
    │    └── **ChatMessage** *(Maintains context logs)*
    ├── **RideSearch**
    │    └── **RiderQuote** *(Aggregated pricing quotes)*
    └── **Booking** *(References the specific selected quote)*

*   **Guest Identity:**
    └── **Temporary Session** *(Tracks unauthenticated actions; automatically wiped upon sign-out)*
