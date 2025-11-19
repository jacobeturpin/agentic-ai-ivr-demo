# Agentic AI IVR Demo

A WebSocket-based service for interactive voice response demonstrations using agentic AI.

## Project Structure

```
docker-compose.yml       # Docker Compose configuration
.env.example             # Example environment variables
ws-service/              # WebSocket service
    Dockerfile           # Service container definition
    main.py              # FastAPI WebSocket application
    config.py            # Configuration management
    pyproject.toml       # Python project configuration
    uv.lock              # Dependency lock file
```

## Local Development with Docker Compose

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

2. **Build the services:**
   ```bash
   docker-compose build
   ```

3. **Start the services:**
   ```bash
   docker-compose up
   ```

4. **Access the WebSocket service:**
   - WebSocket endpoint: `ws://localhost:8000/ws/test`
   - Health check: `http://localhost:8000/`

5. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Development Commands

**Rebuild and restart after code changes:**
```bash
docker-compose up --build
```

**View logs:**
```bash
docker-compose logs -f ws-service
```

**Run in detached mode:**
```bash
docker-compose up -d
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

### Available Configuration Options

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `APP_NAME` | Application name | "Agentic AI IVR Demo" | any string |
| `APP_VERSION` | Application version | "0.1.0" | any string |
| `HOST` | Server host | "0.0.0.0" | any valid host |
| `PORT` | Server port | 8000 | any valid port |
| `LOG_LEVEL` | Logging level | "INFO" | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FORMAT` | Log output format | "text" | text, json |
| `ENVIRONMENT` | Environment name | "development" | development, staging, production |
| `TWILIO_AUTH_TOKEN` | Auth token for Twilio API usage | None | valid API token as a string |

### Logging

The application supports two logging formats:

**Text Format (Human-Readable):**
```
2025-11-12 10:30:45 - main - INFO - Application starting
```

**JSON Format (Structured):**
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

To change log level or format, update your `.env` file:
```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

Or override in `docker-compose.yml`:
```yaml
environment:
  - LOG_LEVEL=DEBUG
  - LOG_FORMAT=json
```

## Testing the WebSocket Endpoint

You can test the WebSocket connection using a simple HTML client or a WebSocket testing tool:

```html
<!DOCTYPE html>
<html>
<body>
    <script>
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onopen = () => {
            console.log('Connected');
            ws.send('Hello from client');
        };
        ws.onmessage = (event) => {
            console.log('Received:', event.data);
        };
    </script>
</body>
</html>
```

## Adding Additional Services

The docker-compose setup is designed to easily accommodate additional services. Simply add new service definitions to `docker-compose.yml` and they will automatically join the `app-network`.
