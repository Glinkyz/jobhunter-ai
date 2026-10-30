import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from services.db.database import get_db
from services.db.models import Job
from services.api.schemas import JobCreate, JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobResponse])
def search_jobs(
    q: Optional[str] = Query(None, description="Búsqueda por título o palabras clave"),
    location: Optional[str] = Query(None, description="Filtro de localización o provincia"),
    modality: Optional[str] = Query(None, description="REMOTE, HYBRID, ONSITE"),
    min_salary: Optional[float] = Query(None, description="Salario mínimo anual deseado"),
    source: Optional[str] = Query(None, description="Portal de origen (InfoJobs, SEPE, etc.)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Job).filter(Job.is_active == True)

    if q:
        term = f"%{q}%"
        query = query.filter((Job.title.ilike(term)) | (Job.description.ilike(term)))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if modality:
        query = query.filter(Job.modality == modality.upper())
    if min_salary:
        query = query.filter((Job.salary_max >= min_salary) | (Job.salary_min >= min_salary))
    if source:
        query = query.filter(Job.source.ilike(f"%{source}%"))

    jobs = query.order_by(Job.published_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta de empleo no encontrada")
    return job


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    raw_signature = f"{job_in.title.lower().strip()}|{job_in.company.lower().strip()}|{job_in.location.lower().strip()}"
    content_hash = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

    existing = db.query(Job).filter(Job.content_hash == content_hash).first()
    if existing:
        return existing

    job = Job(
        title=job_in.title,
        company=job_in.company,
        location=job_in.location,
        modality=job_in.modality,
        contract_type=job_in.contract_type,
        salary_min=job_in.salary_min,
        salary_max=job_in.salary_max,
        currency=job_in.currency,
        experience_required_years=job_in.experience_required_years,
        required_skills=job_in.required_skills,
        nice_to_have_skills=job_in.nice_to_have_skills,
        description=job_in.description,
        source=job_in.source,
        source_url=job_in.source_url,
        external_id=job_in.external_id,
        content_hash=content_hash
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
