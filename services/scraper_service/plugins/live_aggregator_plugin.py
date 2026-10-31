import re
import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from services.scraper_service.base import BaseScraperPlugin, RawJobData

logger = logging.getLogger(__name__)


class LiveWebAggregatorPlugin(BaseScraperPlugin):
    """
    Plugin en vivo que consulta agregadores internacionales y nacionales con soporte para España / Remoto
    (Remotive API y Jobicy API en vivo).
    """
    plugin_id = "live_web_aggregator"
    name = "Agregador Web en Vivo (Remotive & Jobicy)"
    country = "Global / ES"
    region = "Nacional & Remoto"
    is_regional = False
    is_public_agency = False

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "JobHunterAI/1.0 (+https://github.com/Glinkyz/jobhunter-ai)"
        }

    async def scrape(self, query: str = "", location: str = "", limit: int = 15) -> List[RawJobData]:
        offers: List[RawJobData] = []

        # 1. Remotive API en vivo
        try:
            remotive_url = "https://remotive.com/api/remote-jobs"
            params = {}
            if query:
                params["search"] = query
            params["limit"] = min(limit, 20)

            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                resp = await client.get(remotive_url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("jobs", [])
                    for item in data[:limit]:
                        offers.append(self._parse_remotive_job(item))
        except Exception as e:
            logger.warning(f"Error fetching live jobs from Remotive: {e}")

        # 2. Jobicy API en vivo (si necesitamos más o como fuente complementaria)
        if len(offers) < limit:
            try:
                jobicy_url = "https://jobicy.com/api/v2/remote-jobs"
                params = {"count": min(limit, 20)}
                if query:
                    clean_tag = re.sub(r"[^a-zA-Z0-9]", "", query.lower())
                    if clean_tag:
                        params["tag"] = clean_tag

                async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                    resp = await client.get(jobicy_url, params=params)
                    if resp.status_code == 200:
                        data = resp.json().get("jobs", [])
                        for item in data[:limit - len(offers)]:
                            offers.append(self._parse_jobicy_job(item))
            except Exception as e:
                logger.warning(f"Error fetching live jobs from Jobicy: {e}")

        # Filtrar por localización si se especifica
        if location:
            loc_lower = location.lower().strip()
            filtered = [
                o for o in offers
                if loc_lower in o.location.lower() or o.modality == "REMOTE" or "españa" in o.location.lower() or "spain" in o.location.lower()
            ]
            return filtered or offers

        return offers[:limit]

    def _parse_remotive_job(self, item: dict) -> RawJobData:
        title = item.get("title", "Posición Técnica")
        company = item.get("company_name", "Empresa Tecnológica")
        loc = item.get("candidate_required_location") or "Remoto (España / Global)"
        desc = item.get("description", "")
        # Limpiar tags HTML básicos
        clean_desc = re.sub(r"<[^>]+>", " ", desc).strip()[:500]

        salary_text = item.get("salary", "")
        salary_min, salary_max = self._extract_salary_numbers(salary_text)

        tags = item.get("tags", [])
        if not tags and "tags" in item:
            tags = []

        return RawJobData(
            title=title,
            company=company,
            location=f"{loc}",
            modality="REMOTE",
            contract_type="Indefinido",
            salary_min=salary_min or 45000.0,
            salary_max=salary_max or 65000.0,
            currency="EUR",
            experience_required_years=3.0,
            required_skills=tags[:6] if tags else ["Software Development", "Git"],
            nice_to_have_skills=["Docker", "Cloud", "CI/CD"],
            description=clean_desc or f"Oportunidad remota para el rol de {title} en {company}.",
            source="Remotive (Live)",
            source_url=item.get("url") or "https://remotive.com",
            external_id=f"remotive_{item.get('id')}",
            published_at=datetime.now(timezone.utc)
        )

    def _parse_jobicy_job(self, item: dict) -> RawJobData:
        title = item.get("jobTitle", "Posición de Empleo")
        company = item.get("companyName", "Empresa")
        loc = item.get("jobGeo") or "Remoto España / Global"
        desc = item.get("jobDescription", "")
        clean_desc = re.sub(r"<[^>]+>", " ", desc).strip()[:500]

        salary_min = float(item.get("annualSalaryMin") or 40000.0)
        salary_max = float(item.get("annualSalaryMax") or 55000.0)

        industry = item.get("jobIndustry") or []
        if isinstance(industry, str):
            skills = [industry]
        elif isinstance(industry, list):
            skills = industry
        else:
            skills = ["Tech", "IT"]

        return RawJobData(
            title=title,
            company=company,
            location=loc,
            modality="REMOTE",
            contract_type="Indefinido",
            salary_min=salary_min,
            salary_max=salary_max,
            currency="EUR",
            experience_required_years=2.0,
            required_skills=skills[:5],
            nice_to_have_skills=["Metodologías Ágiles", "Scrum"],
            description=clean_desc or f"Vacante publicada en Jobicy para {title}.",
            source="Jobicy (Live)",
            source_url=item.get("url") or "https://jobicy.com",
            external_id=f"jobicy_{item.get('id')}",
            published_at=datetime.now(timezone.utc)
        )

    def _extract_salary_numbers(self, text: str) -> tuple[Optional[float], Optional[float]]:
        if not text:
            return None, None
        nums = re.findall(r"\b\d+(?:[\.,]\d+)?k?\b", text.lower())
        parsed = []
        for n in nums:
            try:
                val = n.replace(",", ".")
                if "k" in val:
                    parsed.append(float(val.replace("k", "")) * 1000)
                else:
                    parsed.append(float(val))
            except Exception:
                continue
        if len(parsed) >= 2:
            return min(parsed[0], parsed[1]), max(parsed[0], parsed[1])
        elif len(parsed) == 1:
            return parsed[0], parsed[0] * 1.25
        return None, None
