import google.generativeai as genai
from typing import List, Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_filename(self, content: str, original_filename: str) -> str:
        """Generate smart filename based on content"""
        try:
            prompt = f"""
            You are a file naming expert. Based on the file content below, suggest a clear,
            descriptive filename that accurately represents what the file is about.

            Original filename: {original_filename}
            File content (excerpt): {content[:2000]}

            Rules:
            - Use clear, descriptive names
            - Use underscores or hyphens instead of spaces
            - Keep it under 50 characters
            - Include file type context if relevant (e.g., resume, invoice, report)
            - Only return the filename, nothing else

            Suggested filename:
            """

            response = self.model.generate_content(prompt)
            filename = response.text.strip()

            # Clean the filename
            filename = filename.replace(" ", "_").replace("/", "-")

            logger.info(f"Generated filename: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            # Fallback to original filename
            return original_filename

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def summarize_content(self, content: str) -> str:
        """Summarize file content"""
        try:
            prompt = f"""
            Summarize the following document content in 2-3 concise sentences.
            Focus on the main purpose, key points, and important information.

            Content: {content[:5000]}

            Summary:
            """

            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            logger.info(f"Generated summary: {summary[:100]}...")
            return summary

        except Exception as e:
            logger.error(f"Error summarizing content: {e}")
            return "Unable to generate summary"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_tags(self, content: str, filename: str) -> List[Dict[str, any]]:
        """Generate relevant tags for the file"""
        try:
            prompt = f"""
            You are a content categorization expert. Analyze the following file and generate 3-5 relevant tags.

            Filename: {filename}
            Content (excerpt): {content[:3000]}

            Generate tags that describe:
            - Subject matter (e.g., education, business, personal)
            - Document type (e.g., invoice, resume, report, notes)
            - Topics (e.g., programming, finance, health)
            - Any other relevant categories

            Return ONLY a JSON array of objects with this format:
            [
                {{"tag": "education", "confidence": 0.95}},
                {{"tag": "english", "confidence": 0.90}},
                {{"tag": "ielts", "confidence": 0.85}}
            ]

            Important: Return ONLY the JSON array, no explanations or other text.
            """

            response = self.model.generate_content(prompt)
            tags_text = response.text.strip()

            # Clean response (remove markdown code blocks if present)
            if "```json" in tags_text:
                tags_text = tags_text.split("```json")[1].split("```")[0].strip()
            elif "```" in tags_text:
                tags_text = tags_text.split("```")[1].split("```")[0].strip()

            # Parse JSON
            tags = json.loads(tags_text)

            logger.info(f"Generated {len(tags)} tags")
            return tags

        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            # Fallback tags
            return [{"tag": "document", "confidence": 0.5}]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for semantic search"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )

            embedding = result['embedding']
            logger.info(f"Generated embedding of size {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def analyze_file(
        self,
        content: str,
        filename: str
    ) -> Dict[str, any]:
        """
        Complete AI analysis of a file
        Returns: {
            'suggested_filename': str,
            'summary': str,
            'tags': List[Dict],
            'embedding': List[float]
        }
        """
        try:
            logger.info(f"Starting AI analysis for: {filename}")

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

            logger.info(f"AI analysis completed for: {filename}")
            return result

        except Exception as e:
            logger.error(f"Error in file analysis: {e}")
            raise


# Singleton instance
ai_service = AIService()
