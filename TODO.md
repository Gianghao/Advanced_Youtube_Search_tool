# Team Collaboration Guide & TODO List 📋

This document serves as a guide for development workflow, backend architecture, and tracking remaining project tasks.

---

## 🌿 Git Branching & Workflow

To maintain a clean repository, follow these guidelines when developing new features:

### 1. Creating a New Branch
Always create a new branch from `main` (or the development branch) using the following naming convention:
`feature_<feature_name>`

For example, to work on User CRUD:
```bash
git checkout main
git pull
git checkout -b feature_crud_for_User
```

### 2. Committing Changes
After done the coding part, add files to git and write meaningful, concise commit messages:
```bash
git add .
git commit -m "feat: implement user creation and update endpoints"
```

### 3. Running Unit Tests
Before pushing your changes, always run the unit tests to ensure you haven't introduced any regressions:
```bash
# Run all tests
uv run pytest

# Run specific tests (e.g. video tests)
uv run pytest tests/test_video.py
```
Make sure all tests pass (`PASSED` status) before proceeding to push.

### 4. Pushing Changes
Push your branch to the remote repository:
```bash
git push -u origin feature_crud_for_User
```
Once pushed, open a **Pull Request (PR)** on GitHub for review.

---

## 🏗️ Backend Architecture & Data Flow

Our backend is built with **FastAPI** and **Supabase** (Postgres DB + Storage). To implement new APIs, you will typically touch the following layers in this sequence:

### Key Folders to Focus On:
1. `backend/app/schemas/`: Define **Pydantic models** for validation. This is where request bodies (`UserCreate`, `VideoUpload`) and response models (`UserResponse`, `VideoResponse`) are defined.
2. `backend/app/services/`: Write the core **Business Logic**. This layer interacts with Supabase DB (using queries) and Storage. (e.g., `AuthService`, `UploadService`).
3. `backend/app/api/routes/`: Define the **FastAPI endpoints (Routers)**. The router validates input schemas, calls the corresponding service layer, and returns the response.
4. `backend/app/api/main.py`: Include any new route files in this main router aggregator.

### Data Flow Path:
```text
[Streamlit Frontend] 
       │ (HTTP Request / JSON / Multipart Form)
       ▼
[FastAPI Router] (backend/app/api/routes/*)
       │ (Validates input with Pydantic Schemas in backend/app/schemas/*)
       ▼
[Service Layer] (backend/app/services/*)
       │ (Runs business logic & queries Supabase)
       ▼
[Supabase Client] ───► [Supabase DB / Storage]
```

---

## 🔑 Test Credentials
For local development and testing of authentication/frontend features, you can use:
- **Email:** `user123@gmail.com`
- **Password:** `123456`

---

## 📝 TODO List

Below is the roadmap of tasks for the team. Check them off as they are completed:

### 🎨 Frontend & Design
- [x] **Streamlit Frontend**:
  - Connect all pages to the backend REST API endpoints.
  - Implement dynamic pages for user authentication (Login/Register).
  - Build UI for uploading video files and querying advanced AI search.

### 📐 Diagrams & System Architecture
- [ ] **Use Case Diagram**: Map out all actors (User, Admin, AI Engine) and their interactions.
- [ ] **Logical View**: Model the logical packages, layers, and class relationships.
- [x] **Process View** *(Completed)*: Already drawn and documented inside the `docs` folder.
- [ ] **Physical / Development View**: Document the physical deployment environment, servers, and build toolchains.
- [ ] **Relational Schema**: Design and document the PostgreSQL relational schema, including table structures, constraints, and relationships.

### 🔌 API Design
- [ ] **API Design Specifications**:
  - Document all endpoints, HTTP methods, payload structures, headers, and status codes.
  - Test and verify endpoints using FastAPI's automatic docs (`/docs`).

### 👥 User Management (CRUD for User)
- [ ] **CRUD for User**:
  - Define user profile table schemas in Supabase.
  - Implement endpoints/services to Retrieve, Update, and Delete user accounts and profiles.

### 🎥 Video Management (CRUD for Video)
- [ ] **CRUD for Video**:
  - Extend the existing upload functionality to support full video management.
  - Implement endpoints/services to delete videos (deleting both DB records and files in Supabase Storage), edit video metadata (title, status), and fetch specific video details.

### 🤖 AI Engine & Advanced Search
- [ ] **AI for Advanced Search**:
  - Integrate AI pipelines (e.g., video segmenting, visual/text embedding models) to extract metadata from videos.
  - Implement semantic video scene search endpoints where users can find exact timestamps based on natural language queries.
