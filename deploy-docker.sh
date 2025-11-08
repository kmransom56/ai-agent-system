#!/bin/bash
# AI Agent System - Docker Deployment Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_header "Creating Directories"

    mkdir -p logs cache reports config

    print_success "Directories created"
}

# Build Docker images
build_images() {
    print_header "Building Docker Images"

    docker-compose build

    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_header "Starting AI Agent Services"

    docker-compose up -d

    print_success "Services started"
}

# Show status
show_status() {
    print_header "Service Status"

    docker-compose ps

    echo ""
    print_header "Container Logs (last 10 lines)"
    docker-compose logs --tail=10
}

# Show access information
show_access_info() {
    print_header "Access Information"

    echo -e "${GREEN}🎯 AI Agent Dashboard:${NC}"
    echo "   http://localhost:11050"
    echo ""
    echo -e "${GREEN}📊 Available Endpoints:${NC}"
    echo "   http://localhost:11050/api/status   - Agent status"
    echo "   http://localhost:11050/api/metrics  - System metrics"
    echo "   http://localhost:11050/api/reports  - Recent reports"
    echo ""
    echo -e "${GREEN}📁 Data Locations:${NC}"
    echo "   ./logs/     - Agent logs and metrics"
    echo "   ./cache/    - Agent context and state"
    echo "   ./reports/  - Generated reports"
}

# Main deployment flow
main() {
    print_header "AI Agent System - Docker Deployment"

    # Check prerequisites
    check_docker

    # Create directories
    create_directories

    # Build images
    build_images

    # Start services
    start_services

    # Wait for services to be ready
    echo ""
    print_warning "Waiting for services to start (10 seconds)..."
    sleep 10

    # Show status
    show_status

    # Show access information
    echo ""
    show_access_info

    echo ""
    print_success "Deployment complete!"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  docker-compose logs -f             # Follow logs"
    echo "  docker-compose ps                  # Check status"
    echo "  docker-compose restart            # Restart services"
    echo "  docker-compose down               # Stop services"
    echo "  docker-compose down -v            # Stop and remove volumes"
}

# Parse command line arguments
case "${1:-}" in
    start)
        start_services
        show_status
        ;;
    stop)
        print_header "Stopping Services"
        docker-compose down
        print_success "Services stopped"
        ;;
    restart)
        print_header "Restarting Services"
        docker-compose restart
        show_status
        ;;
    status)
        show_status
        ;;
    logs)
        docker-compose logs -f "${2:-}"
        ;;
    build)
        build_images
        ;;
    clean)
        print_header "Cleaning Up"
        print_warning "This will remove all containers, volumes, and images"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker-compose rm -f
            print_success "Cleanup complete"
        else
            print_warning "Cleanup cancelled"
        fi
        ;;
    *)
        main
        ;;
esac
