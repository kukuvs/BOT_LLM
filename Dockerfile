# Используем ultra-light образ
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для сборки (нужны для asyncpg)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev

# Копируем и ставим зависимости (кэширование слоев)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# ВАЖНО: Добавляем текущую директорию в PYTHONPATH, чтобы Python видел 'src'
ENV PYTHONPATH=/app

# Запуск
CMD ["python", "src/main.py"]
