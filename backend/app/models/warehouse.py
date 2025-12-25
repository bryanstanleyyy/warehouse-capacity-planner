"""Warehouse and Zone models."""
from datetime import datetime
from app.extensions import db


class Warehouse(db.Model):
    """Warehouse model representing a storage facility."""

    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    warehouse_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_area = db.Column(db.Numeric(12, 2))  # sq ft
    total_volume = db.Column(db.Numeric(15, 2))  # cu ft
    is_custom = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    zones = db.relationship('Zone', back_populates='warehouse', cascade='all, delete-orphan', lazy='dynamic')
    allocation_results = db.relationship('AllocationResult', back_populates='warehouse', lazy='dynamic')

    def __repr__(self):
        return f'<Warehouse {self.name}>'

    def to_dict(self, include_zones=False):
        """Convert warehouse to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'warehouse_type': self.warehouse_type,
            'description': self.description,
            'total_area': float(self.total_area) if self.total_area else None,
            'total_volume': float(self.total_volume) if self.total_volume else None,
            'is_custom': self.is_custom,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'zone_count': self.zones.count()
        }

        if include_zones:
            data['zones'] = [zone.to_dict() for zone in self.zones.all()]

        return data

    def calculate_totals(self):
        """Calculate total area and volume from zones."""
        zones = self.zones.all()
        self.total_area = sum(float(zone.area or 0) for zone in zones)
        self.total_volume = sum(float(zone.volume or 0) for zone in zones)


class Zone(db.Model):
    """Zone model representing a storage zone within a warehouse."""

    __tablename__ = 'zones'

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    zone_order = db.Column(db.Integer, default=0)  # Display order

    # Capacity specifications
    area = db.Column(db.Numeric(12, 2), nullable=False)  # sq ft
    height = db.Column(db.Numeric(8, 2), nullable=False)  # ft (ceiling height)
    strength = db.Column(db.Numeric(8, 2))  # psf (floor strength)
    volume = db.Column(db.Numeric(15, 2))  # cu ft (calculated or manual)

    # Zone capabilities
    climate_controlled = db.Column(db.Boolean, default=False)
    temperature_min = db.Column(db.Numeric(5, 2))  # °F
    temperature_max = db.Column(db.Numeric(5, 2))  # °F
    special_handling = db.Column(db.Boolean, default=False)
    container_capacity = db.Column(db.Integer, default=0)
    is_weather_zone = db.Column(db.Boolean, default=False)  # Outdoor storage

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    warehouse = db.relationship('Warehouse', back_populates='zones')

    def __repr__(self):
        return f'<Zone {self.name} (Warehouse: {self.warehouse_id})>'

    def to_dict(self):
        """Convert zone to dictionary."""
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'name': self.name,
            'zone_order': self.zone_order,
            'area': float(self.area) if self.area else None,
            'height': float(self.height) if self.height else None,
            'strength': float(self.strength) if self.strength else None,
            'volume': float(self.volume) if self.volume else None,
            'climate_controlled': self.climate_controlled,
            'temperature_min': float(self.temperature_min) if self.temperature_min is not None else None,
            'temperature_max': float(self.temperature_max) if self.temperature_max is not None else None,
            'special_handling': self.special_handling,
            'container_capacity': self.container_capacity,
            'is_weather_zone': self.is_weather_zone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def calculate_volume(self):
        """Calculate volume from area and height."""
        if self.area and self.height:
            self.volume = float(self.area) * float(self.height)
