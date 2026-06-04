from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.app.api.main import api_router

app = FastAPI(title="AI Video Scene Search Engine")

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

app.include_router(api_router)

@app.get("/")
async def render_homepage(request: Request):
    return templates.TemplateResponse(request, "index.html")