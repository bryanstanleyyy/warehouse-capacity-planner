"""API blueprint."""
from flask import Blueprint
from flask_restx import Api

# Create blueprint
api_bp = Blueprint('api', __name__)

# Create API with documentation
api = Api(
    api_bp,
    title='Warehouse Capacity Planner API',
    version='1.0',
    description='REST API for warehouse capacity planning and space optimization',
    doc='/doc',  # Swagger documentation at /api/v1/doc
    ordered=True
)

# Namespaces will be added here as they are created
# from app.api.warehouses import ns as warehouses_ns
# from app.api.inventory import ns as inventory_ns
# from app.api.allocation import ns as allocation_ns
# from app.api.reports import ns as reports_ns
#
# api.add_namespace(warehouses_ns, path='/warehouses')
# api.add_namespace(inventory_ns, path='/inventory')
# api.add_namespace(allocation_ns, path='/allocation')
# api.add_namespace(reports_ns, path='/reports')
