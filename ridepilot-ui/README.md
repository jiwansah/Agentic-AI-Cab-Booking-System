# RidePilot UI — Phase 2

npm run dev


This version matches the supplied FastAPI authentication contracts.


## Run

```bash
npm install
cp .env.example .env.local
npm run dev
```
Add the below line in .env.local 
NEXT_PUBLIC_API_BASE_URL=http://192.168.29.7:8000

Open `http://localhost:3000`.

## Auth response

The supplied responses are supported, including:

Registered:
- user_id
- session_id
- access_token
- token_type
- expires_at
- account_type

Guest:
- user_id
- session_id
- access_token
- device_credential
- recovery_code

The auth response is kept in `sessionStorage` for this development phase.

For production, use an HttpOnly secure cookie/BFF pattern rather than exposing bearer credentials to browser JavaScript.

## CORS

Your FastAPI backend must allow the frontend origin during development, e.g.:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## APIs

### Login

```http
POST http://127.0.0.1:8000/auth/login
Content-Type: application/json
```

```json
{
  "identifier": "strings",
  "password": "stringst"
}
```

### Guest

```http
POST http://127.0.0.1:8000/auth/guest
```

No body.

### Registration

```http
POST http://127.0.0.1:8000/auth/register
Content-Type: application/json
```

```json
{
  "phone": "strings_2",
  "email": "user_2@example.com",
  "password": "stringst"
}
```


## Next

After authentication, connect the successful session to the RidePilot Agent screen and `/chat`, then quote selection and booking.
