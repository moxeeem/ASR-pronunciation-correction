#!/bin/bash

# название Docker-контейнера и образа
CONTAINER_NAME="pronunciation_api_container"
IMAGE_NAME="pronunciation_api_image"

# создаём/проверяем директорию для модели
mkdir -p ./model

# остановка и удаление старого контейнера
echo "Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

# пересобираем образ
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# запуск нового контейнера с переменными окружения и со смонтированной моделью
echo "Starting new container..."
docker run -d --name $CONTAINER_NAME \
  --env-file .env \
  -p 8000:8000 \
  -v $(pwd)/model:/app/model \
  $IMAGE_NAME

echo "Container restarted successfully!"
