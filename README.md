# Warehouse Capacity Planner

> Intelligent space optimization for modern warehouses

A full-stack web application for warehouse capacity planning and space optimization. Features multi-constraint allocation algorithms, visual planning tools, and comprehensive reporting.

## Overview

Warehouse Capacity Planner helps logistics managers and warehouse operators optimize space utilization by:
- Analyzing inventory requirements and warehouse capacity
- Allocating items to storage zones using multi-constraint optimization
- Accounting for real-world space utilization factors
- Generating detailed allocation reports and visualizations
- Supporting climate-controlled zones and special handling requirements

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
- **Comprehensive Reporting**: Generate detailed HTML and PDF reports with item manifests and capacity analysis
- **Priority-Based Loading**: Configure loading priorities by category to ensure critical items are allocated first

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
- ReportLab for PDF generation

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
git clone https://github.com/YOUR_USERNAME/warehouse-capacity-planner.git
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

1. **Create a Warehouse**: Define your warehouse with storage zones (area, height, floor strength)
2. **Upload Inventory**: Import inventory data from an Excel file
3. **Configure Parameters**: Set Space Utilization Factor (BSF) and priorities
4. **Run Allocation**: Execute the allocation algorithm to optimize space usage
5. **Review Results**: Analyze utilization charts and allocation details
6. **Generate Reports**: Create detailed HTML or PDF reports

## Algorithm

The core allocation engine uses a **height-first optimization strategy**:

1. Sort items by height (tallest first)
2. For each item, iterate through zones:
   - Check height clearance
   - Calculate required area: `base_area × (1 + BSF)`
   - Validate floor strength (PSF)
   - Check available capacity
3. Allocate if all constraints pass
4. Track failures with detailed reasons

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
- `POST /api/v1/inventory/upload` - Upload inventory
- `POST /api/v1/allocation/analyze` - Run allocation
- `POST /api/v1/reports/generate` - Generate report

## Screenshots

*Coming soon - screenshots will be added as features are implemented*

## Development Roadmap

### Completed Features
- [x] Project setup and structure
- [x] Database models and migrations (SQLAlchemy with Flask-Migrate)
- [x] Warehouse management API (Full CRUD with Swagger docs)
- [x] Warehouse management UI (React with Material-UI, full CRUD operations)
- [x] Inventory upload API (Excel parsing with pandas)
- [x] Frontend routing and layout (React Router with responsive navigation)
- [x] API client setup (Axios with TypeScript types)

### In Progress
- [ ] Core allocation algorithm (height-first, multi-constraint optimization)
- [ ] Inventory upload UI (File upload component with validation)
- [ ] Zone management UI (Add/edit zones for warehouses)

### Planned Features
- [ ] Allocation API and service layer
- [ ] Allocation planner UI (control panel + results display)
- [ ] Visualization components (Chart.js, Recharts, D3.js)
- [ ] Report generation (HTML/PDF export)
- [ ] Advanced features (climate control, special handling, priority-based loading)
- [ ] Testing suite (pytest for backend, Jest for frontend)
- [ ] Production deployment (Docker Compose)

## Contributing

This is a portfolio project, but suggestions and feedback are welcome! Feel free to open an issue for discussion.

## License

MIT License - see LICENSE file for details

## Author

**Bryan** - [GitHub Profile](https://github.com/YOUR_USERNAME)

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
