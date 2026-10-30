from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.db.database import get_db
from services.db.models import Job
from services.scraper_service.manager import ScraperManager
from services.scraper_service.plugins.infojobs_plugin import InfoJobsPlugin
from services.scraper_service.plugins.sepe_plugin import SEPEPlugin
from services.scraper_service.plugins.madrid_plugin import MadridEmpleoPlugin
from services.api.schemas import (
    ScraperPluginResponse,
    ScraperTriggerRequest,
    ScraperTriggerResponse
)

router = APIRouter(prefix="/scrapers", tags=["Scrapers & Conectores"])

# Global scraper manager singleton with Spain connectors
scraper_mgr = ScraperManager()
scraper_mgr.register_plugin(InfoJobsPlugin())
scraper_mgr.register_plugin(SEPEPlugin())
scraper_mgr.register_plugin(MadridEmpleoPlugin())


@router.get("/plugins", response_model=List[ScraperPluginResponse])
def get_active_plugins():
    return scraper_mgr.list_plugins()


@router.post("/run", response_model=ScraperTriggerResponse)
async def run_scrapers(payload: ScraperTriggerRequest, db: Session = Depends(get_db)):
    raw_offers = await scraper_mgr.scrape_all(
        query=payload.query,
        location=payload.location,
        limit=payload.limit_per_plugin
    )

    persisted = 0
    duplicates = 0
    sources = set()

    for r in raw_offers:
        sources.add(r.source)
        existing = db.query(Job).filter(Job.content_hash == r.content_hash).first()
        if existing:
            duplicates += 1
            continue

        job = Job(
            title=r.title,
            company=r.company,
            location=r.location,
            modality=r.modality,
            contract_type=r.contract_type,
            salary_min=r.salary_min,
            salary_max=r.salary_max,
            currency=r.currency,
            experience_required_years=r.experience_required_years,
            required_skills=r.required_skills,
            nice_to_have_skills=r.nice_to_have_skills,
            description=r.description,
            source=r.source,
            source_url=r.source_url,
            external_id=r.external_id,
            content_hash=r.content_hash,
            published_at=r.published_at
        )
        db.add(job)
        persisted += 1

    db.commit()

    return ScraperTriggerResponse(
        offers_found=len(raw_offers),
        offers_persisted=persisted,
        duplicates_skipped=duplicates,
        sources=list(sources)
    )
