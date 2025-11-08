# Docker Deployment Guide
## AI Agent System Containerization

---

## Why Docker is Efficient for This System

### 1. **Dependency Isolation**
- All Python packages (Flask, pandas, schedule, etc.) contained in container
- No conflicts with host system Python installations
- Consistent Python 3.13.2 environment across all deployments
- System dependencies (curl, etc.) managed within container

### 2. **Easy Deployment**
- **Single Command Deployment**: `./deploy-docker.sh`
- **Zero Configuration**: Works out of the box
- **Cross-Platform**: Works on any machine with Docker
- **No Virtual Environment Management**: No need for uv/pip/venv commands

### 3. **Resource Management**
```yaml
# Control CPU and memory per service
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### 4. **Scaling Capabilities**
```bash
# Scale sales agent to 3 instances
docker-compose up -d --scale sales-agent=3

# Scale dashboard for high traffic
docker-compose up -d --scale dashboard=2
```

### 5. **Service Isolation**
- Orchestrator runs in separate container from dashboard
- Individual agents can run as separate containers
- Failures in one service don't affect others
- Easy to restart specific services

### 6. **Data Persistence**
```yaml
volumes:
  - ./logs:/app/logs          # Persistent logs
  - ./cache:/app/cache        # Agent state preserved
  - ./reports:/app/reports    # Reports accessible on host
```

### 7. **Health Monitoring**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11050/api/status"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 8. **Simple Updates**
```bash
# Pull latest code
git pull

# Rebuild and restart
./deploy-docker.sh build
./deploy-docker.sh restart
```

---

## Docker vs Traditional Deployment

| Feature | Docker | Traditional Python |
|---------|--------|-------------------|
| **Setup Time** | 2 minutes | 10-15 minutes |
| **Dependency Management** | Automatic | Manual (uv/pip) |
| **Environment Isolation** | Complete | Virtual env only |
| **Scaling** | Built-in | Complex/manual |
| **Resource Control** | Built-in | OS-level only |
| **Health Monitoring** | Built-in | Manual scripts |
| **Multi-Machine Deploy** | Copy files + run | Full setup each time |
| **Rollback** | One command | Manual restore |

---

## Architecture

### Container Structure

```
┌─────────────────────────────────────────────┐
│           Docker Network: ai-agent-network   │
│                                              │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │   Orchestrator   │  │    Dashboard    │ │
│  │   Container      │  │    Container    │ │
│  │                  │  │                 │ │
│  │ - Run agents     │  │ - Flask app     │ │
│  │ - Schedule tasks │  │ - Web UI        │ │
│  │ - Generate       │  │ - REST API      │ │
│  │   reports        │  │ - Port 11050    │ │
│  └──────────────────┘  └─────────────────┘ │
│           │                      │          │
│           └──────────┬───────────┘          │
│                      │                      │
│                 Volume Mounts               │
│                      │                      │
└──────────────────────┼──────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │   Host File System         │
         │                            │
         │  ./logs/    (read/write)   │
         │  ./cache/   (read/write)   │
         │  ./reports/ (read/write)   │
         │  ./config/  (read-only)    │
         └────────────────────────────┘
```

### Multi-Stage Build Process

```dockerfile
# Stage 1: Builder
FROM python:3.13.2-slim as builder
- Install uv
- Create virtual environment
- Install dependencies
- Optimize for size

# Stage 2: Runtime
FROM python:3.13.2-slim
- Copy virtual environment
- Copy application code
- Setup runtime environment
- Configure health checks
```

**Benefits:**
- Smaller final image size
- Faster deployment
- Improved security (no build tools in runtime)
- Layer caching for faster rebuilds

---

## Performance Characteristics

### Resource Usage

**Orchestrator Container:**
- **CPU**: 1-2 cores
- **Memory**: 1-2 GB
- **Disk I/O**: Low (logs/cache writes)

**Dashboard Container:**
- **CPU**: 0.5-1 core
- **Memory**: 512 MB - 1 GB
- **Network**: Moderate (web interface)

**Total System:**
- **CPU**: 2-3 cores
- **Memory**: 2-3 GB
- **Disk**: ~500 MB (image) + data volumes

### Startup Time
- **Cold Start** (first run): ~30 seconds
- **Warm Start** (with cached images): ~5 seconds
- **Individual Service Restart**: ~2 seconds

### Network Performance
- **Inter-Container**: Native Docker network (fast)
- **Dashboard Access**: Standard HTTP (no overhead)
- **Volume I/O**: Near-native performance

---

## Advanced Configurations

### 1. Production Configuration

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    restart: always
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
      placement:
        constraints:
          - node.role == worker
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  dashboard:
    build: .
    restart: always
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      resources:
        limits:
          cpus: '1'
          memory: 1G
    healthcheck:
      interval: 15s
      timeout: 5s
      retries: 5
```

### 2. Development Configuration

**docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app  # Mount source code for live reload
    environment:
      - DEBUG=1
      - PYTHONDONTWRITEBYTECODE=1
    command: python orchestrator.py --debug

  dashboard:
    volumes:
      - .:/app
    environment:
      - FLASK_DEBUG=1
      - FLASK_ENV=development
    ports:
      - "11050:11050"
      - "5678:5678"  # debugpy port
```

### 3. High-Availability Configuration

**docker-compose.ha.yml:**
```yaml
version: '3.8'

services:
  orchestrator:
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  dashboard:
    deploy:
      replicas: 3
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ai_agents
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

---

## Monitoring and Debugging

### Container Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f dashboard

# Last N lines
docker-compose logs --tail=100 orchestrator

