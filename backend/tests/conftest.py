"""Pytest configuration and fixtures for warehouse capacity planner tests."""
import pytest
import tempfile
import os
import sys
from io import BytesIO
from openpyxl import Workbook
from werkzeug.datastructures import FileStorage

# Add tests directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db as _db
from app.models.warehouse import Warehouse, Zone
from app.models.inventory import InventoryUpload, InventoryItem
from fixtures.sample_data import (
    SAMPLE_WAREHOUSES,
    SAMPLE_ZONES,
    SAMPLE_ITEMS,
    create_simple_zone,
    create_simple_item
)


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application.

    This fixture is session-scoped, meaning it's created once per test session.
    """
    app = create_app('testing')

    # Create application context
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    """Create a clean database for each test.

    This fixture is function-scoped, meaning each test gets a fresh database.
    """
    with app.app_context():
        # Create all tables
        _db.create_all()

        yield _db

        # Drop all tables after test
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create a Flask test client.

    Used for testing API endpoints without starting a server.
    """
    return app.test_client()


@pytest.fixture
def sample_warehouse(db):
    """Create a sample warehouse with three zones in the database.

    Returns:
        Warehouse: A warehouse with standard, climate-controlled, and special handling zones
    """
    warehouse = Warehouse(
        name=SAMPLE_WAREHOUSES[0]['name'],
        warehouse_type=SAMPLE_WAREHOUSES[0]['warehouse_type'],
        description=SAMPLE_WAREHOUSES[0]['description'],
        is_custom=True
    )
    db.session.add(warehouse)
    db.session.flush()  # Get warehouse ID

    # Add three different types of zones
    for zone_data in SAMPLE_ZONES:
        zone = Zone(
            warehouse_id=warehouse.id,
            **zone_data
        )
        zone.calculate_volume()
        db.session.add(zone)

    db.session.commit()

    # Refresh to get relationships
    db.session.refresh(warehouse)
    warehouse.calculate_totals()
    db.session.commit()

    return warehouse


@pytest.fixture
def sample_zones_dict():
    """Return sample zone dictionaries for testing allocation engine.

    Returns:
        List[Dict]: Three zones with different capabilities
    """
    return [
        {
            'id': 1,
            'name': 'Zone A - Standard',
            'area': 1000.0,
            'height': 12.0,
            'strength': 300.0,
            'climate_controlled': False,
            'special_handling': False
        },
        {
            'id': 2,
            'name': 'Zone B - Climate Controlled',
            'area': 800.0,
            'height': 15.0,
            'strength': 500.0,
            'climate_controlled': True,
            'special_handling': False
        },
        {
            'id': 3,
            'name': 'Zone C - Special Handling',
            'area': 500.0,
            'height': 10.0,
            'strength': 200.0,
            'climate_controlled': False,
            'special_handling': True
        }
    ]


@pytest.fixture
def sample_inventory_upload(db):
    """Create a sample inventory upload with items in the database.

    Returns:
        InventoryUpload: An upload with sample items
    """
    upload = InventoryUpload(
        upload_name='Test Upload',
        filename='test_inventory.xlsx',
        site='Test Site',
        bsf_factor=0.63
    )
    db.session.add(upload)
    db.session.flush()  # Get upload ID

    # Add sample items
    for idx, item_data in enumerate(SAMPLE_ITEMS, start=1):
        item = InventoryItem(
            upload_id=upload.id,
            **item_data
        )
        db.session.add(item)

    db.session.commit()

    # Calculate totals
    upload.calculate_totals()
    db.session.commit()

    return upload


@pytest.fixture
def sample_items_dict():
    """Return sample item dictionaries for testing allocation engine.

    Returns:
        List[Dict]: Sample inventory items with IDs
    """
    items = []
    for idx, item_data in enumerate(SAMPLE_ITEMS, start=1):
        item_dict = item_data.copy()
        item_dict['id'] = idx
        items.append(item_dict)
    return items


@pytest.fixture
def sample_excel_file():
    """Create a temporary Excel file with sample inventory data.

    Returns:
        BytesIO: In-memory Excel file suitable for upload testing
    """
    # Create a workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory"

    # Add headers
    headers = [
        'Name', 'Description', 'Quantity', 'Weight (lbs)',
        'Length (ft)', 'Width (ft)', 'Height (ft)', 'Category',
        'Service Branch', 'Requires Climate Control', 'Requires Special Handling'
    ]
    ws.append(headers)

    # Add sample data
    sample_rows = [
        ['Item 1', 'Test item 1', 5, 1000, 4, 4, 6, 'General', 'Navy', 'No', 'No'],
        ['Item 2', 'Test item 2', 3, 800, 5, 5, 8, 'Equipment', 'Army', 'Yes', 'No'],
        ['Item 3', 'Test item 3', 2, 500, 3, 3, 4, 'Medical', 'Air Force', 'No', 'Yes']
    ]

    for row in sample_rows:
        ws.append(row)

    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    return excel_file


@pytest.fixture
def mock_file_upload(sample_excel_file):
    """Create a mock werkzeug FileStorage object for testing file uploads.

    Args:
        sample_excel_file: Excel file fixture

    Returns:
        FileStorage: Mock file upload object
    """
    return FileStorage(
        stream=sample_excel_file,
        filename='test_inventory.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@pytest.fixture
def empty_warehouse(db):
    """Create a warehouse with no zones.

    Returns:
        Warehouse: An empty warehouse
    """
    warehouse = Warehouse(
        name='Empty Warehouse',
        warehouse_type='Test',
        description='Warehouse with no zones',
        is_custom=True
    )
    db.session.add(warehouse)
    db.session.commit()
    return warehouse


@pytest.fixture
def simple_zone_dict():
    """Create a simple zone dictionary for testing.

    Returns:
        Dict: A simple zone with id
    """
    zone = create_simple_zone()
    zone['id'] = 1
    return zone


@pytest.fixture
def simple_item_dict():
    """Create a simple item dictionary for testing.

    Returns:
        Dict: A simple item with id
    """
    item = create_simple_item()
    item['id'] = 1
    return item


@pytest.fixture
def tall_item_dict():
    """Create a tall item that requires high ceiling.

    Returns:
        Dict: An item with 14 ft height
    """
    item = create_simple_item(name='Tall Item', height=14.0, area=25.0)
    item['id'] = 2
    return item


@pytest.fixture
def heavy_item_dict():
    """Create a heavy item that requires strong floor.

    Returns:
        Dict: An item with high PSF (400 PSF)
    """
    item = create_simple_item(
        name='Heavy Item',
        height=6.0,
        area=100.0,
        weight=40000.0,
        psf=400.0
    )
    item['id'] = 3
    return item


@pytest.fixture
def climate_item_dict():
    """Create an item requiring climate control.

    Returns:
        Dict: An item with climate control requirement
    """
    item = create_simple_item(
        name='Climate Item',
        height=5.0,
        area=9.0,
        requires_climate=True
    )
    item['id'] = 4
    return item


@pytest.fixture
def special_item_dict():
    """Create an item requiring special handling.

    Returns:
        Dict: An item with special handling requirement
    """
    item = create_simple_item(
        name='Special Item',
        height=4.0,
        area=4.0,
        requires_special=True
    )
    item['id'] = 5
    return item
