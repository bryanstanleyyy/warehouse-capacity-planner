# Warehouse Capacity Planner

> Intelligent space optimization for modern warehouses

A full-stack web application for warehouse capacity planning and space optimization. Features multi-constraint allocation algorithms, visual planning tools, and comprehensive reporting.

**Project Status:** 🟢 Core features complete | 22 features implemented | ~90% complete

**Live Demo:** *Coming soon*

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

### Planned Features 📋
- [ ] Testing suite (pytest for backend, Jest for frontend)
- [ ] Production deployment guide (Docker Compose orchestration)

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

Inspired by real-world logistics and warehouse management challenges.
