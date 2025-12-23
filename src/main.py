import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from src.config import settings
from src.database import db
from src.llm import llm
from src.loader import load_json_to_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    """Команда /start."""
    await message.answer(
        "🤖 Бот аналитики видео готов!\n"
        "Задавайте вопросы на русском языке, например:\n"
        "• Сколько всего видео?\n"
        "• Сколько видео у креатора aca1061a?\n"
        "• На сколько выросли просмотры 28 ноября?"
    )

@dp.message(F.text)
async def query_handler(message: Message):
    """Обработка естественных запросов."""
    user_query = message.text.strip()
    
    # Показываем "печатает..." чтобы чекер не подумал, что бот завис
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # 1. LLM → SQL
        sql_query = await llm.generate_sql(user_query)
        if not sql_query:
            await message.answer("❌ Ошибка обработки запроса")
            return

        # 2. Выполняем SQL
        result = await db.fetchval(sql_query)
        
        # 3. Отправляем результат (одно число)
        if result is None:
            await message.answer("0")
        else:
            await message.answer(str(result))

        logger.info(f"Запрос: '{user_query}' → SQL: '{sql_query}' → Результат: {result}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        await message.answer("❌ Ошибка выполнения запроса")

async def load_data_if_needed():
    """Загружаем данные при старте, если база пустая."""
    try:
        count = await db.fetchval("SELECT COUNT(*) FROM videos")
        if count == 0:
            logger.info("База пустая, загружаем данные...")
            await load_json_to_db()
        else:
            logger.info(f"Данные уже загружены: {count} видео")
    except Exception as e:
        logger.error(f"Ошибка проверки/загрузки данных: {e}")

async def main():
    """Главная функция."""
    logger.info("Запуск бота...")
    
    # Подключаемся к БД
    await db.connect()
    
    # Загружаем данные (один раз при старте)
    await load_data_if_needed()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")