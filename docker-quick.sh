#!/bin/bash

# Script rápido para desarrollo con Docker
# Uso: ./docker-quick.sh [start|stop|build|logs]

CONTAINER_NAME="vitacurai-dev"
IMAGE_NAME="vitacurai-api"

case "$1" in
  "build")
    echo "🔨 Construyendo imagen..."
    docker build -t $IMAGE_NAME .
    ;;
  "start")
    echo "🚀 Iniciando contenedor de desarrollo..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    docker run -d \
      --name $CONTAINER_NAME \
      -p 8000:8000 \
      -v "$(pwd):/app" \
      -e PYTHONPATH=/app \
      $IMAGE_NAME
    echo "✅ Contenedor iniciado en http://localhost:8000"
    ;;
  "stop")
    echo "⏹️ Deteniendo contenedor..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    ;;
  "logs")
    docker logs -f $CONTAINER_NAME
    ;;
  *)
    echo "Uso: $0 [build|start|stop|logs]"
    ;;
esac