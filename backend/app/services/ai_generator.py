"""AI Generator Service: Melakukan panggilan HTTP async ke LLM Provider (Gemini / OpenAI)."""
import json
import re
from typing import Any, Dict, Optional

import httpx

from app.core.config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    NINE_ROUTER_API_KEY,
    NINE_ROUTER_BASE_URL,
    NINE_ROUTER_MODEL,
)
from app.services.prompt_engine import PromptEngine


class AIGenerator:
    @staticmethod
    def _clean_json_text(text: str) -> str:
        """Membersihkan markdown backtick ```json ... ``` dari respons LLM jika ada."""
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        return text

    @classmethod
    async def _call_gemini(cls, system_instruction: str, user_prompt: str) -> str:
        """Panggilan async ke REST API Google Gemini."""
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY belum dikonfigurasi pada file environment (.env)."
            )

        # Normalize model name if user wrote prefix like "gemini/gemini-2.0-flash" or "models/..."
        clean_model = GEMINI_MODEL.replace("gemini/", "").replace("models/", "")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{clean_model}:generateContent?key={GEMINI_API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\n{user_prompt}"}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.4,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Gemini API Error [{response.status_code}]: {response.text}"
                )
            data = response.json()
            try:
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return candidate_text
            except (KeyError, IndexError) as err:
                raise RuntimeError(f"Gagal mem-parsing format respons Gemini: {str(err)}")

    @classmethod
    async def _call_9router(cls, system_instruction: str, user_prompt: str) -> str:
        """Panggilan async ke REST API 9router (OpenAI-compatible format)."""
        if not NINE_ROUTER_API_KEY:
            raise ValueError(
                "NINE_ROUTER_API_KEY belum dikonfigurasi pada file environment (.env)."
            )

        url = f"{NINE_ROUTER_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {NINE_ROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        # 9router defaults to streaming chunks; explicitly enforce stream: false for atomic JSON
        payload = {
            "model": NINE_ROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "temperature": 0.4,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"9router API Error [{response.status_code}]: {response.text}"
                )
            data = response.json()
            return data["choices"][0]["message"]["content"]

    @classmethod
    async def generate_json(cls, system_instruction: str, user_prompt: str) -> Dict[str, Any]:
        """Panggil provider terpilih dan pastikan return valid dictionary JSON."""
        provider = AI_PROVIDER.lower()
        if provider == "9router" or provider == "openai":
            raw_text = await cls._call_9router(system_instruction, user_prompt)
        else:
            raw_text = await cls._call_gemini(system_instruction, user_prompt)

        cleaned = cls._clean_json_text(raw_text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"AI mengembalikan respons yang bukan JSON valid: {cleaned}") from e

    @classmethod
    async def generate_material(
        cls,
        topic: str,
        module_title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menghasilkan artikel materi kimia terstruktur via AI."""
        prompt_data = PromptEngine.build_material_generation_prompt(
            topic=topic,
            module_title=module_title,
        )
        return await cls.generate_json(
            system_instruction=prompt_data["system_instruction"],
            user_prompt=prompt_data["user_prompt"],
        )

    @classmethod
    async def generate_virtual_lab(
        cls,
        teacher_prompt: str,
        material_title: Optional[str] = None,
        material_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menghasilkan konfigurasi lab virtual kimia berbasis prompt guru."""
        prompt_data = PromptEngine.build_lab_generation_prompt(
            teacher_prompt=teacher_prompt,
            material_title=material_title,
            material_content=material_content,
        )
        return await cls.generate_json(
            system_instruction=prompt_data["system_instruction"],
            user_prompt=prompt_data["user_prompt"],
        )

    @classmethod
    async def ask_chembot(cls, question: str) -> str:
        """Menjawab pertanyaan siswa melalui Kimi AI Tutor."""
        prompt_data = PromptEngine.build_tutor_prompt(question)
        provider = AI_PROVIDER.lower()
        if provider == "9router" or provider == "openai":
            return await cls._call_9router(
                prompt_data["system_instruction"], prompt_data["user_prompt"]
            )
        else:
            return await cls._call_gemini(
                prompt_data["system_instruction"], prompt_data["user_prompt"]
            )
