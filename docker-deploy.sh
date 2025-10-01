#!/bin/bash

# Script simplificado para Vitacurai API Docker
set -e

# Configuración
CONTAINER_NAME="vitacurai-api"
IMAGE_NAME="vitacurai-api:latest"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función de ayuda
show_help() {
    echo "Uso: $0 [build|run|stop|logs|clean]"
    echo ""
    echo "  build  - Construir imagen"
    echo "  run    - Ejecutar contenedor"
    echo "  stop   - Detener contenedor" 
    echo "  logs   - Ver logs"
    echo "  clean  - Limpiar todo"
}

# Función principal según comando
case ${1:-help} in
    build)
        echo -e "${GREEN}📦 Construyendo imagen...${NC}"
        docker build -t $IMAGE_NAME .
        ;;
    run)
        echo -e "${GREEN}🚀 Ejecutando contenedor...${NC}"
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        mkdir -p logs checkpoints
        docker run -d --name $CONTAINER_NAME -p 8000:8000 \
            -v "$(pwd)/logs:/app/logs" \
            -v "$(pwd)/checkpoints:/app/checkpoints" \
            $IMAGE_NAME
        echo -e "${GREEN}✅ Contenedor iniciado en http://localhost:8000${NC}"
        ;;
    stop)
        echo -e "${YELLOW}⏹️ Deteniendo contenedor...${NC}"
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        ;;
    logs)
        docker logs -f $CONTAINER_NAME
        ;;
    clean)
        echo -e "${RED}🧹 Limpiando...${NC}"
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        docker rmi $IMAGE_NAME 2>/dev/null || true
        ;;
    *)
        show_help
        ;;
esac