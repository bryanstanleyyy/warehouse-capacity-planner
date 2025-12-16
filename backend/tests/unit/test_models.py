"""Unit tests for database models."""
import pytest
from decimal import Decimal
from app.models.warehouse import Warehouse, Zone
from app.models.inventory import InventoryUpload, InventoryItem


@pytest.mark.unit
class TestWarehouseModel:
    """Test Warehouse model functionality."""

    def test_create_warehouse(self, db):
        """Test creating a warehouse."""
        warehouse = Warehouse(
            name='Test Warehouse',
            warehouse_type='Distribution',
            description='Test description',
            is_custom=True
        )
        db.session.add(warehouse)
        db.session.commit()

        assert warehouse.id is not None
        assert warehouse.name == 'Test Warehouse'
        assert warehouse.warehouse_type == 'Distribution'
        assert warehouse.is_custom is True

    def test_warehouse_to_dict(self, sample_warehouse):
        """Test warehouse serialization to dictionary."""
        data = sample_warehouse.to_dict()

        assert data['id'] == sample_warehouse.id
        assert data['name'] == sample_warehouse.name
        assert data['warehouse_type'] == sample_warehouse.warehouse_type
        assert 'created_at' in data
        assert 'zone_count' in data
        assert data['zone_count'] == 3  # Sample warehouse has 3 zones

    def test_warehouse_to_dict_with_zones(self, sample_warehouse):
        """Test warehouse serialization including zones."""
        data = sample_warehouse.to_dict(include_zones=True)

        assert 'zones' in data
        assert len(data['zones']) == 3
        assert data['zones'][0]['name'] is not None

    def test_warehouse_zone_relationship(self, sample_warehouse):
        """Test relationship between warehouse and zones."""
        zones = sample_warehouse.zones.all()

        assert len(zones) == 3
        for zone in zones:
            assert zone.warehouse_id == sample_warehouse.id
            assert zone.warehouse == sample_warehouse

    def test_calculate_totals(self, db):
        """Test calculate_totals() method."""
        warehouse = Warehouse(name='Test', is_custom=True)
        db.session.add(warehouse)
        db.session.flush()

        # Add zones
        zone1 = Zone(warehouse_id=warehouse.id, name='Zone 1', area=1000, height=12)
        zone2 = Zone(warehouse_id=warehouse.id, name='Zone 2', area=800, height=15)
        zone1.calculate_volume()
        zone2.calculate_volume()
        db.session.add_all([zone1, zone2])
        db.session.commit()

        # Calculate totals
        warehouse.calculate_totals()
        db.session.commit()

        assert warehouse.total_area == 1800.0  # 1000 + 800
        assert warehouse.total_volume == 24000.0  # (1000 * 12) + (800 * 15)

    def test_warehouse_cascade_delete(self, db, sample_warehouse):
        """Test that deleting warehouse cascades to zones."""
        warehouse_id = sample_warehouse.id
        zone_ids = [zone.id for zone in sample_warehouse.zones.all()]

        # Delete warehouse
        db.session.delete(sample_warehouse)
        db.session.commit()

        # Verify zones are also deleted
        assert db.session.query(Warehouse).filter_by(id=warehouse_id).first() is None
        for zone_id in zone_ids:
            assert db.session.query(Zone).filter_by(id=zone_id).first() is None


@pytest.mark.unit
class TestZoneModel:
    """Test Zone model functionality."""

    def test_create_zone(self, db, sample_warehouse):
        """Test creating a zone."""
        zone = Zone(
            warehouse_id=sample_warehouse.id,
            name='Test Zone',
            area=500.0,
            height=10.0,
            strength=250.0,
            zone_order=1
        )
        db.session.add(zone)
        db.session.commit()

        assert zone.id is not None
        assert zone.warehouse_id == sample_warehouse.id
        assert zone.name == 'Test Zone'
        assert float(zone.area) == 500.0
        assert float(zone.height) == 10.0

    def test_zone_to_dict(self, sample_warehouse):
        """Test zone serialization to dictionary."""
        zone = sample_warehouse.zones.first()
        data = zone.to_dict()

        assert data['id'] == zone.id
        assert data['warehouse_id'] == zone.warehouse_id
        assert data['name'] == zone.name
        assert data['area'] == float(zone.area)
        assert data['height'] == float(zone.height)
        assert 'climate_controlled' in data
        assert 'special_handling' in data

    def test_calculate_volume(self, db, sample_warehouse):
        """Test calculate_volume() method."""
        zone = Zone(
            warehouse_id=sample_warehouse.id,
            name='Test Zone',
            area=1000.0,
            height=12.0
        )
        db.session.add(zone)

        # Calculate volume
        zone.calculate_volume()
        db.session.commit()

        assert zone.volume is not None
        assert float(zone.volume) == 12000.0  # 1000 * 12

    def test_zone_with_climate_control(self, db, sample_warehouse):
        """Test zone with climate control specifications."""
        zone = Zone(
            warehouse_id=sample_warehouse.id,
            name='Climate Zone',
            area=800.0,
            height=15.0,
            climate_controlled=True,
            temperature_min=35.0,
            temperature_max=45.0
        )
        db.session.add(zone)
        db.session.commit()

        assert zone.climate_controlled is True
        assert float(zone.temperature_min) == 35.0
        assert float(zone.temperature_max) == 45.0

    def test_zone_with_special_handling(self, db, sample_warehouse):
        """Test zone with special handling capability."""
        zone = Zone(
            warehouse_id=sample_warehouse.id,
            name='Special Zone',
            area=500.0,
            height=10.0,
            special_handling=True
        )
        db.session.add(zone)
        db.session.commit()

        assert zone.special_handling is True


