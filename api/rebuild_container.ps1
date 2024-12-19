# PowerShell-скрипт для автоматизации пересборки
#   и перезапуска Docker-контейнера

# название Docker-контейнера и образа
$CONTAINER_NAME = "pronunciation_api_container"
$IMAGE_NAME = "pronunciation_api_image"

# создание/проверка существования директории для модели
# New-Item -Type Directory -Force model

Write-Host "Stopping existing container..."
# остановка и удаление старого контейнера
if (docker ps -aq --filter "name=$CONTAINER_NAME") {
    docker stop $CONTAINER_NAME | Out-Null
    docker rm $CONTAINER_NAME | Out-Null
}

Write-Host "Building Docker image..."
# пересборка образа
docker build -t $IMAGE_NAME .

Write-Host "Starting new container..."
# запуск нового контейнера с переменными окружения и со смонтированной моделью
docker run -d --name $CONTAINER_NAME `
  --env-file .env `
  -p 8000:8000 `
  -v "$((Get-Location).Path)/model:/app/model" `
  $IMAGE_NAME

Write-Host "Container restarted successfully!"