# Since specific time
docker-compose logs --since 30m dashboard

# Filter logs
docker-compose logs | grep ERROR
```

### Container Statistics

```bash
# Real-time resource usage
docker stats

# Specific containers
docker stats ai-agent-orchestrator ai-agent-dashboard

# Format output
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Container Inspection

```bash
# Detailed container info
docker inspect ai-agent-orchestrator

# Network details
docker network inspect ai-agents_ai-agent-network

# Volume details
docker volume inspect ai-agents_logs
```

### Shell Access

```bash
# Access container shell
docker exec -it ai-agent-orchestrator bash

# Run specific command
docker exec ai-agent-orchestrator ls -la /app/logs

# Check Python environment
docker exec ai-agent-orchestrator python --version
docker exec ai-agent-orchestrator pip list
```

---

## Troubleshooting

### Common Issues

**Issue: Container won't start**
```bash
# Check logs
docker-compose logs orchestrator

# Check container status
docker-compose ps

# Verify configuration
docker-compose config

# Check for port conflicts
netstat -tuln | grep 11050
```

**Issue: High memory usage**
```bash
# Check current usage
docker stats

# Adjust limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G  # Reduce from 2G
```

**Issue: Slow performance**
```bash
# Check system resources
docker system df

# Clean up unused resources
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

**Issue: Volume permission errors**
```bash
# Check volume permissions
ls -la logs/ cache/ reports/

# Fix permissions
sudo chown -R $USER:$USER logs cache reports

# Restart containers
docker-compose restart
```

---

## Best Practices

### 1. Security

```bash
# Don't commit secrets to .env
echo ".env" >> .gitignore

# Use Docker secrets for production
docker secret create db_password ./secrets/db_pass.txt

# Run as non-root user in container
USER agent:agent
```

### 2. Data Backup

```bash
# Backup volumes
docker run --rm \
  -v ai-agents_logs:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/logs-backup.tar.gz /data

# Backup configuration
tar czf config-backup.tar.gz config/ .env
```

### 3. Updates

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart with zero downtime
docker-compose up -d --no-deps --build orchestrator
docker-compose up -d --no-deps --build dashboard
```

### 4. Monitoring

```bash
# Set up health check endpoint monitoring
curl http://localhost:11050/api/status

# Use external monitoring tools
# - Prometheus for metrics
# - Grafana for dashboards
# - Alertmanager for notifications
```

---

## Migration from Traditional Deployment

### Step 1: Backup Current Setup

```bash
# Backup data
cp -r logs logs.backup
cp -r cache cache.backup
cp -r reports reports.backup
cp config/agents_config.yaml config/agents_config.yaml.backup
```

### Step 2: Stop Current Services

```bash
# Stop systemd service
sudo systemctl stop ai-agent-orchestrator

# Or kill processes
pkill -f orchestrator.py
pkill -f agent_dashboard.py
```

### Step 3: Deploy Docker

```bash
# Quick deploy
./deploy-docker.sh

# Verify migration
curl http://localhost:11050/api/status
```

### Step 4: Validate

```bash
# Check logs match expectations
docker-compose logs -f

# Verify reports are generating
ls -lh reports/

# Check metrics
tail -f logs/metrics.jsonl
```

---

## Comparison: Docker vs Traditional

### Storage Efficiency

**Traditional:**
- Python: ~500 MB
- Virtual environment: ~200 MB
- Dependencies: ~300 MB
- **Total: ~1 GB per installation**

**Docker:**
- Base image (shared): ~150 MB
- Dependencies layer: ~200 MB
- Application layer: ~50 MB
- **Total: ~400 MB per deployment**
- **Shared base across multiple containers**

### Deployment Speed

**Traditional:**
```bash
# ~15 minutes
git clone
python3 -m venv
pip install -r requirements.txt
configure environment
test setup
start services
```

**Docker:**
```bash
# ~2 minutes
./deploy-docker.sh
# Done
```

### Maintenance Overhead

**Traditional:**
- Update Python manually
- Update dependencies manually
- Monitor processes manually
- Configure autostart manually
- **~1 hour/month**

**Docker:**
- Update with rebuild
- Dependencies in Dockerfile
- Health checks built-in
- Restart policy configured
- **~10 minutes/month**

---

## Integration with Existing Infrastructure

### 1. With MCP Servers

```yaml
services:
  orchestrator:
    volumes:
      - /opt/mcp-servers:/mcp-servers:ro
    environment:
      - MCP_SERVERS_PATH=/mcp-servers
```

### 2. With Existing Monitoring

```yaml
services:
  orchestrator:
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://monitoring.example.com:514"
```

### 3. With Load Balancer

```yaml
services:
  dashboard:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`agents.example.com`)"
```

---

## Conclusion

**Docker is highly efficient for the AI Agent System because:**

1. ✅ **Fast deployment** - 2 minutes vs 15 minutes traditional
2. ✅ **Isolated environment** - No conflicts with host system
3. ✅ **Easy scaling** - Built-in horizontal scaling
4. ✅ **Resource control** - CPU/memory limits per service
5. ✅ **Health monitoring** - Automatic restart on failures
6. ✅ **Simple updates** - Rebuild and restart in seconds
7. ✅ **Portable** - Works on any Docker host
8. ✅ **Production-ready** - Built-in logging, health checks, restart policies

**Recommended for:**
- Production deployments
- Multi-machine setups
- CI/CD pipelines
- Teams with varying environments
- Scaling to multiple instances

**Use traditional deployment for:**
- Local development with hot reload
- Single-user simple testing
- Systems without Docker available
