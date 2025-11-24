# CLAUDE.md - AI Assistant Guide

> **Last Updated:** 2025-11-14
> **Project:** Agentic AI IVR Demo
> **Version:** 0.1.0

## Project Overview

This is a **WebSocket-based service** for Interactive Voice Response (IVR) demonstrations using agentic AI. The application is built with **FastAPI** and follows modern Python async patterns with production-ready configuration management and structured logging.

### Core Purpose
- Provide a WebSocket endpoint for real-time IVR communication
- Demonstrate agentic AI integration capabilities
- Support both development and production environments with configurable logging

## Technology Stack

### Primary Technologies
- **Python 3.14+** - Language runtime
- **FastAPI (>=0.121.1)** - Modern async web framework
- **websockets (>=15.0.1)** - WebSocket protocol support
- **Uvicorn** - ASGI server
- **Pydantic Settings (>=2.0.0)** - Type-safe configuration

### Package Management
- **uv** - Ultra-fast Python package installer and resolver
- **uv.lock** - Locked dependencies for reproducible builds

### Deployment
- **Docker** with Alpine Linux base image
- **Docker Compose** for orchestration

## Repository Structure

```
agentic-ai-ivr-demo/
├── .env.example              # Template for environment variables
├── .gitignore               # Git ignore patterns
├── .python-version          # Python version (3.14)
├── README.md                # User-facing documentation
├── CLAUDE.md                # This file - AI assistant guide
├── docker-compose.yml       # Service orchestration
└── ws-service/              # WebSocket service (main application)
    ├── .dockerignore        # Docker build exclusions
    ├── Dockerfile           # Container definition
    ├── config.py            # Configuration management (Settings class)
    ├── main.py              # FastAPI application entry point
    ├── pyproject.toml       # Project metadata & dependencies
    └── uv.lock              # Locked dependency versions
```

### Key Files and Their Purposes

| File | Purpose | Lines | Key Elements |
|------|---------|-------|--------------|
| `ws-service/main.py` | Application entry point | 175 | FastAPI app, WebSocket endpoint, logging setup |
| `ws-service/config.py` | Configuration management | ~70 | Settings class, environment variable loading |
| `docker-compose.yml` | Service orchestration | ~20 | Service definitions, networking, env loading |
| `ws-service/Dockerfile` | Container image | ~10 | Multi-stage build with uv |
| `.env.example` | Config template | ~8 | All configurable environment variables |

## Configuration Management

### Pattern: Pydantic Settings

The project uses **pydantic-settings** for type-safe, environment-driven configuration.

**Location:** `ws-service/config.py`

```python
class Settings(BaseSettings):
    # Application
    app_name: str = "Agentic AI IVR Demo"
    app_version: str = "0.1.0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "text"

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
```

### Configuration Guidelines for AI Assistants

1. **Always use the Settings class** - Never hardcode configuration values
2. **Add new config to Settings class** - Use type hints and defaults
3. **Update .env.example** - Document all new environment variables
4. **Use Literal types** - For restricted value sets (log levels, environments)
5. **Provide sensible defaults** - All configs should work without .env file

### Environment Variables

| Variable | Type | Default | Options | Purpose |
|----------|------|---------|---------|---------|
| `APP_NAME` | str | "Agentic AI IVR Demo" | any | Application identifier |
| `APP_VERSION` | str | "0.1.0" | semver | Version string |
| `HOST` | str | "0.0.0.0" | valid host | Server bind address |
| `PORT` | int | 8000 | 1-65535 | Server port |
| `LOG_LEVEL` | str | "INFO" | DEBUG/INFO/WARNING/ERROR/CRITICAL | Logging verbosity |
| `LOG_FORMAT` | str | "text" | json/text | Log output format |
| `ENVIRONMENT` | str | "development" | development/staging/production | Deployment environment |

## Logging Conventions

### Dual-Format Logging System

The application supports two logging formats configured via `LOG_FORMAT` environment variable:

#### Text Format (Human-Readable)
```
2025-11-12 10:30:45 - main - INFO - Application starting
```

#### JSON Format (Structured)
```json
{
  "timestamp": "2025-11-12T10:30:45.123456",
  "level": "INFO",
  "logger": "main",
  "message": "Application starting",
  "module": "main",
  "function": "startup_event",
  "line": 85
}
```

### Logging Levels and When to Use Them

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Development details, message content | `logger.debug("Received message", extra={"message": data})` |
| **INFO** | Application lifecycle, connections | `logger.info("Client connected", extra={"client_host": host})` |
| **WARNING** | Degraded operation, deprecated usage | `logger.warning("Deprecated pattern used")` |
| **ERROR** | Errors with recovery, exceptions | `logger.error("Connection failed", exc_info=True)` |
| **CRITICAL** | System failures requiring intervention | `logger.critical("Database unavailable")` |

