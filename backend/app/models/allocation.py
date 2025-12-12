"""Allocation result models."""
from datetime import datetime
from app.extensions import db


class AllocationResult(db.Model):
    """Allocation result model representing the outcome of an allocation analysis."""

    __tablename__ = 'allocation_results'

    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('inventory_uploads.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    result_name = db.Column(db.String(255))
    bsf_factor = db.Column(db.Numeric(5, 3), nullable=False)

    # Allocation metrics
    total_allocated = db.Column(db.Integer, default=0)
    total_failed = db.Column(db.Integer, default=0)
    overall_fit = db.Column(db.Boolean, default=False)

    # Detailed allocation data stored as JSON
    allocation_data = db.Column(db.JSON)  # Zone allocations, failures, utilization
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    upload = db.relationship('InventoryUpload', back_populates='allocation_results')
    warehouse = db.relationship('Warehouse', back_populates='allocation_results')
    reports = db.relationship('SavedReport', back_populates='allocation', lazy='dynamic')

    def __repr__(self):
        return f'<AllocationResult {self.result_name or self.id}>'

    def to_dict(self, include_data=False):
        """Convert allocation result to dictionary."""
        data = {
            'id': self.id,
            'upload_id': self.upload_id,
            'warehouse_id': self.warehouse_id,
            'result_name': self.result_name,
            'bsf_factor': float(self.bsf_factor) if self.bsf_factor else None,
            'total_allocated': self.total_allocated,
            'total_failed': self.total_failed,
            'overall_fit': self.overall_fit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_data:
            data['allocation_data'] = self.allocation_data

        return data


class SavedReport(db.Model):
    """Saved report model for generated reports."""

    __tablename__ = 'saved_reports'

    id = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('allocation_results.id'), nullable=False)
    report_name = db.Column(db.String(255))
    report_type = db.Column(db.String(50))  # HTML, PDF, Excel
    file_path = db.Column(db.String(500))  # If saved to disk
    report_data = db.Column(db.JSON)  # Report configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    allocation = db.relationship('AllocationResult', back_populates='reports')

    def __repr__(self):
        return f'<SavedReport {self.report_name} ({self.report_type})>'

    def to_dict(self):
        """Convert report to dictionary."""
        return {
            'id': self.id,
            'allocation_id': self.allocation_id,
            'report_name': self.report_name,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'report_data': self.report_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