@pytest.mark.unit
class TestInventoryUploadModel:
    """Test InventoryUpload model functionality."""

    def test_create_inventory_upload(self, db):
        """Test creating an inventory upload."""
        upload = InventoryUpload(
            upload_name='Test Upload',
            filename='test.xlsx',
            site='Test Site',
            bsf_factor=0.63
        )
        db.session.add(upload)
        db.session.commit()

        assert upload.id is not None
        assert upload.upload_name == 'Test Upload'
        assert upload.filename == 'test.xlsx'
        assert float(upload.bsf_factor) == 0.63

    def test_inventory_upload_to_dict(self, sample_inventory_upload):
        """Test inventory upload serialization to dictionary."""
        data = sample_inventory_upload.to_dict()

        assert data['id'] == sample_inventory_upload.id
        assert data['upload_name'] == sample_inventory_upload.upload_name
        assert data['filename'] == sample_inventory_upload.filename
        assert data['total_items'] > 0
        assert data['total_weight'] > 0
        assert 'upload_date' in data

    def test_inventory_upload_to_dict_with_items(self, sample_inventory_upload):
        """Test inventory upload serialization including items."""
        data = sample_inventory_upload.to_dict(include_items=True)

        assert 'items' in data
        assert len(data['items']) > 0
        assert data['items'][0]['name'] is not None

    def test_calculate_totals(self, db):
        """Test calculate_totals() method."""
        upload = InventoryUpload(
            upload_name='Test',
            filename='test.xlsx',
            bsf_factor=0.63
        )
        db.session.add(upload)
        db.session.flush()

        # Add items
        item1 = InventoryItem(
            upload_id=upload.id,
            name='Item 1',
            quantity=5,
            weight=100.0,
            area=10.0,
            length=4.0,
            width=2.5,
            height=6.0
        )
        item2 = InventoryItem(
            upload_id=upload.id,
            name='Item 2',
            quantity=3,
            weight=200.0,
            area=20.0,
            length=5.0,
            width=4.0,
            height=8.0
        )
        db.session.add_all([item1, item2])
        db.session.commit()

        # Calculate totals
        upload.calculate_totals()
        db.session.commit()

        # total_entries should be 2 (two rows)
        assert upload.total_entries == 2
        # total_items should be 8 (5 + 3)
        assert upload.total_items == 8
        # total_weight should be 1100 (5*100 + 3*200)
        assert float(upload.total_weight) == 1100.0
        # total_area should be 110 (5*10 + 3*20)
        assert float(upload.total_area) == 110.0

    def test_inventory_upload_cascade_delete(self, db, sample_inventory_upload):
        """Test that deleting upload cascades to items."""
        upload_id = sample_inventory_upload.id
        item_ids = [item.id for item in sample_inventory_upload.items.all()]

        # Delete upload
        db.session.delete(sample_inventory_upload)
        db.session.commit()

        # Verify items are also deleted
        assert db.session.query(InventoryUpload).filter_by(id=upload_id).first() is None
        for item_id in item_ids:
            assert db.session.query(InventoryItem).filter_by(id=item_id).first() is None


@pytest.mark.unit
class TestInventoryItemModel:
    """Test InventoryItem model functionality."""

    def test_create_inventory_item(self, db, sample_inventory_upload):
        """Test creating an inventory item."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Test Item',
            description='Test description',
            quantity=10,
            weight=500.0,
            length=4.0,
            width=4.0,
            height=6.0,
            category='Test'
        )
        db.session.add(item)
        db.session.commit()

        assert item.id is not None
        assert item.upload_id == sample_inventory_upload.id
        assert item.name == 'Test Item'
        assert item.quantity == 10

    def test_inventory_item_to_dict(self, sample_inventory_upload):
        """Test inventory item serialization to dictionary."""
        item = sample_inventory_upload.items.first()
        data = item.to_dict()

        assert data['id'] == item.id
        assert data['upload_id'] == item.upload_id
        assert data['name'] == item.name
        assert data['quantity'] == item.quantity
        assert 'requires_climate_control' in data
        assert 'requires_special_handling' in data

    def test_calculate_area(self, db, sample_inventory_upload):
        """Test calculate_area() method."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Test Item',
            length=5.0,
            width=4.0,
            quantity=1
        )
        db.session.add(item)

        # Calculate area
        item.calculate_area()
        db.session.commit()

        assert item.area is not None
        assert float(item.area) == 20.0  # 5 * 4

    def test_calculate_area_already_provided(self, db, sample_inventory_upload):
        """Test that calculate_area() doesn't override existing area."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Test Item',
            length=5.0,
            width=4.0,
            area=25.0,  # Already set
            quantity=1
        )
        db.session.add(item)

        # Calculate area (should not change)
        item.calculate_area()
        db.session.commit()

        assert float(item.area) == 25.0  # Should remain unchanged

    def test_calculate_psf(self, db, sample_inventory_upload):
        """Test calculate_psf() method."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Test Item',
            weight=1000.0,
            area=16.0,
            length=4.0,
            width=4.0,
            height=6.0,
            quantity=1
        )
        db.session.add(item)

        # Calculate PSF
        item.calculate_psf()
        db.session.commit()

        assert item.psf is not None
        assert float(item.psf) == pytest.approx(62.5)  # 1000 / 16

    def test_calculate_psf_zero_area(self, db, sample_inventory_upload):
        """Test that calculate_psf() handles zero area gracefully."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Test Item',
            weight=1000.0,
            area=0.0,
            quantity=1
        )
        db.session.add(item)

        # Calculate PSF (should not crash)
        item.calculate_psf()
        db.session.commit()

        # PSF should not be set when area is zero
        assert item.psf is None or float(item.psf) == 0

    def test_item_with_requirements(self, db, sample_inventory_upload):
        """Test item with climate control and special handling requirements."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Special Item',
            quantity=1,
            weight=500.0,
            area=10.0,
            requires_climate_control=True,
            requires_special_handling=True
        )
        db.session.add(item)
        db.session.commit()

        assert item.requires_climate_control is True
        assert item.requires_special_handling is True

    def test_item_with_priority(self, db, sample_inventory_upload):
        """Test item with priority order."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Priority Item',
            quantity=1,
            weight=500.0,
            area=10.0,
            priority_order=1
        )
        db.session.add(item)
        db.session.commit()

        assert item.priority_order == 1

    def test_item_decimal_precision(self, db, sample_inventory_upload):
        """Test that decimal values are stored with correct precision."""
        item = InventoryItem(
            upload_id=sample_inventory_upload.id,
            name='Precision Test',
            quantity=1,
            weight=123.45,
            length=12.34,
            width=56.78,
            height=9.12,
            area=700.85
        )
        db.session.add(item)
        db.session.commit()

        assert float(item.weight) == pytest.approx(123.45)
        assert float(item.length) == pytest.approx(12.34)
        assert float(item.width) == pytest.approx(56.78)
        assert float(item.height) == pytest.approx(9.12)
        assert float(item.area) == pytest.approx(700.85)


@pytest.mark.unit
class TestModelRelationships:
    """Test relationships between models."""

    def test_warehouse_to_zones_relationship(self, sample_warehouse):
        """Test accessing zones from warehouse."""
        zones = sample_warehouse.zones.all()

        assert len(zones) > 0
        for zone in zones:
            assert zone.warehouse == sample_warehouse

    def test_zone_to_warehouse_relationship(self, sample_warehouse):
        """Test accessing warehouse from zone."""
        zone = sample_warehouse.zones.first()

        assert zone.warehouse is not None
        assert zone.warehouse.id == sample_warehouse.id

    def test_upload_to_items_relationship(self, sample_inventory_upload):
        """Test accessing items from upload."""
        items = sample_inventory_upload.items.all()

        assert len(items) > 0
        for item in items:
            assert item.upload == sample_inventory_upload

    def test_item_to_upload_relationship(self, sample_inventory_upload):
        """Test accessing upload from item."""
        item = sample_inventory_upload.items.first()

        assert item.upload is not None
        assert item.upload.id == sample_inventory_upload.id
