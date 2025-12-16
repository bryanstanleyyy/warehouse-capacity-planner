"""Inventory API endpoints."""
from flask import request, send_file
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from app.services.inventory_service import InventoryService
from app.services.excel_service import ExcelParsingError
from app.models import InventoryUpload

# Create namespace
ns = Namespace('inventory', description='Inventory operations')

# File upload parser
upload_parser = ns.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True,
                          help='Excel file containing inventory data')
upload_parser.add_argument('upload_name', location='form', type=str,
                          help='Name for this upload')
upload_parser.add_argument('site', location='form', type=str,
                          help='Primary site')
upload_parser.add_argument('site2', location='form', type=str,
                          help='Secondary site')
upload_parser.add_argument('bsf_factor', location='form', type=float, default=0.63,
                          help='Space utilization factor (BSF)')

# Define API models
inventory_item_model = ns.model('InventoryItem', {
    'id': fields.Integer(readonly=True, description='Item ID'),
    'upload_id': fields.Integer(description='Upload ID'),
    'name': fields.String(description='Item name'),
    'description': fields.String(description='Item description'),
    'quantity': fields.Integer(description='Quantity'),
    'category': fields.String(description='Category'),
    'weight': fields.Float(description='Weight (lbs)'),
    'length': fields.Float(description='Length (ft)'),
    'width': fields.Float(description='Width (ft)'),
    'height': fields.Float(description='Height (ft)'),
    'area': fields.Float(description='Area (sq ft)'),
    'psf': fields.Float(description='Pounds per square foot'),
    'service_branch': fields.String(description='Service branch/department'),
    'priority_order': fields.Integer(description='Priority order'),
    'requires_climate_control': fields.Boolean(description='Requires climate control'),
    'requires_special_handling': fields.Boolean(description='Requires special handling'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

inventory_upload_model = ns.model('InventoryUpload', {
    'id': fields.Integer(readonly=True, description='Upload ID'),
    'upload_name': fields.String(description='Upload name'),
    'filename': fields.String(description='Original filename'),
    'site': fields.String(description='Primary site'),
    'site2': fields.String(description='Secondary site'),
    'total_items': fields.Integer(description='Total items'),
    'total_entries': fields.Integer(description='Total entries'),
    'total_weight': fields.Float(description='Total weight (lbs)'),
    'total_area': fields.Float(description='Total area (sq ft)'),
    'bsf_factor': fields.Float(description='Space utilization factor'),
    'upload_date': fields.DateTime(readonly=True, description='Upload timestamp'),
    'metadata': fields.Raw(description='Upload metadata')
})

bsf_update_model = ns.model('BSFUpdate', {
    'bsf_factor': fields.Float(required=True, description='New BSF factor (0.0 - 1.0)')
})


@ns.route('/uploads')
class InventoryUploadList(Resource):
    """Inventory upload list operations."""

    @ns.doc('list_uploads')
    @ns.marshal_list_with(inventory_upload_model)
    def get(self):
        """List all inventory uploads."""
        uploads = InventoryUpload.query.order_by(InventoryUpload.upload_date.desc()).all()
        return [u.to_dict() for u in uploads]

    @ns.doc('upload_inventory')
    @ns.expect(upload_parser)
    @ns.marshal_with(inventory_upload_model, code=201)
    def post(self):
        """Upload and process an inventory Excel file."""
        args = upload_parser.parse_args()

        try:
            inventory_service = InventoryService()
            upload = inventory_service.process_upload(
                file=args['file'],
                upload_name=args.get('upload_name'),
                site=args.get('site'),
                site2=args.get('site2'),
                bsf_factor=args.get('bsf_factor', 0.63)
            )

            return upload.to_dict(), 201

        except ExcelParsingError as e:
            ns.abort(400, f"Error parsing Excel file: {str(e)}")
        except ValueError as e:
            ns.abort(400, str(e))
        except Exception as e:
            ns.abort(500, f"Server error: {str(e)}")


@ns.route('/uploads/<int:upload_id>')
@ns.param('upload_id', 'Upload identifier')
class InventoryUploadResource(Resource):
    """Inventory upload operations."""

    @ns.doc('get_upload')
    @ns.marshal_with(inventory_upload_model)
    def get(self, upload_id):
        """Get inventory upload by ID."""
        upload = InventoryUpload.query.get_or_404(upload_id, description='Upload not found')
        return upload.to_dict()

    @ns.doc('delete_upload')
    @ns.response(204, 'Upload deleted')
    def delete(self, upload_id):
        """Delete an inventory upload and all its items."""
        inventory_service = InventoryService()
        inventory_service.delete_upload(upload_id)
        return '', 204


@ns.route('/uploads/<int:upload_id>/items')
@ns.param('upload_id', 'Upload identifier')
class InventoryItemList(Resource):
    """Inventory items operations."""

    @ns.doc('get_upload_items')
    @ns.param('category', 'Filter by category', type=str, required=False)
    @ns.param('limit', 'Limit number of results', type=int, required=False)
    @ns.param('offset', 'Offset for pagination', type=int, required=False, default=0)
    @ns.marshal_list_with(inventory_item_model)
    def get(self, upload_id):
        """Get items for an upload."""
        # Verify upload exists
        InventoryUpload.query.get_or_404(upload_id, description='Upload not found')

        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)

        inventory_service = InventoryService()
        items = inventory_service.get_upload_items(
            upload_id=upload_id,
            category=category,
            limit=limit,
            offset=offset
        )

        return [item.to_dict() for item in items]


@ns.route('/uploads/<int:upload_id>/summary')
@ns.param('upload_id', 'Upload identifier')
class InventoryUploadSummary(Resource):
    """Inventory upload summary statistics."""

    @ns.doc('get_upload_summary')
    def get(self, upload_id):
        """Get summary statistics for an upload."""
        inventory_service = InventoryService()
        summary = inventory_service.get_summary_statistics(upload_id)
        return summary


@ns.route('/uploads/<int:upload_id>/bsf')
@ns.param('upload_id', 'Upload identifier')
class InventoryUploadBSF(Resource):
    """Update BSF factor for an upload."""

    @ns.doc('update_bsf')
    @ns.expect(bsf_update_model)
    @ns.marshal_with(inventory_upload_model)
    def patch(self, upload_id):
        """Update the BSF factor for an upload."""
        data = request.json
        bsf_factor = data.get('bsf_factor')

        if bsf_factor is None:
            ns.abort(400, "bsf_factor is required")

        try:
            inventory_service = InventoryService()
            upload = inventory_service.update_bsf_factor(upload_id, bsf_factor)
            return upload.to_dict()
        except ValueError as e:
            ns.abort(400, str(e))


@ns.route('/uploads/<int:upload_id>/export/xlsx')
@ns.param('upload_id', 'Upload identifier')
class InventoryUploadExport(Resource):
    """Export inventory upload as Excel file."""

    @ns.doc('export_upload_xlsx')
    @ns.produces(['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'])
    def get(self, upload_id):
        """Export inventory upload as XLSX file."""
        try:
            inventory_service = InventoryService()
            excel_buffer = inventory_service.export_to_excel(upload_id)

            # Get upload for filename
            upload = InventoryUpload.query.get_or_404(upload_id)
            filename = f"{upload.upload_name or f'inventory_{upload_id}'}.xlsx"

            return send_file(
                excel_buffer,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            ns.abort(500, f"Error exporting Excel: {str(e)}")
