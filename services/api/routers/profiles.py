from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.db.database import get_db
from services.db.models import Profile, User
from services.api.schemas import ProfileCreate, ProfileResponse

router = APIRouter(prefix="/profiles", tags=["Multi-Profile"])


@router.get("", response_model=List[ProfileResponse])
def list_profiles(user_id: str, db: Session = Depends(get_db)):
    return db.query(Profile).filter(Profile.user_id == user_id).all()


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    profile = Profile(
        user_id=payload.user_id,
        title=payload.title,
        bio=payload.bio,
        target_roles=payload.target_roles,
        target_salary_min=payload.target_salary_min,
        target_salary_max=payload.target_salary_max,
        currency=payload.currency,
        preferred_modality=payload.preferred_modality,
        locations=payload.locations,
        skills=payload.skills,
        experience_years=payload.experience_years,
        portfolio_urls=payload.portfolio_urls
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile
