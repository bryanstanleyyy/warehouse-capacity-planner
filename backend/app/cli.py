"""Flask CLI commands for warehouse capacity planner."""
import click
from flask.cli import with_appcontext
from datetime import datetime
from app.extensions import db
from app.models.warehouse import Warehouse, Zone
from app.models.inventory import InventoryUpload, InventoryItem
from app.models.allocation import AllocationResult
from app.services.allocation_service import AllocationService


@click.command('seed-data')
@click.option('--clear', is_flag=True, help='Clear existing data before seeding')
@click.option('--with-allocation', is_flag=True, help='Generate sample allocation result')
@with_appcontext
def seed_data_command(clear, with_allocation):
    """Seed the database with sample warehouses and inventory data."""
    try:
        click.echo("=" * 60)
        click.echo("Warehouse Capacity Planner - Seed Data Generator")
        click.echo("=" * 60)

        # Handle existing data
        if clear:
            click.echo("\nClearing existing data...")
            clear_existing_data()
            click.echo("[OK] Existing data cleared")
        elif Warehouse.query.count() > 0:
            click.echo("\n[WARNING] Database already contains warehouse data.")
            if not click.confirm("Continue anyway?"):
                click.echo("Operation cancelled.")
                return

        # Create warehouses
        click.echo("\nCreating warehouses...")
        warehouses = create_warehouses()
        for warehouse in warehouses:
            db.session.add(warehouse)
        db.session.commit()
        click.echo(f"[OK] Created {len(warehouses)} warehouses with {sum(warehouse.zones.count() for warehouse in warehouses)} zones")

        # Create inventory uploads
        click.echo("\nCreating inventory uploads...")
        uploads = create_inventory_uploads()
        for upload in uploads:
            db.session.add(upload)
        db.session.commit()
        click.echo(f"[OK] Created {len(uploads)} inventory uploads with {sum(upload.total_items for upload in uploads)} total items")

        # Optional allocation
        if with_allocation:
            click.echo("\nRunning sample allocation...")
            allocation = create_sample_allocation(uploads[0], warehouses[0])
            db.session.add(allocation)
            db.session.commit()
            click.echo(f"[OK] Created allocation result: {allocation.total_allocated} allocated, {allocation.total_failed} failed")

        # Summary
        click.echo("\n" + "=" * 60)
        click.echo("SUMMARY:")
        click.echo(f"  Warehouses: {len(warehouses)}")
        for w in warehouses:
            click.echo(f"    - {w.name}: {w.zones.count()} zones, {float(w.total_area):,.0f} sq ft")
        click.echo(f"  Inventory uploads: {len(uploads)}")
        for u in uploads:
            click.echo(f"    - {u.upload_name}: {u.total_items} items, {float(u.total_area):,.0f} sq ft")
        if with_allocation:
            click.echo(f"  Allocation results: 1")
            click.echo(f"    - Allocated: {allocation.total_allocated}/{allocation.total_allocated + allocation.total_failed} items ({allocation.total_allocated / (allocation.total_allocated + allocation.total_failed) * 100:.1f}%)")
        click.echo("=" * 60)
        click.echo("\n[SUCCESS] Seed data created successfully!")
        click.echo("\nYou can now start the frontend to view the data:")
        click.echo("  cd frontend && npm run dev")

    except Exception as e:
        db.session.rollback()
        click.echo(f"\n[ERROR] {str(e)}", err=True)
        raise


def clear_existing_data():
    """Clear all existing data from tables in correct order."""
    AllocationResult.query.delete()
    InventoryItem.query.delete()
    InventoryUpload.query.delete()
    Zone.query.delete()
    Warehouse.query.delete()
    db.session.commit()