### Logging Best Practices

1. **Use extra fields** for contextual data:
   ```python
   logger.info("Client connected", extra={
       "client_host": websocket.client.host,
       "client_port": websocket.client.port
   })
   ```

2. **Include exc_info=True** for exceptions:
   ```python
   logger.error("WebSocket error occurred", exc_info=True, extra={
       "error_type": type(e).__name__
   })
   ```

3. **Create module-level loggers**:
   ```python
   logger = logging.getLogger(__name__)
   ```

4. **Don't log sensitive data** - PII, credentials, tokens

## API Endpoints

### REST Endpoints

#### Health Check
- **Route:** `GET /`
- **Handler:** `read_root()` in `main.py:102-111`
- **Response:**
  ```json
  {
    "message": "Agentic AI IVR Demo is running",
    "version": "0.1.0",
    "status": "healthy"
  }
  ```
- **Purpose:** Container health checks, service discovery

### WebSocket Endpoints

#### Test WebSocket
- **Route:** `ws://localhost:8000/ws/test`
- **Handler:** `websocket_endpoint()` in `main.py:114-167`
- **Behavior:**
  - Accepts connection
  - Echoes messages back with prefix: `"Message text was: {data}"`
  - Logs connection, messages, and disconnection
  - Handles errors gracefully
- **Client Example:**
  ```javascript
  const ws = new WebSocket('ws://localhost:8000/ws/test');
  ws.onopen = () => ws.send('Hello');
  ws.onmessage = (event) => console.log(event.data);
  ```

## Code Patterns and Conventions

### 1. Async/Await Pattern

This project is **fully async**. Always use async/await:

```python
# ✅ CORRECT
@app.websocket("/ws/example")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(response)

# ❌ INCORRECT - Don't mix sync code in async handlers
@app.websocket("/ws/example")
def websocket_handler(websocket: WebSocket):  # Missing async
    time.sleep(1)  # Blocking call - use asyncio.sleep instead
```

### 2. FastAPI Lifespan Pattern

Use `@asynccontextmanager` for startup/shutdown logic:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application starting")
    yield
    # Shutdown logic
    logger.info("Application shutting down")

app = FastAPI(lifespan=lifespan)
```

**Location:** `main.py:76-93`

### 3. Error Handling Pattern

Always handle WebSocket errors with specific exception types:

```python
try:
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
except WebSocketDisconnect:
    logger.info("Client disconnected gracefully")
except Exception as e:
    logger.error("Unexpected error", exc_info=True, extra={
        "error_type": type(e).__name__
    })
```

**Location:** `main.py:114-167`

### 4. Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | `snake_case` | `client_host`, `message_data` |
| Functions | `snake_case` | `websocket_endpoint()`, `read_root()` |
| Classes | `PascalCase` | `Settings`, `WebSocketHandler` |
| Constants | `UPPER_CASE` | `DEFAULT_HOST`, `MAX_CONNECTIONS` |
| Environment Variables | `UPPER_CASE` | `LOG_LEVEL`, `APP_NAME` |
| Files | `snake_case` | `config.py`, `main.py` |

### 5. Type Hints

Always use type hints:

```python
# ✅ CORRECT
async def process_message(data: str, client_id: int) -> dict[str, Any]:
    return {"message": data, "client": client_id}

# ❌ INCORRECT - No type hints
async def process_message(data, client_id):
    return {"message": data, "client": client_id}
