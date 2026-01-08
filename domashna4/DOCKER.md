# Docker Setup for Crypto Analysis Application

## Prerequisites
- Docker Desktop installed
- Docker Compose installed

## Quick Start

### Development Mode

1. Build and run the application:
```bash
docker-compose up --build
```

2. Access the application:
- Main app: http://localhost:8000
- API docs: http://localhost:8000/docs
- Interactive API: http://localhost:8000/redoc

3. Stop the application:
```bash
docker-compose down
```

### Production Mode

1. Build the production image:
```bash
docker build -f Dockerfile.prod -t crypto-analysis:prod .
```

2. Run the production container:
```bash
docker run -d -p 8000:8000 --name crypto-analysis-prod crypto-analysis:prod
```

3. Stop and remove the container:
```bash
docker stop crypto-analysis-prod
docker rm crypto-analysis-prod
```

## Docker Commands

### View logs
```bash
docker-compose logs -f
```

### Rebuild without cache
```bash
docker-compose build --no-cache
docker-compose up
```

### Execute commands inside container
```bash
docker-compose exec app bash
```

### Remove all containers and volumes
```bash
docker-compose down -v
```

## Project Structure
- `Dockerfile` - Development Docker configuration
- `Dockerfile.prod` - Production Docker configuration
- `docker-compose.yml` - Docker Compose orchestration
- `.dockerignore` - Files to exclude from Docker context

## Notes
- The development mode includes auto-reload on code changes
- Production mode uses 4 workers for better performance
- The SQLite database (`crypto.db`) is persisted in the container
- Static files and templates are copied into the container