def create_warehouses():
    """Create all 3 warehouses with zones."""
    warehouses = []

    # Warehouse 1: Main Distribution Center
    warehouse1 = Warehouse(
        name="Main Distribution Center",
        warehouse_type="Climate Controlled Distribution",
        description="Primary distribution facility with mixed climate and standard zones",
        is_custom=False
    )

    # Zones for Warehouse 1
    zones1 = [
        Zone(
            name="Zone A - High Bay Storage",
            zone_order=1,
            area=15000,
            height=20,
            strength=250,
            climate_controlled=False,
            special_handling=False,
            is_weather_zone=False
        ),
        Zone(
            name="Zone B - Climate Controlled",
            zone_order=2,
            area=10000,
            height=12,
            strength=150,
            climate_controlled=True,
            temperature_min=55,
            temperature_max=75,
            special_handling=False,
            is_weather_zone=False
        ),
        Zone(
            name="Zone C - Standard Storage",
            zone_order=3,
            area=15000,
            height=15,
            strength=200,
            climate_controlled=False,
            special_handling=False,
            is_weather_zone=False
        ),
        Zone(
            name="Zone D - Low Clearance",
            zone_order=4,
            area=10000,
            height=8,
            strength=300,
            climate_controlled=False,
            special_handling=False,
            is_weather_zone=False
        )
    ]

    for zone in zones1:
        zone.calculate_volume()
        warehouse1.zones.append(zone)

    warehouse1.calculate_totals()
    warehouses.append(warehouse1)

    # Warehouse 2: Cold Storage Facility
    warehouse2 = Warehouse(
        name="Cold Storage Facility",
        warehouse_type="Refrigerated Warehouse",
        description="Specialized climate-controlled facility for temperature-sensitive items",
        is_custom=False
    )

    # Zones for Warehouse 2
    zones2 = [
        Zone(
            name="Zone A - Freezer",
            zone_order=1,
            area=8000,
            height=14,
            strength=175,
            climate_controlled=True,
            temperature_min=0,
            temperature_max=32,
            special_handling=True,
            is_weather_zone=False
        ),
        Zone(
            name="Zone B - Refrigerated",
            zone_order=2,
            area=12000,
            height=14,
            strength=175,
            climate_controlled=True,
            temperature_min=35,
            temperature_max=45,
            special_handling=False,
            is_weather_zone=False
        ),
        Zone(
            name="Zone C - Staging Area",
            zone_order=3,
            area=10000,
            height=10,
            strength=200,
            climate_controlled=False,
            special_handling=False,
            is_weather_zone=False
        )
    ]

    for zone in zones2:
        zone.calculate_volume()
        warehouse2.zones.append(zone)

    warehouse2.calculate_totals()
    warehouses.append(warehouse2)

    # Warehouse 3: Outdoor Storage Yard
    warehouse3 = Warehouse(
        name="Outdoor Storage Yard",
        warehouse_type="Weather Zone Storage",
        description="Outdoor storage for weather-resistant equipment and oversized items",
        is_custom=False
    )

    # Zones for Warehouse 3
    zones3 = [
        Zone(
            name="Zone A - Heavy Equipment",
            zone_order=1,
            area=20000,
            height=25,
            strength=500,
            climate_controlled=False,
            special_handling=False,
            is_weather_zone=True,
            container_capacity=0
        ),
        Zone(
            name="Zone B - Container Storage",
            zone_order=2,
            area=20000,
            height=12,
            strength=400,
            climate_controlled=False,
            special_handling=False,
            is_weather_zone=True,
            container_capacity=50
        )
    ]

    for zone in zones3:
        zone.calculate_volume()
        warehouse3.zones.append(zone)

    warehouse3.calculate_totals()
    warehouses.append(warehouse3)

    return warehouses


