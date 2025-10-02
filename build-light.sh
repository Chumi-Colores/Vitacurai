#!/bin/bash
echo "🏗️ Construyendo imagen Docker LIGERA..."

# Limpiar imagen anterior
docker rmi vitacurai-test:light 2>/dev/null || true

# Construir imagen optimizada
docker build \
    --no-cache \
    -f Dockerfile.light \
    -t vitacurai-test:light .

echo ""
echo "📊 COMPARACIÓN DE TAMAÑOS:"
echo "Antes:"
docker images vitacurai-test:latest --format "{{.Size}}" 2>/dev/null || echo "No encontrada"
echo "Después:"
docker images vitacurai-test:light --format "{{.Size}}"

echo ""
echo "💾 REDUCCIÓN ESTIMADA:"
echo "- .dockerignore: ~70% menos en COPY"
echo "- Requirements optimizado: ~50% menos dependencias"
echo "- Multietapa: ~20% menos tamaño final"
echo "- Total esperado: <500MB (vs actual ~3GB)"
