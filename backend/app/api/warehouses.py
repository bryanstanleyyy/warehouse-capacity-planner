"""Warehouse API endpoints."""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.extensions import db
from app.models import Warehouse, Zone

# Create namespace
ns = Namespace('warehouses', description='Warehouse operations')

# Define API models for documentation
zone_model = ns.model('Zone', {
    'id': fields.Integer(readonly=True, description='Zone ID'),
    'warehouse_id': fields.Integer(required=True, description='Warehouse ID'),
    'name': fields.String(required=True, description='Zone name'),
    'zone_order': fields.Integer(description='Display order'),
    'area': fields.Float(required=True, description='Zone area (sq ft)'),
    'height': fields.Float(required=True, description='Zone height (ft)'),
    'strength': fields.Float(description='Floor strength (PSF)'),
    'volume': fields.Float(description='Zone volume (cu ft)'),
    'climate_controlled': fields.Boolean(description='Climate controlled'),
    'temperature_min': fields.Float(description='Minimum temperature (°F)'),
    'temperature_max': fields.Float(description='Maximum temperature (°F)'),
    'special_handling': fields.Boolean(description='Special handling required'),
    'container_capacity': fields.Integer(description='Container capacity'),
    'is_weather_zone': fields.Boolean(description='Outdoor storage zone'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

warehouse_model = ns.model('Warehouse', {
    'id': fields.Integer(readonly=True, description='Warehouse ID'),
    'name': fields.String(required=True, description='Warehouse name'),
    'warehouse_type': fields.String(description='Warehouse type'),
    'description': fields.String(description='Warehouse description'),
    'total_area': fields.Float(description='Total area (sq ft)'),
    'total_volume': fields.Float(description='Total volume (cu ft)'),
    'is_custom': fields.Boolean(description='Custom warehouse'),
    'zone_count': fields.Integer(readonly=True, description='Number of zones'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Update timestamp')
})

warehouse_with_zones = ns.model('WarehouseWithZones', {
    'id': fields.Integer(readonly=True, description='Warehouse ID'),
    'name': fields.String(required=True, description='Warehouse name'),
    'warehouse_type': fields.String(description='Warehouse type'),
    'description': fields.String(description='Warehouse description'),
    'total_area': fields.Float(description='Total area (sq ft)'),
    'total_volume': fields.Float(description='Total volume (cu ft)'),
    'is_custom': fields.Boolean(description='Custom warehouse'),
    'zone_count': fields.Integer(readonly=True, description='Number of zones'),
    'zones': fields.List(fields.Nested(zone_model)),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Update timestamp')
})

warehouse_input = ns.model('WarehouseInput', {
    'name': fields.String(required=True, description='Warehouse name'),
    'warehouse_type': fields.String(description='Warehouse type'),
    'description': fields.String(description='Warehouse description'),
    'is_custom': fields.Boolean(description='Custom warehouse', default=True)
})

zone_input = ns.model('ZoneInput', {
    'name': fields.String(required=True, description='Zone name'),
    'zone_order': fields.Integer(description='Display order'),
    'area': fields.Float(required=True, description='Zone area (sq ft)'),
    'height': fields.Float(required=True, description='Zone height (ft)'),
    'strength': fields.Float(description='Floor strength (PSF)'),
    'climate_controlled': fields.Boolean(description='Climate controlled', default=False),
    'temperature_min': fields.Float(description='Minimum temperature (°F)'),
    'temperature_max': fields.Float(description='Maximum temperature (°F)'),
    'special_handling': fields.Boolean(description='Special handling required', default=False),
    'container_capacity': fields.Integer(description='Container capacity', default=0),
    'is_weather_zone': fields.Boolean(description='Outdoor storage zone', default=False)
})


@ns.route('')
class WarehouseList(Resource):
    """Warehouse list operations."""

    @ns.doc('list_warehouses')
    @ns.marshal_list_with(warehouse_model)
    def get(self):
        """List all warehouses."""
        warehouses = Warehouse.query.all()
        return [w.to_dict() for w in warehouses]

    @ns.doc('create_warehouse')
    @ns.expect(warehouse_input)
    @ns.marshal_with(warehouse_model, code=201)
    def post(self):
        """Create a new warehouse."""
        data = request.json

        # Check if warehouse name already exists
        if Warehouse.query.filter_by(name=data['name']).first():
            ns.abort(400, f"Warehouse with name '{data['name']}' already exists")

        warehouse = Warehouse(
            name=data['name'],
            warehouse_type=data.get('warehouse_type'),
            description=data.get('description'),
            is_custom=data.get('is_custom', True)
        )

        db.session.add(warehouse)
        db.session.commit()

        return warehouse.to_dict(), 201


@ns.route('/<int:warehouse_id>')
@ns.param('warehouse_id', 'Warehouse identifier')
class WarehouseResource(Resource):
    """Warehouse operations."""

    @ns.doc('get_warehouse')
    @ns.marshal_with(warehouse_with_zones)
    def get(self, warehouse_id):
        """Get warehouse by ID."""
        warehouse = Warehouse.query.get_or_404(warehouse_id, description='Warehouse not found')
        return warehouse.to_dict(include_zones=True)

    @ns.doc('update_warehouse')
    @ns.expect(warehouse_input)
    @ns.marshal_with(warehouse_model)
    def put(self, warehouse_id):
        """Update a warehouse."""
        warehouse = Warehouse.query.get_or_404(warehouse_id, description='Warehouse not found')
        data = request.json

        # Check if new name conflicts with existing warehouse
        if data.get('name') and data['name'] != warehouse.name:
            existing = Warehouse.query.filter_by(name=data['name']).first()
            if existing:
                ns.abort(400, f"Warehouse with name '{data['name']}' already exists")

        warehouse.name = data.get('name', warehouse.name)
        warehouse.warehouse_type = data.get('warehouse_type', warehouse.warehouse_type)
        warehouse.description = data.get('description', warehouse.description)

        db.session.commit()
        return warehouse.to_dict()

    @ns.doc('delete_warehouse')
    @ns.response(204, 'Warehouse deleted')
    def delete(self, warehouse_id):
        """Delete a warehouse."""
        warehouse = Warehouse.query.get_or_404(warehouse_id, description='Warehouse not found')
        db.session.delete(warehouse)
        db.session.commit()
        return '', 204


@ns.route('/<int:warehouse_id>/zones')
@ns.param('warehouse_id', 'Warehouse identifier')
class ZoneList(Resource):
    """Zone list operations."""

    @ns.doc('list_zones')
    @ns.marshal_list_with(zone_model)
    def get(self, warehouse_id):
        """List all zones for a warehouse."""
        warehouse = Warehouse.query.get_or_404(warehouse_id, description='Warehouse not found')
        zones = warehouse.zones.order_by(Zone.zone_order).all()
        return [z.to_dict() for z in zones]

    @ns.doc('create_zone')
    @ns.expect(zone_input)
    @ns.marshal_with(zone_model, code=201)
    def post(self, warehouse_id):
        """Add a zone to a warehouse."""
        warehouse = Warehouse.query.get_or_404(warehouse_id, description='Warehouse not found')
        data = request.json

        zone = Zone(
            warehouse_id=warehouse_id,
            name=data['name'],
            zone_order=data.get('zone_order', 0),
            area=data['area'],
            height=data['height'],
            strength=data.get('strength'),
            climate_controlled=data.get('climate_controlled', False),
            temperature_min=data.get('temperature_min'),
            temperature_max=data.get('temperature_max'),
            special_handling=data.get('special_handling', False),
            container_capacity=data.get('container_capacity', 0),
            is_weather_zone=data.get('is_weather_zone', False)
        )

        # Calculate volume
        zone.calculate_volume()

        db.session.add(zone)
        db.session.commit()

        # Update warehouse totals
        warehouse.calculate_totals()
        db.session.commit()

        return zone.to_dict(), 201


@ns.route('/<int:warehouse_id>/zones/<int:zone_id>')
@ns.param('warehouse_id', 'Warehouse identifier')
@ns.param('zone_id', 'Zone identifier')
class ZoneResource(Resource):
    """Zone operations."""

    @ns.doc('get_zone')
    @ns.marshal_with(zone_model)
    def get(self, warehouse_id, zone_id):
        """Get zone by ID."""
        zone = Zone.query.filter_by(id=zone_id, warehouse_id=warehouse_id).first_or_404(
            description='Zone not found'
        )
        return zone.to_dict()

    @ns.doc('update_zone')
    @ns.expect(zone_input)
    @ns.marshal_with(zone_model)
    def put(self, warehouse_id, zone_id):
        """Update a zone."""
        zone = Zone.query.filter_by(id=zone_id, warehouse_id=warehouse_id).first_or_404(
            description='Zone not found'
        )
        data = request.json

        zone.name = data.get('name', zone.name)
        zone.zone_order = data.get('zone_order', zone.zone_order)
        zone.area = data.get('area', zone.area)
        zone.height = data.get('height', zone.height)
        zone.strength = data.get('strength', zone.strength)
        zone.climate_controlled = data.get('climate_controlled', zone.climate_controlled)
        zone.temperature_min = data.get('temperature_min', zone.temperature_min)
        zone.temperature_max = data.get('temperature_max', zone.temperature_max)
        zone.special_handling = data.get('special_handling', zone.special_handling)
        zone.container_capacity = data.get('container_capacity', zone.container_capacity)
        zone.is_weather_zone = data.get('is_weather_zone', zone.is_weather_zone)

        # Recalculate volume
        zone.calculate_volume()

        db.session.commit()

        # Update warehouse totals
        warehouse = Warehouse.query.get(warehouse_id)
        warehouse.calculate_totals()
        db.session.commit()

        return zone.to_dict()

    @ns.doc('delete_zone')
    @ns.response(204, 'Zone deleted')
    def delete(self, warehouse_id, zone_id):
        """Delete a zone."""
        zone = Zone.query.filter_by(id=zone_id, warehouse_id=warehouse_id).first_or_404(
            description='Zone not found'
        )
        db.session.delete(zone)
        db.session.commit()

        # Update warehouse totals
        warehouse = Warehouse.query.get(warehouse_id)
        warehouse.calculate_totals()
        db.session.commit()

        return '', 204
