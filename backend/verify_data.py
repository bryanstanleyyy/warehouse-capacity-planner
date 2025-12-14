"""Quick script to verify seed data."""
from app import create_app
from app.models import Warehouse, InventoryUpload, AllocationResult

app = create_app()

with app.app_context():
    print("Database Contents:")
    print(f"  Warehouses: {Warehouse.query.count()}")
    print(f"  Inventory Uploads: {InventoryUpload.query.count()}")
    print(f"  Allocation Results: {AllocationResult.query.count()}")

    print("\nWarehouse Details:")
    for w in Warehouse.query.all():
        print(f"  - {w.name}: {w.zones.count()} zones")

    print("\nInventory Upload Details:")
    for u in InventoryUpload.query.all():
        print(f"  - {u.upload_name}: {u.total_items} items")
