from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from services.db.database import get_db
from services.db.models import Profile, Job, JobMatch
from services.api.schemas import (
    MatchRequestSingle,
    MatchRequestBatch,
    MatchResponse,
    MatchScoreBreakdown
)
from services.ai_engine_service.matching_engine import MultivariableMatchingEngine
from services.ai_engine_service.openai_provider import OpenAIProvider
from services.ai_engine_service.ollama_provider import OllamaProvider

router = APIRouter(prefix="/matching", tags=["AI Matching Engine"])


def _get_provider(provider_name: Optional[str]):
    p = (provider_name or "").lower()
    if p == "openai":
        return OpenAIProvider()
    elif p == "ollama":
        return OllamaProvider()
    return None


@router.get("/models/status")
async def get_models_status():
    """
    Comprueba el estado de salud de los motores y proveedores de IA disponibles.
    """
    ollama = OllamaProvider()
    openai = OpenAIProvider()
    ollama_ok = await ollama.health_check()
    openai_ok = await openai.health_check()
    return {
        "status": "healthy",
        "service": "ai_matching_models",
        "heuristic_engine": {
            "status": "active",
            "weights": {
                "skills": 0.40,
                "salary": 0.25,
                "location_modality": 0.20,
                "experience": 0.15
            }
        },
        "providers": {
            "heuristic": {
                "available": True,
                "description": "Motor de reglas semánticas y análisis multidimensional local"
            },
            "ollama": {
                "available": ollama_ok,
                "endpoint": ollama.base_url,
                "model": ollama.model
            },
            "openai": {
                "available": openai_ok,
                "configured": bool(openai.api_key),
                "model": openai.model
            }
        }
    }


@router.post("/calculate", response_model=MatchResponse)
async def calculate_match(payload: MatchRequestSingle, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    provider = _get_provider(payload.provider)
    engine = MultivariableMatchingEngine(provider=provider)

    profile_dict = {
        "title": profile.title,
        "skills": profile.skills,
        "target_salary_min": profile.target_salary_min,
        "target_salary_max": profile.target_salary_max,
        "preferred_modality": profile.preferred_modality,
        "locations": profile.locations,
        "experience_years": profile.experience_years
    }

    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "required_skills": job.required_skills,
        "nice_to_have_skills": job.nice_to_have_skills,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "modality": job.modality,
        "location": job.location,
        "experience_required_years": job.experience_required_years
    }

    res = await engine.compute_match(profile_dict, job_dict, use_llm=payload.use_llm)

    # Persist or update JobMatch in database
    db_match = db.query(JobMatch).filter(
        JobMatch.profile_id == profile.id,
        JobMatch.job_id == job.id
    ).first()

    explanation_payload = {
        "summary": res.explanation.summary,
        "strengths": res.explanation.strengths,
        "gaps": res.explanation.gaps,
        "recommendation": res.explanation.recommendation,
        "llm_insights": res.explanation.llm_insights
    }

    if db_match:
        db_match.total_score = res.total_score
        db_match.skill_score = res.skill_score
        db_match.salary_score = res.salary_score
        db_match.location_score = res.location_score
        db_match.experience_score = res.experience_score
        db_match.explanation = explanation_payload
    else:
        db_match = JobMatch(
            profile_id=profile.id,
            job_id=job.id,
            total_score=res.total_score,
            skill_score=res.skill_score,
            salary_score=res.salary_score,
            location_score=res.location_score,
            experience_score=res.experience_score,
            explanation=explanation_payload
        )
        db.add(db_match)

    db.commit()

    return MatchResponse(
        profile_id=profile.id,
        job_id=job.id,
        job_title=job.title,
        company=job.company,
        scores=MatchScoreBreakdown(
            total_score=res.total_score,
            skill_score=res.skill_score,
            salary_score=res.salary_score,
            location_score=res.location_score,
            experience_score=res.experience_score,
            matched_skills=res.skill_analysis.matched_skills,
            missing_skills=res.skill_analysis.missing_required_skills,
            explanation=explanation_payload
        )
    )


@router.post("/batch", response_model=List[MatchResponse])
async def batch_match(payload: MatchRequestBatch, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    jobs = db.query(Job).filter(Job.is_active == True).limit(50).all()
    provider = _get_provider(payload.provider)
    engine = MultivariableMatchingEngine(provider=provider)

    profile_dict = {
        "title": profile.title,
        "skills": profile.skills,
        "target_salary_min": profile.target_salary_min,
        "target_salary_max": profile.target_salary_max,
        "preferred_modality": profile.preferred_modality,
        "locations": profile.locations,
        "experience_years": profile.experience_years
    }

    results = []
    for job in jobs:
        job_dict = {
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "required_skills": job.required_skills,
            "nice_to_have_skills": job.nice_to_have_skills,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "modality": job.modality,
            "location": job.location,
            "experience_required_years": job.experience_required_years
        }
        res = await engine.compute_match(profile_dict, job_dict, use_llm=False)
        if res.total_score >= payload.min_score:
            results.append(
                MatchResponse(
                    profile_id=profile.id,
                    job_id=job.id,
                    job_title=job.title,
                    company=job.company,
                    scores=MatchScoreBreakdown(
                        total_score=res.total_score,
                        skill_score=res.skill_score,
                        salary_score=res.salary_score,
                        location_score=res.location_score,
                        experience_score=res.experience_score,
                        matched_skills=res.skill_analysis.matched_skills,
                        missing_skills=res.skill_analysis.missing_required_skills,
                        explanation={
                            "summary": res.explanation.summary,
                            "strengths": res.explanation.strengths,
                            "gaps": res.explanation.gaps,
                            "recommendation": res.explanation.recommendation
                        }
                    )
                )
            )

    results.sort(key=lambda x: x.scores.total_score, reverse=True)
    return results[:payload.limit]
