import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from services.db.database import init_db
from services.api.routers import jobs, matching, crm, profiles, scrapers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    init_db()
    yield


app = FastAPI(
    title="JobHunter AI - Core Backend API",
    version="1.0.0",
    description="Motor de matching con IA, CRM ATS Personal y Agregador Multifuente Nacional y Autonómico (España)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")
app.include_router(crm.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(scrapers.router, prefix="/api/v1")

# Mount Static Files Dashboard
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "jobhunter-backend-core",
        "version": "1.0.0"
    }
