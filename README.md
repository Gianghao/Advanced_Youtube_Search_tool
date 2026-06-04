# Advanced YouTube Search Tool 🚀

An AI-powered Video Scene Search Engine designed to search for specific scenes inside YouTube videos.

## 📂 Project Structure

```text
.
├── backend/                  # Server-side codebase (FastAPI)
│   ├── app/
│   │   ├── api/              # API routing logic
│   │   │   ├── routes/       # Specific router modules
│   │   │   │   ├── auth_router.py   # Auth routes (SignUp/SignIn)
│   │   │   │   ├── search_router.py # Search routes
│   │   │   │   └── video_router.py  # Video routes (Upload/View)
│   │   │   └── main.py       # API main router aggregator
│   │   ├── core/
│   │   │   └── config.py     # Environment variables and configuration
│   │   ├── database/
│   │   │   └── db.py         # DB connection setup
│   │   ├── schemas/          # Pydantic data schemas (User, Video, etc.)
│   │   └── services/         # Business logic services (Auth, Upload, etc.)
│   ├── static/               # Static assets (CSS, JS, images)
│   ├── templates/            # Jinja2 template files
│   ├── main.py               # FastAPI application entry point
│   ├── .env.example          # Environment variable template
│   └── .env                  # Configuration keys (Ignored by Git)
├── frontend/                 # User interface files
│   └── app.py                # Main Streamlit web application
├── tests/                    # Test suite (Pytest)
│   ├── test_auth.py          # Authentication tests
│   └── test_video.py         # Video upload and viewing tests
├── pyproject.toml            # Project configurations (dependencies, pytest, etc.)
├── requirements.txt          # Python dependencies list
└── setup.sh                  # Shell script for automated environment setup
```

## 🛠️ Installation & Setup

This project uses a Python virtual environment and dependencies listed in `requirements.txt`.

### Option 1: Automated Script (Recommended)
Suitable for Linux / macOS, or Git Bash on Windows:

1. Open your terminal at the root directory of the project.
2. Grant execution permissions and run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Once completed, a `.env` file will be generated at `backend/.env`. Open this file and fill in your actual **Supabase URL**, **Supabase Key**, and **Supabase Video Bucket**:
   ```env
   SUPABASE_URL='https://your-supabase-project.supabase.co'
   SUPABASE_KEY='your-anon-key'
   SUPABASE_VIDEO_BUCKET='video-bucket'
   ```
   *(Note: Ensure Row-Level Security (RLS) is configured correctly or disabled for the `videos` table in Supabase, and make sure your storage bucket `video-bucket` is set to **Public**).*
4. Run the project (see running instructions below).

### Option 2: Manual Installation using `uv` (or `pip`)
1. Create a virtual environment:
   ```bash
   uv venv
   # Activate environment (Linux/macOS):
   source .venv/bin/activate
   # Activate environment (Windows):
   # .venv\Scripts\activate
   ```
2. Install the required dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
3. Copy the configuration template:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Remember to configure `backend/.env` with your actual Supabase credentials.*

---

## 🚀 Running the Application

To interact with the app, you need to start both the FastAPI backend and the Streamlit frontend.

### 1. Run the Backend
From the root directory:
```bash
uv run uvicorn backend.main:app --reload
```
The API server will run at `http://localhost:8000`.

### 2. Run the Frontend
In a new terminal window (ensure the virtual environment is activated):
```bash
streamlit run frontend/app.py
```
The Streamlit app will launch and open in your default browser at `http://localhost:8501`.

---

## 🔑 Test Credentials
For testing and login functionality, you can use the following default credentials:
- **Email:** `user123@gmail.com`
- **Password:** `123456`

---

## 🧪 Running Unit Tests
Unit tests use `pytest` with mocked Supabase clients (no active Supabase connection is required to run tests):

Run the entire test suite:
```bash
uv run pytest
```

Run specific tests (e.g., authentication or video functionality):
```bash
uv run pytest tests/test_auth.py
uv run pytest tests/test_video.py
```
