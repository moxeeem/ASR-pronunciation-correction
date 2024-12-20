# используем Python 3.10 образ 
FROM python:3.10-slim

WORKDIR /app

# устанавливаем git (может быть нужен нужен для установки editable-версии пакета)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# python-dotenv - пакет для загрузки .env
RUN pip install python-dotenv

# Скопируем зависимости
COPY README.md pyproject.toml requirements.txt ./

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# скопируем исходники приложения
COPY src ./src
COPY .env ./
# COPY data ./data

# устанавливаем рабочую директорию на каталог с API
WORKDIR /app/src

# команда запуска FastAPI сервера через uvicorn
CMD ["uvicorn", "pronunciation_api.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]