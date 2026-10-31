import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from services.db.database import Base, get_db
from services.db.models import User, Profile, Job
from services.api.main import app

# Shared in-memory test database using StaticPool
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_models_service_status():
    res = client.get("/api/v1/matching/models/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["heuristic_engine"]["status"] == "active"
    assert "providers" in data
    assert data["providers"]["heuristic"]["available"] is True


def test_jobs_and_matching_flow():
    # 1. Scrape to seed jobs
    scrape_res = client.post("/api/v1/scrapers/run", json={"query": "Flutter", "limit_per_plugin": 5})
    assert scrape_res.status_code == 200
    assert scrape_res.json()["offers_persisted"] > 0

    # 2. Search jobs with live mode
    jobs_res = client.get("/api/v1/jobs?q=Flutter&live=false")
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()
    assert len(jobs) > 0
    job_id = jobs[0]["id"]

    # 3. Create User & Profile
    db = TestingSessionLocal()
    user = User(email="flutter_dev@tech.es", hashed_password="pw", full_name="Elena Martín")
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(
        user_id=user.id,
        title="Senior Flutter Specialist",
        skills=[{"name": "Flutter"}, {"name": "Dart"}, {"name": "Clean Architecture"}],
        target_salary_min=45000.0,
        preferred_modality="REMOTE",
        locations=["Madrid", "Valencia"],
        experience_years=5.0
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # 4. Calculate Match
    match_res = client.post("/api/v1/matching/calculate", json={
        "profile_id": profile.id,
        "job_id": job_id,
        "use_llm": False
    })
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["scores"]["total_score"] > 50.0

    # 5. Create CRM Application & Kanban
    crm_res = client.post("/api/v1/crm/applications", json={
        "user_id": user.id,
        "profile_id": profile.id,
        "job_id": job_id,
        "status": "APPLIED",
        "stage_notes": "Enviado CV adaptado"
    })
    assert crm_res.status_code == 201
    app_id = crm_res.json()["id"]

    # 6. Check Kanban board
    kanban_res = client.get(f"/api/v1/crm/kanban?user_id={user.id}")
    assert kanban_res.status_code == 200
    kanban = kanban_res.json()
    assert len(kanban["columns"]["APPLIED"]) == 1

    # 7. Transition status to INTERVIEW
    patch_res = client.patch(f"/api/v1/crm/applications/{app_id}/status", json={
        "status": "INTERVIEW",
        "note": "Primera ronda con el hiring manager"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "INTERVIEW"
    assert len(patch_res.json()["timeline_events"]) == 2

    # 8. Remove job from Kanban (DELETE application)
    del_app_res = client.delete(f"/api/v1/crm/applications/{app_id}")
    assert del_app_res.status_code == 204
    # Verify removed from Kanban
    kanban_after = client.get(f"/api/v1/crm/kanban?user_id={user.id}").json()
    assert len(kanban_after["columns"]["INTERVIEW"]) == 0

    # 9. Remove Profile (DELETE profile)
    del_prof_res = client.delete(f"/api/v1/profiles/{profile.id}")
    assert del_prof_res.status_code == 204
    # Verify profile deleted
    prof_list = client.get(f"/api/v1/profiles?user_id={user.id}").json()
    assert len(prof_list) == 0
