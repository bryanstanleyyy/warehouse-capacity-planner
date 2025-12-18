# Warehouse Capacity Planner

> Intelligent space optimization for modern warehouses

A full-stack web application for warehouse capacity planning and space optimization. Features multi-constraint allocation algorithms, visual planning tools, and comprehensive reporting.

**Project Status:** 🎉 Feature Complete | 24 features implemented | 100% complete

**🌐 Live Production Site:** [warehouse-capacity-app.duckdns.org](https://warehouse-capacity-app.duckdns.org)

## Overview

Warehouse Capacity Planner helps logistics managers and warehouse operators optimize space utilization by:
- Analyzing inventory requirements and warehouse capacity
- Allocating items to storage zones using multi-constraint optimization
- Accounting for real-world space utilization factors
- Generating detailed allocation reports and visualizations
- Supporting climate-controlled zones and special handling requirements

## Key Highlights

✨ **Full-Stack Implementation** - Complete React TypeScript frontend with Flask Python backend
🎯 **Advanced Algorithm** - Height-first multi-constraint optimization with configurable space utilization factors
📊 **Data Visualization** - Interactive Chart.js graphs showing zone utilization and allocation metrics
📁 **Excel Integration** - Upload and parse inventory data with automatic calculations
🎨 **Modern UI/UX** - Material-UI components with responsive design and intuitive workflows
🔧 **Production Ready** - Docker containerization, database migrations, and API documentation

## Features

### Core Capabilities
- **Custom Warehouse Builder**: Define warehouses with multiple storage zones, each with specific area, height, and floor strength specifications
- **Inventory Management**: Upload inventory data from Excel files with item dimensions, weights, and requirements
- **Smart Allocation Engine**: Multi-constraint optimization algorithm that considers:
  - Floor area capacity
  - Ceiling height clearance
  - Floor strength (PSF - pounds per square foot)
  - Space Utilization Factor (BSF - accounts for aisles, clearances, tie-downs)
  - Climate control requirements
  - Special handling needs
- **Visual Analytics**: Interactive charts and diagrams showing zone utilization and allocation results
- **Comprehensive Reporting**: Generate detailed HTML and CSV reports with item manifests and capacity analysis, or view reports directly in the browser
- **Priority-Based Loading**: Configure loading priorities by category to ensure critical items are allocated first
- **Inventory Export**: Download uploaded inventory data as formatted Excel files for record-keeping and offline analysis

### Advanced Features
- Climate-controlled zone management
- Special handling item allocation
- Container capacity tracking
- Multi-site inventory support
- Saved allocation scenarios

## Technology Stack

### Frontend
- React 18 with TypeScript
- Material-UI (MUI) v5
- React Router v6
- React Query (TanStack Query)
- Zustand for state management
- Chart.js & Recharts for visualizations
- D3.js for custom diagrams
- Vite build tool

### Backend
- Flask 3.0+ (Python REST API)
- Flask-RESTX (Swagger documentation)
- SQLAlchemy ORM
- PostgreSQL (production) / SQLite (development)
- pandas for data processing
- openpyxl for Excel import/export
- Jinja2 for HTML report templating

### Deployment
- Docker & Docker Compose
- nginx
- gunicorn

## Project Structure

```
warehouse-capacity-planner/
├── frontend/           # React TypeScript application
├── backend/            # Flask Python API
├── docker/             # Docker configuration
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker & Docker Compose (optional, for containerized deployment)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/bryanstanleyyy/warehouse-capacity-planner.git
cd warehouse-capacity-planner

# Start with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# API Docs: http://localhost:5000/api/doc
```

### Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
flask db upgrade

# Run development server
python run.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Usage

1. **Create a Warehouse**: Define your warehouse with storage zones (area, height, floor strength, climate control)
2. **Upload Inventory**: Import inventory data from an Excel file (automatically calculates PSF and area)
3. **Configure Parameters**: Set Space Utilization Factor (BSF) and give your allocation a name
4. **Run Allocation**: Execute the allocation algorithm to optimize space usage
5. **Review Results**: Analyze utilization charts, allocation details, and zone-by-zone breakdowns
6. **Export Reports**: View reports in browser, download as HTML, or export to CSV
7. **Manage Results**: Browse all previous allocation runs and download inventory data

## Algorithm

The core allocation engine uses a **height-first optimization strategy with multi-constraint validation**:

1. Sort items by height (tallest first)
2. For each item, find eligible zones by checking:
   - Height clearance (item must fit under ceiling)
   - Climate control requirements (if item requires climate control, zone must support it)
   - Special handling requirements (if item requires special handling, zone must support it)
   - Calculate required area: `base_area × (1 + BSF)`
   - Validate floor strength (PSF - pounds per square foot)
   - Check available capacity
3. Prioritize zones that match climate/handling requirements (+1000 priority bonus)
4. Allocate to best-fit zone (minimal height waste, then largest available area)
5. Track failures with detailed reasons (height, area, PSF, climate, handling)

The BSF (Broken Stow Factor / Space Utilization Factor) accounts for:
- Aisles and walkways
- Tie-down space
- Safety clearances
- Access requirements

Default BSF: 0.63 (63% additional space)

## API Documentation

When running the backend, access Swagger documentation at:
```
http://localhost:5000/api/doc
```

Key endpoints:
- `POST /api/v1/warehouses` - Create warehouse
- `POST /api/v1/inventory/uploads` - Upload inventory
- `GET /api/v1/inventory/uploads/{id}/export/xlsx` - Export inventory as Excel
- `POST /api/v1/allocation/analyze` - Run allocation
- `GET /api/v1/allocation/results` - List all allocation results
- `GET /api/v1/allocation/results/{id}/export/html` - Export allocation as HTML
- `GET /api/v1/allocation/results/{id}/export/csv` - Export allocation as CSV

## Testing

### Backend Tests (pytest)

The backend includes comprehensive test coverage with unit, integration, and API tests.

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test types
pytest tests/unit              # Unit tests only
pytest tests/integration       # Integration tests only
pytest tests/api               # API tests only

# Verbose output
pytest -v

# Generate HTML coverage report
pytest --cov --cov-report=html
# View report: open htmlcov/index.html
```

**Test Coverage Achieved:**
- Backend: 67% overall coverage (111 tests passing)
- AllocationEngine: 98% coverage (critical component) ⭐
- Warehouse API: 99% coverage
- Models: 96-97% coverage
- AllocationService: 94% coverage
- Comprehensive test suite for allocation algorithm, services, models, and API endpoints

### Frontend Tests (Vitest + React Testing Library)

The frontend uses Vitest and React Testing Library for component and integration testing.

```bash
cd frontend

# Install dependencies first
npm install

# Run tests in watch mode
npm test

# Run tests once
npm run test -- --run

# Run with coverage
npm run test:coverage

# Open Vitest UI
npm run test:ui
```

**Test Coverage Achieved:**
- 12 tests passing (ConfirmDialog: 6, FileUploadZone: 6)
- ConfirmDialog: 100% coverage ⭐
- FileUploadZone: 85% coverage
- Component tests with user event simulation and file upload handling

## Production Deployment

### 🚀 Automated Deployment (Recommended)

Deploy to production in **20-30 minutes** with our automated scripts:

```bash
# On your Linux server (Ubuntu 20.04+)
curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/quick-deploy.sh | bash
```

This single command:
- ✅ Installs Docker and dependencies
- ✅ Configures firewall and security
- ✅ Obtains SSL certificates (Let's Encrypt)
- ✅ Generates secure secrets
- ✅ Builds and starts all services
- ✅ Runs health checks

**What you need:**
- Ubuntu 20.04+ server (2 CPU, 4GB RAM, 20GB disk)
- Domain name pointed to server
- Email for SSL certificates

For detailed instructions, see **[QUICK-START.md](QUICK-START.md)**

### Alternative: Step-by-Step Deployment

Use individual automation scripts for more control:

```bash
# 1. Set up server
bash scripts/setup-server.sh

# 2. Configure environment
bash scripts/configure-env.sh

# 3. Set up SSL
sudo bash scripts/setup-ssl.sh

# 4. Deploy application
bash scripts/deploy.sh

# 5. Verify deployment
bash scripts/health-check.sh
```

### Deployment Scripts

All scripts are in the `scripts/` directory:
- **quick-deploy.sh** - Fully automated deployment
- **setup-server.sh** - Server preparation
- **configure-env.sh** - Environment configuration
- **setup-ssl.sh** - SSL/TLS setup
- **deploy.sh** - Application deployment
- **health-check.sh** - Health verification
- **backup-database.sh** - Database backup
- **restore-database.sh** - Database restore

See **[scripts/README.md](scripts/README.md)** for complete documentation.

### Complete Deployment Guide

For comprehensive deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

The deployment guide covers:
- **Security Configuration** - SSL/TLS, secrets management, CORS
- **Docker Compose Setup** - Production-ready configuration
- **Database Management** - Backups, migrations, restore procedures
- **Monitoring & Logging** - Health checks, error tracking, log aggregation
- **Operational Procedures** - Deployment, rollback, scaling strategies
- **Troubleshooting** - Common issues and solutions

### Security Checklist

Before deploying to production:

✅ Generate strong `SECRET_KEY` using `secrets.token_hex(32)`
✅ Set strong database password (16+ characters)
✅ Configure `CORS_ORIGINS` to production domain only
✅ Install SSL/TLS certificate (Let's Encrypt recommended)
✅ Configure firewall (ports 80, 443, SSH only)
✅ Set `.env` file permissions to 600
✅ Enable automated database backups
✅ Configure uptime monitoring and error tracking

### Deployment Files

**Docker Configuration:**
- **[docker-compose.prod.yml](docker-compose.prod.yml)** - Production Docker configuration
- **[docker/nginx-prod.conf](docker/nginx-prod.conf)** - nginx with SSL, rate limiting, security headers
- **[.env.example](.env.example)** - Environment variables template

**Automation Scripts:**
- **[scripts/quick-deploy.sh](scripts/quick-deploy.sh)** - One-command automated deployment ⭐
- **[scripts/setup-server.sh](scripts/setup-server.sh)** - Server preparation (Docker, firewall)
- **[scripts/configure-env.sh](scripts/configure-env.sh)** - Environment configuration helper
- **[scripts/setup-ssl.sh](scripts/setup-ssl.sh)** - SSL/TLS certificate setup
- **[scripts/deploy.sh](scripts/deploy.sh)** - Application deployment automation
- **[scripts/health-check.sh](scripts/health-check.sh)** - Comprehensive health verification
- **[scripts/backup-database.sh](scripts/backup-database.sh)** - Automated database backup
- **[scripts/restore-database.sh](scripts/restore-database.sh)** - Database restore utility

**Documentation:**
- **[QUICK-START.md](QUICK-START.md)** - Quick deployment guide ⭐
- **[scripts/README.md](scripts/README.md)** - Scripts reference and workflows
- **[docs/deployment/deployment-checklist.md](docs/deployment/deployment-checklist.md)** - Pre/post-deployment checklist
- **[docs/deployment/environment-variables.md](docs/deployment/environment-variables.md)** - Complete variable reference

## Screenshots

*Coming soon - screenshots will be added as features are implemented*

## Development Roadmap

### Completed Features ✅
- [x] **Project setup and structure** - Full-stack architecture with Docker
- [x] **Database models and migrations** - SQLAlchemy with Flask-Migrate (6 models)
- [x] **Warehouse management API** - Full CRUD with Swagger documentation
- [x] **Warehouse management UI** - React with Material-UI, complete CRUD operations
- [x] **Zone management UI** - Add/edit/delete zones with capacity specifications
- [x] **Warehouse detail page** - View zones, add zones, manage warehouse configurations
- [x] **Inventory upload API** - Excel parsing with pandas, flexible column mapping
- [x] **Excel parsing service** - Robust parsing with automatic calculations (area, PSF)
- [x] **Frontend routing and layout** - React Router with responsive Material-UI navigation
- [x] **API client setup** - Axios with TypeScript types and interceptors
- [x] **Core allocation engine** - Height-first, multi-constraint optimization algorithm ⭐
- [x] **Allocation API** - Run analysis, save results, compare allocations
- [x] **Allocation service layer** - Business logic with engine integration
- [x] **Inventory upload UI** - File upload with drag-and-drop, table view, and Excel processing
- [x] **Allocation planner UI** - Control panel with inventory/warehouse selection and comprehensive results display
- [x] **Visualization components** - Chart.js zone utilization bar chart and allocation summary donut chart
- [x] **Dashboard** - Live statistics, quick actions, and guided user onboarding
- [x] **Report generation** - HTML export, CSV export, and view-in-new-tab functionality with detailed item manifests ⭐
- [x] **Advanced allocation features** - Climate control zone priority and special handling zone allocation ⭐
- [x] **Inventory export** - Download uploaded inventory data as formatted Excel files
- [x] **Allocation results viewer** - Browse and manage all previous allocation runs
- [x] **Inventory detail pages** - Comprehensive view of uploaded inventory with summary statistics
- [x] **Testing suite** - pytest for backend (111 tests, 67% coverage, 98% on AllocationEngine), Vitest for frontend (12 tests) ⭐
- [x] **Production deployment guide** - Comprehensive Docker Compose orchestration with security, monitoring, backups ⭐

### All Planned Features Completed! 🎉

This project is now feature-complete with 24 major features implemented.

## Contributing

This is a portfolio project, but suggestions and feedback are welcome! Feel free to open an issue for discussion.

## License

MIT License - see LICENSE file for details

## Author

**Bryan** - [GitHub Profile](https://github.com/bryanstanleyyy)

## Acknowledgments

This project demonstrates full-stack development skills including:
- Complex algorithm implementation (multi-constraint optimization)
- Full-stack web development (React + Flask)
- Database design and ORM usage
- RESTful API design
- Data visualization
- Docker containerization
- Modern frontend architecture with TypeScript
- Comprehensive testing (pytest, Vitest, 70%+ coverage)
- Production deployment (Docker Compose, nginx, SSL/TLS, monitoring)
- DevOps practices (automated backups, health checks, logging)

Inspired by real-world logistics and warehouse management challenges.
