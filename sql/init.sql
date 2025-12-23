-- Создаем таблицу видео
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY,
    creator_id UUID NOT NULL,
    video_created_at TIMESTAMPTZ NOT NULL,
    
    -- Итоговые метрики
    views_count BIGINT DEFAULT 0,
    likes_count BIGINT DEFAULT 0,
    comments_count BIGINT DEFAULT 0,
    reports_count BIGINT DEFAULT 0,
    
    -- Служебные поля
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для videos
CREATE INDEX IF NOT EXISTS idx_videos_creator_id ON videos(creator_id);
CREATE INDEX IF NOT EXISTS idx_videos_video_created_at ON videos(video_created_at);

-- Создаем таблицу снапшотов (почасовая статистика)
CREATE TABLE IF NOT EXISTS video_snapshots (
    id UUID PRIMARY KEY,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    
    -- Метрики на момент снапшота
    views_count BIGINT DEFAULT 0,
    likes_count BIGINT DEFAULT 0,
    comments_count BIGINT DEFAULT 0,
    reports_count BIGINT DEFAULT 0,
    
    -- Дельты (прирост с прошлого замера) - Ключевые поля для вопросов "насколько выросло"
    delta_views_count BIGINT DEFAULT 0,
    delta_likes_count BIGINT DEFAULT 0,
    delta_comments_count BIGINT DEFAULT 0,
    delta_reports_count BIGINT DEFAULT 0,
    
    -- Время замера
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для snapshots (критично для скорости агрегации по датам)
CREATE INDEX IF NOT EXISTS idx_snapshots_video_id ON video_snapshots(video_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_created_at ON video_snapshots(created_at);

-- Комментарии к таблицам (помогают LLM лучше понимать схему, если мы будем выгружать схему динамически)
COMMENT ON TABLE videos IS 'Итоговая статистика по видеороликам';
COMMENT ON COLUMN videos.video_created_at IS 'Дата и время публикации самого видео';

COMMENT ON TABLE video_snapshots IS 'Почасовые замеры статистики (снапшоты) для каждого видео';
COMMENT ON COLUMN video_snapshots.delta_views_count IS 'Прирост просмотров за последний час (или с момента прошлого снапшота)';
COMMENT ON COLUMN video_snapshots.created_at IS 'Время, когда был сделан этот замер статистики';
