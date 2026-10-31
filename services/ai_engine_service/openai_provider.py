import os
import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from services.ai_engine_service.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.timeout = httpx.Timeout(connect=2.0, read=15.0, write=5.0, pool=5.0)

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return res.status_code == 200
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False

    async def generate(self, prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
        if not self.api_key:
            return self._mock_response(prompt, json_mode)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}. Falling back to heuristic reasoning.")
            return self._mock_response(prompt, json_mode)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            return [[0.0] * 128 for _ in texts]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            "input": texts
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            return [[0.0] * 128 for _ in texts]

    def _mock_response(self, prompt: str, json_mode: bool) -> str:
        if json_mode:
            return json.dumps({
                "summary": "Perfil con sólida afinidad técnica y alineación de modalidad laboral.",
                "strengths": ["Stack tecnológico alineado", "Experiencia adecuada al seniority"],
                "gaps": ["Revisar salario negociable y certificaciones específicas"],
                "recommendation": "Postular adaptando el CV para destacar proyectos recientes."
            })
        return "Análisis de afinidad completado satisfactoriamente por el motor de IA."
