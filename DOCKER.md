# 🐳 Vitacurai API - Docker

Ejecuta la API Vitacurai en Docker fácilmente.

## 📋 Requisitos
- Docker instalado
- Puerto 8000 disponible

## 🚀 Uso Rápido

### Script Automático (Recomendado)
```bash
# Construir y ejecutar
./docker-deploy.sh run

# Ver logs
./docker-deploy.sh logs

# Detener
./docker-deploy.sh stop
```

### Docker Compose
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Manual
```bash
# Construir y ejecutar
docker build -t vitacurai-api .
docker run -d --name vitacurai-api -p 8000:8000 vitacurai-api
```

## 🌐 Acceso
- **API**: http://localhost:8000
- **Health**: http://localhost:8000/health  
- **Docs**: http://localhost:8000/docs

## 🛠️ Comandos Útiles
```bash
# Ver contenedores
docker ps

# Logs del contenedor  
docker logs vitacurai-api

# Detener
docker stop vitacurai-api
```

## ✅ Estado Actual
- ✅ Imagen Docker funcionando
- ✅ API ejecutándose en puerto 8000  
- ✅ Endpoints disponibles: `/health`, `/calibrar`, `/calcular_area`