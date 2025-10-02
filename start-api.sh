#!/bin/bash
echo "🧹 Limpiando contenedores existentes..."
docker stop vitacurai-api 2>/dev/null || true
docker rm vitacurai-api 2>/dev/null || true

echo "🚀 Iniciando API con docker-compose..."
docker-compose up -d

echo "⏳ Esperando que la API inicie..."
sleep 3

echo "✅ Verificando estado..."
docker-compose ps

echo "🌐 Probando endpoints..."
echo "Health: $(curl -s http://localhost:8000/health)"

echo "📝 URLs disponibles:"
echo "  - API: http://localhost:8000"
echo "  - Health: http://localhost:8000/health"
echo "  - Docs: http://localhost:8000/docs"
