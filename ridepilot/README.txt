
Create a account in credit in https://platform.openai.com/home and create API Key,
that need to pe pest in .env file  and add credit in openai

For Free LLM use ollama
curl -fsSL https://ollama.com/install.sh | sh
    Use: ollama pull gpt-oss:20b
    ollama run gpt-oss:20b
    Make sure ollama is running by checking the URL: http://localhost:11434/v1

uvicorn app.main:app --reload
uvicorn app.main:app --host 192.168.29.7 --port 8000 --reload

Create DB:
CREATE USER ridepilot_user
WITH PASSWORD 'replace_with_a_secure_password';

CREATE DATABASE ridepilot
OWNER ridepilot_user;

psql -U ridepilot_user -d ridepilot password replace_with_a_secure_password

// Running the command alembic init migrations initializes
// a new Alembic database migration environment inside a dedicated directory named migrations.
    alembic init migrations

4. Create and inspect the first migration
    alembic revision --autogenerate -m "add users and auth sessions"
    alembic upgrade head
    alembic current


4. Database relationships we should implement
User
 ├── AuthSession
 ├── ChatSession
 │    └── ChatMessage
 ├── RideSearch
 │    └── RiderQuote
 └── Booking
       └── references the selected quote

Guest identity
 └── Temporary session and associated history
      └── deleted at sign-out





