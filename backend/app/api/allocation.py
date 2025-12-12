"""Allocation API endpoints."""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.allocation_service import AllocationService

# Create namespace
ns = Namespace('allocation', description='Allocation operations')

# Define API models
allocation_request_model = ns.model('AllocationRequest', {
    'upload_id': fields.Integer(required=True, description='Inventory upload ID'),
    'warehouse_id': fields.Integer(required=True, description='Warehouse ID'),
    'bsf_factor': fields.Float(description='Space utilization factor (0.0-1.0)', default=0.63),
    'result_name': fields.String(description='Name for this allocation result')
})

zone_allocation_item = ns.model('ZoneAllocationItem', {
    'item_id': fields.Integer(description='Item ID'),
    'name': fields.String(description='Item name'),
    'category': fields.String(description='Category'),
    'quantity': fields.Integer(description='Quantity'),
    'total_area': fields.Float(description='Total area (sq ft)'),
    'total_weight': fields.Float(description='Total weight (lbs)'),
    'height': fields.Float(description='Height (ft)')
})

zone_allocation_model = ns.model('ZoneAllocation', {
    'zone_info': fields.Raw(description='Zone information'),
    'remaining_area': fields.Float(description='Remaining area (sq ft)'),
    'area_utilization': fields.Float(description='Area utilization (%)'),
    'total_items': fields.Integer(description='Total items allocated'),
    'total_weight': fields.Float(description='Total weight (lbs)'),
    'allocated_items': fields.List(fields.Nested(zone_allocation_item))
})

allocation_failure_model = ns.model('AllocationFailure', {
    'item_id': fields.Integer(description='Item ID'),
    'name': fields.String(description='Item name'),
    'category': fields.String(description='Category'),
    'quantity': fields.Integer(description='Quantity'),
    'height': fields.Float(description='Height (ft)'),
    'area': fields.Float(description='Area (sq ft)'),
    'failure_reason': fields.String(description='Reason for failure')
})

allocation_summary_model = ns.model('AllocationSummary', {
    'total_items': fields.Integer(description='Total items'),
    'total_allocated': fields.Integer(description='Total allocated'),
    'total_failed': fields.Integer(description='Total failed'),
    'allocation_rate': fields.Float(description='Allocation rate (%)'),
    'overall_utilization': fields.Float(description='Overall utilization (%)'),
    'bsf_factor': fields.Float(description='BSF factor used')
})

allocation_result_model = ns.model('AllocationResult', {
    'id': fields.Integer(readonly=True, description='Result ID'),
    'upload_id': fields.Integer(description='Upload ID'),
    'warehouse_id': fields.Integer(description='Warehouse ID'),
    'result_name': fields.String(description='Result name'),
    'bsf_factor': fields.Float(description='BSF factor'),
    'total_allocated': fields.Integer(description='Total allocated'),
    'total_failed': fields.Integer(description='Total failed'),
    'overall_fit': fields.Boolean(description='All items fit'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

allocation_result_detail_model = ns.model('AllocationResultDetail', {
    'id': fields.Integer(readonly=True, description='Result ID'),
    'upload_id': fields.Integer(description='Upload ID'),
    'warehouse_id': fields.Integer(description='Warehouse ID'),
    'result_name': fields.String(description='Result name'),
    'bsf_factor': fields.Float(description='BSF factor'),
    'total_allocated': fields.Integer(description='Total allocated'),
    'total_failed': fields.Integer(description='Total failed'),
    'overall_fit': fields.Boolean(description='All items fit'),
    'zone_allocations': fields.List(fields.Nested(zone_allocation_model)),
    'failures': fields.List(fields.Nested(allocation_failure_model)),
    'summary': fields.Nested(allocation_summary_model),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})


@ns.route('/analyze')
class AllocationAnalyze(Resource):
    """Run allocation analysis."""

    @ns.doc('run_allocation')
    @ns.expect(allocation_request_model)
    @ns.marshal_with(allocation_result_detail_model, code=201)
    def post(self):
        """Run allocation analysis for an inventory upload against a warehouse."""
        data = request.json

        try:
            allocation_service = AllocationService()
            result = allocation_service.run_allocation(
                upload_id=data['upload_id'],
                warehouse_id=data['warehouse_id'],
                bsf_factor=data.get('bsf_factor', 0.63),
                result_name=data.get('result_name')
            )

            # Return full result with allocation data
            response = result.to_dict(include_data=True)
            response.update(result.allocation_data)

            return response, 201

        except ValueError as e:
            ns.abort(400, str(e))
        except Exception as e:
            ns.abort(500, f"Server error: {str(e)}")


@ns.route('/results')
class AllocationResultList(Resource):
    """List allocation results."""

    @ns.doc('list_allocation_results')
    @ns.param('upload_id', 'Filter by upload ID', type=int, required=False)
    @ns.param('warehouse_id', 'Filter by warehouse ID', type=int, required=False)
    @ns.marshal_list_with(allocation_result_model)
    def get(self):
        """List all allocation results with optional filtering."""
        upload_id = request.args.get('upload_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)

        allocation_service = AllocationService()
        results = allocation_service.get_all_allocation_results(
            upload_id=upload_id,
            warehouse_id=warehouse_id
        )

        return [r.to_dict() for r in results]


@ns.route('/results/<int:result_id>')
@ns.param('result_id', 'Allocation result identifier')
class AllocationResultResource(Resource):
    """Allocation result operations."""

    @ns.doc('get_allocation_result')
    @ns.marshal_with(allocation_result_detail_model)
    def get(self, result_id):
        """Get allocation result by ID with full details."""
        try:
            allocation_service = AllocationService()
            result = allocation_service.get_allocation_result(result_id)

            # Return full result with allocation data
            response = result.to_dict(include_data=True)
            response.update(result.allocation_data)

            return response

        except ValueError as e:
            ns.abort(404, str(e))

    @ns.doc('delete_allocation_result')
    @ns.response(204, 'Result deleted')
    def delete(self, result_id):
        """Delete an allocation result."""
        try:
            allocation_service = AllocationService()
            allocation_service.delete_allocation_result(result_id)
            return '', 204

        except ValueError as e:
            ns.abort(404, str(e))


@ns.route('/compare')
class AllocationCompare(Resource):
    """Compare multiple allocation results."""

    @ns.doc('compare_allocations')
    @ns.param('result_ids', 'Comma-separated list of result IDs', required=True)
    def get(self):
        """Compare multiple allocation results."""
        result_ids_str = request.args.get('result_ids')
        if not result_ids_str:
            ns.abort(400, "result_ids parameter is required")

        try:
            result_ids = [int(id.strip()) for id in result_ids_str.split(',')]

            allocation_service = AllocationService()
            comparison = allocation_service.compare_allocations(result_ids)

            return comparison

        except ValueError as e:
            ns.abort(400, str(e))
        except Exception as e:
            ns.abort(500, f"Server error: {str(e)}")
