# Agentic AI IVR Demo

A WebSocket-based service for interactive voice response demonstrations using agentic AI.

## Project Structure

```
docker-compose.yml       # Docker Compose configuration
ws-service/              # WebSocket service
    Dockerfile           # Service container definition
    main.py              # FastAPI WebSocket application
    pyproject.toml       # Python project configuration
    uv.lock              # Dependency lock file
```

## Local Development with Docker Compose

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. **Build the services:**
   ```bash
   docker-compose build
   ```

2. **Start the services:**
   ```bash
   docker-compose up
   ```

3. **Access the WebSocket service:**
   - WebSocket endpoint: `ws://localhost:8000/ws`
   - Health check: `http://localhost:8000/`

4. **Stop the services:**
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