def create_inventory_uploads():
    """Create 2 inventory uploads with items."""
    uploads = []

    # Upload 1: Main Equipment Inventory
    upload1 = InventoryUpload(
        upload_name="Main Equipment Inventory - 2025",
        filename="main_equipment_2025.xlsx",
        site="Norfolk Base",
        bsf_factor=0.63,
        upload_date=datetime.utcnow()
    )

    # Create items for upload 1
    items1 = []

    # Small Boxes (15 items) - Easy allocation
    for i in range(1, 16):
        item = InventoryItem(
            name=f"Small Supply Box {i}",
            description="General supply storage box",
            quantity=1,
            category="General Supply",
            weight=200,
            length=4,
            width=3,
            height=3,
            service_branch="Logistics",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Standard Pallets (10 items) - General equipment
    for i in range(1, 11):
        item = InventoryItem(
            name=f"Equipment Pallet {i}",
            description="Standard pallet with equipment",
            quantity=1,
            category="Equipment",
            weight=800,
            length=4,
            width=4,
            height=5,
            service_branch="Operations",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Climate Medical Supplies (5 items) - Require climate control
    for i in range(1, 6):
        item = InventoryItem(
            name=f"Medical Supply Refrigerator {i}",
            description="Climate-controlled medical storage",
            quantity=1,
            category="Medical",
            weight=600,
            length=6,
            width=4,
            height=7,
            service_branch="Medical",
            requires_climate_control=True,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Very Tall Equipment (3 items) - Height challenge
    for i in range(1, 4):
        item = InventoryItem(
            name=f"Tall Rack System {i}",
            description="High-rise storage rack (requires 22ft+ ceiling)",
            quantity=1,
            category="Equipment",
            weight=1500,
            length=5,
            width=5,
            height=22,
            service_branch="Warehouse",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Heavy Machinery (2 items) - PSF challenge
    for i in range(1, 3):
        item = InventoryItem(
            name=f"Heavy Press Machine {i}",
            description="Industrial press (requires reinforced floor 500+ PSF)",
            quantity=1,
            category="Machinery",
            weight=40000,
            length=10,
            width=8,
            height=6,
            service_branch="Manufacturing",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Large Area Items (3 items) - Space challenge
    for i in range(1, 4):
        item = InventoryItem(
            name=f"Large Equipment Platform {i}",
            description="Wide equipment platform",
            quantity=1,
            category="Equipment",
            weight=3000,
            length=20,
            width=15,
            height=8,
            service_branch="Operations",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Climate + Special Handling (4 items)
    for i in range(1, 5):
        item = InventoryItem(
            name=f"Sensitive Lab Equipment {i}",
            description="Laboratory equipment requiring climate and special handling",
            quantity=1,
            category="Sensitive Equipment",
            weight=400,
            length=5,
            width=4,
            height=6,
            service_branch="Research",
            requires_climate_control=True,
            requires_special_handling=True
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Vehicles (5 items)
    for i in range(1, 6):
        item = InventoryItem(
            name=f"Utility Vehicle {i}",
            description="Medium-duty utility vehicle",
            quantity=1,
            category="Vehicles",
            weight=5000,
            length=15,
            width=6,
            height=7,
            service_branch="Transportation",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Office Furniture (3 items)
    for i in range(1, 4):
        item = InventoryItem(
            name=f"Office Desk Set {i}",
            description="Standard office furniture set",
            quantity=1,
            category="Furniture",
            weight=150,
            length=6,
            width=3,
            height=4,
            service_branch="Admin",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items1.append(item)

    # Add all items to upload
    for item in items1:
        upload1.items.append(item)

    upload1.calculate_totals()
    uploads.append(upload1)

    # Upload 2: Specialized Equipment
    upload2 = InventoryUpload(
        upload_name="Specialized Equipment - Q1 2025",
        filename="specialized_equipment_q1_2025.xlsx",
        site="Philadelphia Depot",
        site2="Norfolk Base",
        bsf_factor=0.70,
        upload_date=datetime.utcnow()
    )

    # Create items for upload 2
    items2 = []

    # Refrigerated Containers (8 items)
    for i in range(1, 9):
        item = InventoryItem(
            name=f"Refrigerated Container {i}",
            description="Insulated refrigerated storage container",
            quantity=1,
            category="Containers",
            weight=8000,
            length=8,
            width=8,
            height=9,
            service_branch="Logistics",
            requires_climate_control=True,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items2.append(item)

    # Hazmat Containers (3 items)
    for i in range(1, 4):
        item = InventoryItem(
            name=f"Hazmat Storage Container {i}",
            description="Hazardous materials storage (special handling required)",
            quantity=1,
            category="Hazmat",
            weight=1200,
            length=4,
            width=4,
            height=5,
            service_branch="Safety",
            requires_climate_control=False,
            requires_special_handling=True
        )
        item.calculate_area()
        item.calculate_psf()
        items2.append(item)

    # Oversized Components (6 items)
    for i in range(1, 7):
        item = InventoryItem(
            name=f"Oversized Component {i}",
            description="Large industrial component (18ft height)",
            quantity=1,
            category="Components",
            weight=6000,
            length=12,
            width=10,
            height=18,
            service_branch="Engineering",
            requires_climate_control=False,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items2.append(item)

    # Light Fragile Items (8 items)
    for i in range(1, 9):
        item = InventoryItem(
            name=f"Fragile Electronics Box {i}",
            description="Climate-sensitive electronic components",
            quantity=1,
            category="Fragile",
            weight=50,
            length=3,
            width=2,
            height=2,
            service_branch="Electronics",
            requires_climate_control=True,
            requires_special_handling=False
        )
        item.calculate_area()
        item.calculate_psf()
        items2.append(item)

    # Add all items to upload
    for item in items2:
        upload2.items.append(item)

    upload2.calculate_totals()
    uploads.append(upload2)

    return uploads


def create_sample_allocation(upload, warehouse):
    """Create a sample allocation result using AllocationService."""
    result = AllocationService.run_allocation(
        upload_id=upload.id,
        warehouse_id=warehouse.id,
        bsf_factor=float(upload.bsf_factor),
        result_name=f"Sample Allocation - {upload.upload_name} to {warehouse.name}"
    )
    return result
