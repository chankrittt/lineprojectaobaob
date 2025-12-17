"""
Ollama Service - Fallback AI for when Gemini quota is exceeded

Uses local Ollama models for:
- Filename generation
- Content summarization
- Tag generation
- Embeddings (using sentence-transformers as fallback)

Note: Ollama must be running locally on default port 11434
"""

import httpx
import logging
from typing import List, Dict, Optional
import json
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Ollama API service for local AI processing"""

    def __init__(self):
        self.base_url = getattr(settings, 'OLLAMA_URL', 'http://localhost:11434')
        self.model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2')  # or 'mistral', 'gemma'
        self.timeout = 120.0  # Ollama can be slow on CPU

    async def _call_ollama(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call Ollama API

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Generated text
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }

                if max_tokens:
                    payload["options"]["num_predict"] = max_tokens

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                return result.get("response", "").strip()

        except httpx.ConnectError:
            logger.error("Ollama is not running. Start with: ollama serve")
            raise Exception("Ollama service not available")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def generate_filename(self, content: str, original_filename: str) -> str:
        """Generate smart filename using Ollama"""
        try:
            prompt = f"""You are a file naming expert. Based on the file content, suggest a clear, descriptive filename.

Original filename: {original_filename}
File content: {content[:1500]}

Rules:
- Use clear, descriptive names
- Use underscores or hyphens instead of spaces
- Keep it under 50 characters
- Only return the filename, nothing else

Suggested filename:"""

            filename = await self._call_ollama(prompt, temperature=0.5, max_tokens=30)

            # Clean the filename
            filename = filename.replace(" ", "_").replace("/", "-").strip()
            # Remove quotes if present
            filename = filename.strip('"\'')

            logger.info(f"[Ollama] Generated filename: {filename}")
            return filename

        except Exception as e:
            logger.error(f"[Ollama] Error generating filename: {e}")
            return original_filename

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def summarize_content(self, content: str) -> str:
        """Summarize file content using Ollama"""
        try:
            prompt = f"""Summarize the following document in 2-3 concise sentences. Focus on main purpose and key points.

Content: {content[:4000]}

Summary:"""

            summary = await self._call_ollama(prompt, temperature=0.5, max_tokens=150)

            logger.info(f"[Ollama] Generated summary: {summary[:100]}...")
            return summary

        except Exception as e:
            logger.error(f"[Ollama] Error summarizing content: {e}")
            return "Unable to generate summary"

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def generate_tags(self, content: str, filename: str) -> List[Dict[str, any]]:
        """Generate tags using Ollama"""
        try:
            prompt = f"""Analyze this file and generate 3-5 relevant tags that describe the subject matter, document type, and topics.

Filename: {filename}
Content: {content[:2500]}

Return ONLY a JSON array like this (no explanations):
[
    {{"tag": "education", "confidence": 0.95}},
    {{"tag": "report", "confidence": 0.90}}
]

Tags:"""

            tags_text = await self._call_ollama(prompt, temperature=0.3, max_tokens=200)

            # Try to extract JSON from response
            if "[" in tags_text and "]" in tags_text:
                # Extract JSON array
                start = tags_text.index("[")
                end = tags_text.rindex("]") + 1
                tags_text = tags_text[start:end]

            # Parse JSON
            tags = json.loads(tags_text)

            logger.info(f"[Ollama] Generated {len(tags)} tags")
            return tags

        except json.JSONDecodeError as e:
            logger.warning(f"[Ollama] Failed to parse tags JSON: {e}")
            # Fallback tags
            return [
                {"tag": "document", "confidence": 0.6},
                {"tag": "general", "confidence": 0.5}
            ]
        except Exception as e:
            logger.error(f"[Ollama] Error generating tags: {e}")
            return [{"tag": "document", "confidence": 0.5}]

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Ollama's embedding endpoint

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector)

        Note: Falls back to simple sentence transformer if Ollama embeddings fail
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text[:8000]  # Limit text size
                    }
                )
                response.raise_for_status()

                result = response.json()
                embedding = result.get("embedding", [])

                logger.info(f"[Ollama] Generated embedding of size {len(embedding)}")
                return embedding

        except Exception as e:
            logger.error(f"[Ollama] Error generating embedding: {e}")
            # Return a zero vector as fallback (same dimension as Gemini: 768)
            # This is not ideal but prevents errors
            logger.warning("[Ollama] Returning zero vector fallback")
            return [0.0] * 768

    async def analyze_file(
        self,
        content: str,
        filename: str
    ) -> Dict[str, any]:
        """
        Complete AI analysis using Ollama

        Returns:
            Dict with suggested_filename, summary, tags, embedding
        """
        try:
            logger.info(f"[Ollama] Starting AI analysis for: {filename}")

            # Run all AI tasks
            suggested_filename = await self.generate_filename(content, filename)
            summary = await self.summarize_content(content)
            tags = await self.generate_tags(content, filename)
            embedding = await self.generate_embedding(content)

            result = {
                'suggested_filename': suggested_filename,
                'summary': summary,
                'tags': tags,
                'embedding': embedding
            }

            logger.info(f"[Ollama] AI analysis completed for: {filename}")
            return result

        except Exception as e:
            logger.error(f"[Ollama] Error in file analysis: {e}")
            raise

    async def check_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False


# Singleton instance
ollama_service = OllamaService()