```

### 6. Docstrings

Use clear, concise docstrings:

```python
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for testing real-time communication.

    Accepts connections, receives messages, and echoes them back
    with a prefix. Includes comprehensive logging of connections,
    messages, and errors.
    """
```

## Docker and Deployment

### Dockerfile Pattern

The project uses a **uv-based Alpine image** for minimal size and fast builds:

```dockerfile
ARG UV_TAG="alpine"
FROM ghcr.io/astral-sh/uv:${UV_TAG}

ADD . /app
WORKDIR /app
RUN uv sync --locked  # Install from lock file

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Location:** `ws-service/Dockerfile`

### Docker Compose Pattern

```yaml
services:
  ws-service:
    build:
      context: ./ws-service
    ports:
      - "${PORT:-8000}:8000"
    env_file:
      - .env
    restart: unless-stopped
    networks:
      - app-network
```

**Location:** `docker-compose.yml`

### Development Workflow

```bash
# 1. Set up environment
cp .env.example .env

# 2. Build and start
docker-compose up --build

# 3. View logs
docker-compose logs -f ws-service

# 4. Rebuild after code changes
docker-compose up --build

# 5. Stop services
docker-compose down
```

### Adding New Services

To add a new service to docker-compose.yml:

```yaml
services:
  new-service:
    build:
      context: ./new-service
    ports:
      - "8001:8001"
    env_file:
      - .env
    networks:
      - app-network  # Connects to existing network
    depends_on:
      - ws-service
```

## Dependency Management

### Using uv

```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Sync dependencies from lock file
uv sync --locked

# Update dependencies
uv lock --upgrade
```

### pyproject.toml Structure

```toml
[project]
name = "agentic-ai-ivr-demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "fastapi[standard]>=0.121.1",
    "websockets>=15.0.1",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.0.0",
]
```

**Location:** `ws-service/pyproject.toml`

## Testing (Guidelines for Future Implementation)

### Current State
⚠️ **No test infrastructure exists yet**

### Recommended Testing Stack
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **httpx** - FastAPI test client
- **pytest-cov** - Coverage reporting

### Recommended Directory Structure
```
ws-service/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_config.py       # Configuration tests
│   ├── test_endpoints.py    # REST endpoint tests
│   └── test_websocket.py    # WebSocket tests
```

### Example Test Pattern
```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Common Tasks for AI Assistants

### Adding a New WebSocket Endpoint

1. **Add route decorator** in `main.py`:
   ```python
   @app.websocket("/ws/new_endpoint")
   async def new_websocket_endpoint(websocket: WebSocket):
   ```

2. **Follow error handling pattern**:
   ```python
   try:
       await websocket.accept()
       logger.info("Client connected to new endpoint")
       # Your logic here
   except WebSocketDisconnect:
       logger.info("Client disconnected")
   except Exception as e:
       logger.error("Error in new endpoint", exc_info=True)
   ```

3. **Add logging with context**:
   ```python
   logger.debug("Processing request", extra={
       "endpoint": "new_endpoint",
       "client_host": websocket.client.host
   })
   ```

4. **Update README.md** with endpoint documentation

### Adding a New Configuration Option

1. **Add to Settings class** in `config.py`:
   ```python
   class Settings(BaseSettings):
       new_option: str = "default_value"
   ```

2. **Update .env.example**:
   ```bash
   NEW_OPTION="default_value"
   ```

3. **Update README.md** configuration table

4. **Use in code**:
   ```python
   from config import settings
   value = settings.new_option
   ```

### Adding a New Dependency

1. **Add with uv**:
   ```bash
   cd ws-service
   uv add <package-name>
   ```

2. **Verify uv.lock updated**

3. **Rebuild Docker image**:
   ```bash
   docker-compose build
   ```

4. **Update README.md** if it's a major dependency

### Debugging

1. **Enable DEBUG logging**:
   ```bash
   # In .env
   LOG_LEVEL=DEBUG
   LOG_FORMAT=text  # Easier to read during debugging
   ```

2. **View container logs**:
   ```bash
   docker-compose logs -f ws-service
   ```

3. **Access running container**:
   ```bash
   docker-compose exec ws-service sh
   ```

4. **Check configuration**:
   ```python
   # Add temporary logging in main.py
   logger.info("Current config", extra={
       "log_level": settings.log_level,
       "environment": settings.environment
   })
   ```

## Git Workflow

### Branch Strategy
- **Main branch:** Default branch for stable code
- **Feature branches:** `claude/claude-md-<session-id>` for AI assistant work
- **Naming:** Use descriptive names: `feature/add-authentication`, `fix/websocket-timeout`

### Commit Conventions

Use conventional commit format:

```
type(scope): description

- feat: New feature
- fix: Bug fix
- refactor: Code refactoring
- chore: Maintenance tasks
- docs: Documentation changes
```

**Examples:**
```
feat(websocket): add message validation
fix(logging): correct JSON format timestamp
refactor(config): use pydantic settings
chore(deps): update fastapi to 0.121.1
docs(readme): add websocket usage examples
```

### Recent Commit History
```
cd0ad26 - refactor: update deprecated patterns
62bb1cd - feat: add logging and environment configuration
f5da5e8 - refactor: use docker compose
07e7b32 - chore: add dockerfile
f0b867b - feat: set up fastapi and ws test
```

## Security Considerations

### Current Security Posture

⚠️ **Areas Needing Enhancement:**
- No input validation on WebSocket messages
- No rate limiting
- No authentication/authorization
- No CORS configuration
- No security headers

### Recommendations for AI Assistants

When implementing security features:

1. **Input Validation:**
   ```python
   from pydantic import BaseModel, validator

   class WebSocketMessage(BaseModel):
       message: str

       @validator('message')
       def message_length(cls, v):
           if len(v) > 1000:
               raise ValueError('Message too long')
           return v
   ```

2. **Rate Limiting:**
   ```python
   # Consider: slowapi, fastapi-limiter
   from slowapi import Limiter
   ```

3. **CORS (if adding HTTP endpoints):**
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://example.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Never log sensitive data** - credentials, tokens, PII

## Performance Considerations

### Current Performance Characteristics

- **Async I/O:** Non-blocking operations via asyncio
- **Alpine Base:** Small container size (~50MB)
- **Fast Startup:** uv provides rapid dependency resolution
- **Connection Handling:** FastAPI/Uvicorn handles concurrent WebSocket connections efficiently

### Best Practices for AI Assistants

1. **Avoid blocking calls** in async handlers:
   ```python
   # ❌ INCORRECT
   time.sleep(1)

   # ✅ CORRECT
   await asyncio.sleep(1)
   ```

2. **Use connection pooling** for databases (when added)

3. **Implement message batching** for high-throughput scenarios

4. **Monitor memory usage** with logging:
   ```python
   import psutil
   logger.debug("Memory usage", extra={
       "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
   })
   ```

## Troubleshooting Guide

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Change port in .env
PORT=8001
```

#### Container Won't Start
```bash
# Check logs
docker-compose logs ws-service

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

#### Dependencies Not Installing
```bash
# Force sync from lock file
docker-compose exec ws-service uv sync --locked

# Or rebuild container
docker-compose build --no-cache
```

#### WebSocket Connection Refused
1. Check container is running: `docker-compose ps`
2. Check logs: `docker-compose logs -f ws-service`
3. Verify port mapping in docker-compose.yml
4. Test health endpoint: `curl http://localhost:8000/`

#### Environment Variables Not Loading
1. Verify `.env` file exists
2. Check `env_file` in docker-compose.yml
3. Restart containers: `docker-compose restart`
4. Check capitalization (should be `LOG_LEVEL` not `log_level`)

## Code Quality Standards

### What AI Assistants Should Maintain

1. **Type Safety**
   - All functions have type hints
   - Use Pydantic models for validation
   - Leverage Literal types for restricted values

2. **Error Handling**
   - Specific exception handling before generic
   - Always log errors with context
   - Use exc_info=True for stack traces

3. **Logging**
   - Appropriate log levels
   - Contextual extra fields
   - No sensitive data in logs

4. **Documentation**
   - Docstrings for all public functions
   - Inline comments for complex logic
   - Update README.md and CLAUDE.md for major changes

5. **Consistency**
   - Follow existing naming conventions
   - Match existing code style
   - Use established patterns (async/await, error handling)

## Quick Reference

### File Locations
| What | Where |
|------|-------|
| Application entry | `ws-service/main.py` |
| Configuration | `ws-service/config.py` |
| Dependencies | `ws-service/pyproject.toml` |
| Lock file | `ws-service/uv.lock` |
| Docker image | `ws-service/Dockerfile` |
| Orchestration | `docker-compose.yml` |
| Env template | `.env.example` |

### Key Code Locations
| Feature | File | Lines |
|---------|------|-------|
| Settings class | `config.py` | Full file |
| Logging setup | `main.py` | 13-74 |
| App lifespan | `main.py` | 76-93 |
| Health endpoint | `main.py` | 102-111 |
| WebSocket handler | `main.py` | 114-167 |

### Important Commands
```bash
# Development
docker-compose up --build        # Build and start
docker-compose logs -f           # View logs
docker-compose down              # Stop services

# Dependencies
uv add <package>                 # Add dependency
uv sync --locked                 # Install from lock

# Environment
cp .env.example .env             # Initialize config
```

## Conclusion

This codebase demonstrates **modern Python async patterns** with a focus on:
- Production-ready configuration management
- Comprehensive structured logging
- Docker containerization
- Type safety with Pydantic

When working with this code, AI assistants should:
1. ✅ Follow async/await patterns consistently
2. ✅ Use the Settings class for all configuration
3. ✅ Add contextual logging with extra fields
4. ✅ Handle WebSocket errors gracefully
5. ✅ Maintain type hints throughout
6. ✅ Update documentation for significant changes
7. ✅ Test with Docker Compose before committing

For questions or clarifications, refer to:
- **README.md** - User-facing documentation and quick start
- **This file (CLAUDE.md)** - Developer and AI assistant guide
- **Code comments** - Inline documentation for complex logic
