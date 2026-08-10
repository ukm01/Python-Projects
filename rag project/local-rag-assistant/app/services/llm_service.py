import requests

from app.config import settings


class LLMService:
    def generate_answer(self, prompt: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        response = requests.post(
            url=url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()


llm_service = LLMService()