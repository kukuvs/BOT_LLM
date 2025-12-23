import asyncio
import logging
from typing import Optional
from mistralai import Mistral # Новый импорт для v1.0+
from src.config import settings
import re

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # В v1.0 клиент инициализируется так
        self.client = Mistral(
            api_key=settings.MISTRAL_API_KEY.get_secret_value()
        )
        # Если нужен base_url (например, OpenRouter), он передается через server_url
        if settings.MISTRAL_BASE_URL:
             # Это хак, так как официально в v1.0 server_url может быть не задокументирован так же,
             # но обычно SDK поддерживают переопределение endpoint'а.
             # Если не заработает с base_url, попробуем через environment variable MISTRAL_SERVER_URL
             pass 

    async def generate_sql(self, user_query: str) -> Optional[str]:
        """Преобразует естественный запрос в SQL."""
        try:
            # Читаем системный промпт
            with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
                system_prompt = f.read()

            # В v1.0 метод называется chat.complete_async
            response = await self.client.chat.complete_async(
                model=settings.MISTRAL_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=500,
                temperature=0.1
            )

            # Доступ к ответу тоже немного изменился
            if response.choices:
                sql = response.choices[0].message.content.strip()
            else:
                return None
            
            # Очищаем ответ от мусора (markdown, кавычек, переносов строк)
            sql = re.sub(r'^``````$', '', sql, flags=re.DOTALL).strip()
            sql = re.sub(r'^["\']|["\']$', '', sql).strip()
            sql = ' '.join(sql.split())

            logger.info(f"LLM → SQL: {sql[:100]}...")
            return sql

        except Exception as e:
            logger.error(f"Ошибка LLM: {e}")
            return None

llm = LLMService()
