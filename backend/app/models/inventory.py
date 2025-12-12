"""Inventory models."""
from datetime import datetime
from app.extensions import db


class InventoryUpload(db.Model):
    """Inventory upload model representing a batch of inventory data."""

    __tablename__ = 'inventory_uploads'

    id = db.Column(db.Integer, primary_key=True)
    upload_name = db.Column(db.String(255))
    filename = db.Column(db.String(255))
    site = db.Column(db.String(255))  # Primary site
    site2 = db.Column(db.String(255))  # Secondary site
    total_items = db.Column(db.Integer, default=0)
    total_entries = db.Column(db.Integer, default=0)
    total_weight = db.Column(db.Numeric(15, 2), default=0)  # lbs
    total_area = db.Column(db.Numeric(12, 2), default=0)  # sq ft
    bsf_factor = db.Column(db.Numeric(5, 3), default=0.63)  # Space Utilization Factor
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    upload_metadata = db.Column(db.JSON)  # Store additional info

    # Relationships
    items = db.relationship('InventoryItem', back_populates='upload', cascade='all, delete-orphan', lazy='dynamic')
    allocation_results = db.relationship('AllocationResult', back_populates='upload', lazy='dynamic')

    def __repr__(self):
        return f'<InventoryUpload {self.upload_name or self.filename}>'

    def to_dict(self, include_items=False):
        """Convert upload to dictionary."""
        data = {
            'id': self.id,
            'upload_name': self.upload_name,
            'filename': self.filename,
            'site': self.site,
            'site2': self.site2,
            'total_items': self.total_items,
            'total_entries': self.total_entries,
            'total_weight': float(self.total_weight) if self.total_weight else 0,
            'total_area': float(self.total_area) if self.total_area else 0,
            'bsf_factor': float(self.bsf_factor) if self.bsf_factor else 0.63,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'metadata': self.upload_metadata
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items.all()]

        return data

    def calculate_totals(self):
        """Calculate totals from items."""
        items = self.items.all()
        self.total_entries = len(items)
        self.total_items = sum(item.quantity for item in items)
        self.total_weight = sum(float(item.weight or 0) * item.quantity for item in items)
        self.total_area = sum(float(item.area or 0) * item.quantity for item in items)


class InventoryItem(db.Model):
    """Inventory item model representing individual items in inventory."""

    __tablename__ = 'inventory_items'
    __table_args__ = (
        db.Index('idx_upload_category', 'upload_id', 'category'),
    )

    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('inventory_uploads.id', ondelete='CASCADE'), nullable=False, index=True)

    # Item details
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    category = db.Column(db.String(100), index=True)

    # Physical dimensions
    weight = db.Column(db.Numeric(12, 2))  # lbs per item
    length = db.Column(db.Numeric(8, 2))  # ft
    width = db.Column(db.Numeric(8, 2))  # ft
    height = db.Column(db.Numeric(8, 2))  # ft
    area = db.Column(db.Numeric(10, 2))  # sq ft (base area)
    psf = db.Column(db.Numeric(8, 2))  # lbs per sq ft (floor loading)

    # Classification
    service_branch = db.Column(db.String(50))  # Department/Division (USMC/Navy → Dept)
    priority_order = db.Column(db.Integer, default=999)

    # Requirements
    requires_climate_control = db.Column(db.Boolean, default=False)
    requires_special_handling = db.Column(db.Boolean, default=False)

    # Metadata
    item_data = db.Column(db.JSON)  # Store original Excel row data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    upload = db.relationship('InventoryUpload', back_populates='items')

    def __repr__(self):
        return f'<InventoryItem {self.name} (qty: {self.quantity})>'

    def to_dict(self):
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'upload_id': self.upload_id,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'category': self.category,
            'weight': float(self.weight) if self.weight else None,
            'length': float(self.length) if self.length else None,
            'width': float(self.width) if self.width else None,
            'height': float(self.height) if self.height else None,
            'area': float(self.area) if self.area else None,
            'psf': float(self.psf) if self.psf else None,
            'service_branch': self.service_branch,
            'priority_order': self.priority_order,
            'requires_climate_control': self.requires_climate_control,
            'requires_special_handling': self.requires_special_handling,
            'item_data': self.item_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def calculate_area(self):
        """Calculate area from length and width if not provided."""
        if not self.area and self.length and self.width:
            self.area = float(self.length) * float(self.width)

    def calculate_psf(self):
        """Calculate pounds per square foot."""
        if self.weight and self.area and float(self.area) > 0:
            self.psf = float(self.weight) / float(self.area)
