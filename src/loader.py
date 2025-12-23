import asyncio
import logging
import ijson
import os
from datetime import datetime
from src.database import db
from src.config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_json_to_db():
    file_path = settings.DATA_JSON_PATH
    
    if not os.path.exists(file_path):
        logger.error(f"Файл {file_path} не найден!")
        return

    logger.info(f"Начинаем загрузку данных из {file_path}...")
    
    # Списки для накопления данных перед вставкой (batch insert)
    videos_batch = []
    snapshots_batch = []
    
    BATCH_SIZE = 1000  # Размер пачки для вставки
    
    # Получаем пул, но НЕ инициируем его закрытие здесь, так как он общий
    pool = await db.get_pool()

    try:
        with open(file_path, 'rb') as f:
            # ijson.items парсит JSON поток. 'videos.item' означает каждый элемент в массиве "videos"
            videos_stream = ijson.items(f, 'videos.item')
            
            for video in videos_stream:
                # 1. Подготовка данных видео
                v_data = (
                    video.get('id'),
                    video.get('creator_id'),
                    datetime.fromisoformat(video.get('video_created_at')), # Важно: isoformat
                    video.get('views_count', 0),
                    video.get('likes_count', 0),
                    video.get('comments_count', 0),
                    video.get('reports_count', 0),
                    # Используем текущее время для created_at/updated_at если их нет
                    datetime.now(), 
                    datetime.now()
                )
                videos_batch.append(v_data)
                
                # 2. Подготовка данных снапшотов
                snapshots = video.get('snapshots', [])
                for snap in snapshots:
                    s_data = (
                        snap.get('id'),
                        snap.get('video_id'),
                        snap.get('views_count', 0),
                        snap.get('likes_count', 0),
                        snap.get('comments_count', 0),
                        snap.get('reports_count', 0),
                        snap.get('delta_views_count', 0),
                        snap.get('delta_likes_count', 0),
                        snap.get('delta_comments_count', 0),
                        snap.get('delta_reports_count', 0),
                        datetime.fromisoformat(snap.get('created_at')),
                        datetime.now()
                    )
                    snapshots_batch.append(s_data)

                # 3. Если накопилось достаточно данных, вставляем в БД
                if len(videos_batch) >= BATCH_SIZE:
                    await insert_batch(pool, videos_batch, snapshots_batch)
                    videos_batch = []
                    snapshots_batch = []

            # 4. Вставляем остатки
            if videos_batch:
                await insert_batch(pool, videos_batch, snapshots_batch)

        logger.info("Загрузка данных завершена успешно!")

    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        raise e
    
    # ВАЖНО: Убрали блок finally с закрытием соединения, чтобы не убивать пул бота

async def insert_batch(pool, videos, snapshots):
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Вставка видео
            if videos:
                await conn.copy_records_to_table(
                    'videos',
                    records=videos,
                    columns=[
                        'id', 'creator_id', 'video_created_at', 
                        'views_count', 'likes_count', 'comments_count', 'reports_count',
                        'created_at', 'updated_at'
                    ]
                )
            
            # Вставка снапшотов
            if snapshots:
                await conn.copy_records_to_table(
                    'video_snapshots',
                    records=snapshots,
                    columns=[
                        'id', 'video_id', 
                        'views_count', 'likes_count', 'comments_count', 'reports_count',
                        'delta_views_count', 'delta_likes_count', 'delta_comments_count', 'delta_reports_count',
                        'created_at', 'updated_at'
                    ]
                )
            logger.info(f"Вставлено {len(videos)} видео и {len(snapshots)} снапшотов.")

async def run_standalone():
    """Специальная обертка для ручного запуска скрипта"""
    await db.connect()
    try:
        await load_json_to_db()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_standalone())
