"""Seed warehouse configurations optimized for the example datasets."""
from app import create_app
from app.extensions import db
from app.models import Warehouse, Zone

app = create_app()

with app.app_context():
    # Clear existing warehouses
    print("Clearing existing warehouses...")
    Warehouse.query.delete()
    db.session.commit()

    # 1. Small Training Warehouse - for templates (5-15 items)
    small_wh = Warehouse(
        name="Small Training Warehouse",
        warehouse_type="Training Facility",
        description="Small warehouse for learning the system with template files",
        is_custom=True
    )
    db.session.add(small_wh)
    db.session.flush()

    Zone(warehouse_id=small_wh.id, name="Zone A - General Storage", area=2000, height=12,
         strength=250, zone_order=1, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=small_wh.id, name="Zone B - Climate Controlled", area=1500, height=12,
         strength=200, zone_order=2, climate_controlled=True, temperature_min=55,
         temperature_max=75, special_handling=False).save()
    Zone(warehouse_id=small_wh.id, name="Zone C - Special Handling", area=1000, height=10,
         strength=200, zone_order=3, climate_controlled=False, special_handling=True).save()

    print(f"✓ Created {small_wh.name} (4,500 sq ft)")

    # 2. Standard Distribution Center - for 50-100 items
    standard_wh = Warehouse(
        name="Standard Distribution Center",
        warehouse_type="Distribution Center",
        description="Mid-size warehouse for standard inventory (50-100 items)",
        is_custom=True
    )
    db.session.add(standard_wh)
    db.session.flush()

    Zone(warehouse_id=standard_wh.id, name="Zone A - High Bay Storage", area=15000, height=20,
         strength=250, zone_order=1, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=standard_wh.id, name="Zone B - Climate Controlled", area=10000, height=12,
         strength=200, zone_order=2, climate_controlled=True, temperature_min=55,
         temperature_max=75, special_handling=False).save()
    Zone(warehouse_id=standard_wh.id, name="Zone C - Standard Storage", area=15000, height=15,
         strength=300, zone_order=3, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=standard_wh.id, name="Zone D - Low Clearance", area=8000, height=8,
         strength=200, zone_order=4, climate_controlled=False, special_handling=False).save()

    print(f"✓ Created {standard_wh.name} (48,000 sq ft)")

    # 3. Large Regional Warehouse - for 200 items
    large_wh = Warehouse(
        name="Large Regional Warehouse",
        warehouse_type="Regional Distribution Center",
        description="Large warehouse for substantial inventory (200+ items)",
        is_custom=True
    )
    db.session.add(large_wh)
    db.session.flush()

    Zone(warehouse_id=large_wh.id, name="Zone A - High Bay (Tall Items)", area=25000, height=25,
         strength=300, zone_order=1, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=large_wh.id, name="Zone B - Climate Controlled", area=20000, height=15,
         strength=250, zone_order=2, climate_controlled=True, temperature_min=55,
         temperature_max=75, special_handling=False).save()
    Zone(warehouse_id=large_wh.id, name="Zone C - Standard Storage", area=30000, height=15,
         strength=300, zone_order=3, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=large_wh.id, name="Zone D - Heavy Duty", area=15000, height=12,
         strength=500, zone_order=4, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=large_wh.id, name="Zone E - Low Clearance", area=10000, height=8,
         strength=200, zone_order=5, climate_controlled=False, special_handling=False).save()

    print(f"✓ Created {large_wh.name} (100,000 sq ft)")

    # 4. Cold Storage Facility - for climate-controlled items
    cold_wh = Warehouse(
        name="Cold Storage Facility",
        warehouse_type="Cold Storage",
        description="Refrigerated warehouse for temperature-sensitive inventory",
        is_custom=True
    )
    db.session.add(cold_wh)
    db.session.flush()

    Zone(warehouse_id=cold_wh.id, name="Zone A - Freezer (-10°F to 0°F)", area=8000, height=12,
         strength=250, zone_order=1, climate_controlled=True, temperature_min=-10,
         temperature_max=0, special_handling=False).save()
    Zone(warehouse_id=cold_wh.id, name="Zone B - Refrigerated (35°F-45°F)", area=12000, height=12,
         strength=250, zone_order=2, climate_controlled=True, temperature_min=35,
         temperature_max=45, special_handling=False).save()
    Zone(warehouse_id=cold_wh.id, name="Zone C - Cool Storage (50°F-60°F)", area=10000, height=12,
         strength=250, zone_order=3, climate_controlled=True, temperature_min=50,
         temperature_max=60, special_handling=False).save()
    Zone(warehouse_id=cold_wh.id, name="Zone D - Hazmat Cold Storage", area=5000, height=10,
         strength=300, zone_order=4, climate_controlled=True, temperature_min=35,
         temperature_max=45, special_handling=True).save()

    print(f"✓ Created {cold_wh.name} (35,000 sq ft, all climate controlled)")

    # 5. Outdoor Storage Yard - for weather-resistant items
    yard_wh = Warehouse(
        name="Outdoor Storage Yard",
        warehouse_type="Outdoor Yard",
        description="Open-air storage for weather-resistant equipment and vehicles",
        is_custom=True
    )
    db.session.add(yard_wh)
    db.session.flush()

    Zone(warehouse_id=yard_wh.id, name="Zone A - Heavy Equipment", area=30000, height=25,
         strength=500, zone_order=1, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=yard_wh.id, name="Zone B - Vehicle Parking", area=25000, height=15,
         strength=400, zone_order=2, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=yard_wh.id, name="Zone C - Container Storage", area=40000, height=12,
         strength=350, zone_order=3, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=yard_wh.id, name="Zone D - Hazmat Outdoor", area=10000, height=12,
         strength=400, zone_order=4, climate_controlled=False, special_handling=True).save()

    print(f"✓ Created {yard_wh.name} (105,000 sq ft, no climate control)")

    # 6. Mega Distribution Complex - for stress testing (500 items)
    mega_wh = Warehouse(
        name="Mega Distribution Complex",
        warehouse_type="Mega Distribution Center",
        description="Very large facility for high-volume inventory (500+ items)",
        is_custom=True
    )
    db.session.add(mega_wh)
    db.session.flush()

    Zone(warehouse_id=mega_wh.id, name="Zone A - High Bay (25ft)", area=50000, height=25,
         strength=350, zone_order=1, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=mega_wh.id, name="Zone B - Climate Controlled", area=40000, height=15,
         strength=300, zone_order=2, climate_controlled=True, temperature_min=55,
         temperature_max=75, special_handling=False).save()
    Zone(warehouse_id=mega_wh.id, name="Zone C - Standard Storage", area=60000, height=15,
         strength=300, zone_order=3, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=mega_wh.id, name="Zone D - Heavy Duty Floor", area=30000, height=12,
         strength=600, zone_order=4, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=mega_wh.id, name="Zone E - Low Clearance", area=20000, height=8,
         strength=250, zone_order=5, climate_controlled=False, special_handling=False).save()
    Zone(warehouse_id=mega_wh.id, name="Zone F - Special Handling", area=15000, height=12,
         strength=300, zone_order=6, climate_controlled=False, special_handling=True).save()

    print(f"✓ Created {mega_wh.name} (215,000 sq ft)")

    db.session.commit()

    print("\n" + "="*60)
    print("SUCCESS! Created 6 optimized warehouse configurations:")
    print("="*60)
    print("\n📦 WAREHOUSE GUIDE:")
    print("\n1. Small Training Warehouse (4,500 sq ft)")
    print("   → Use with: quick_start, basic, comprehensive templates")
    print("   → Best for: 5-15 items, learning the system")

    print("\n2. Standard Distribution Center (48,000 sq ft)")
    print("   → Use with: warehouse_standard_50_items.xlsx")
    print("   → Use with: warehouse_mixed_100_items.xlsx")
    print("   → Best for: 50-100 items, typical operations")

    print("\n3. Large Regional Warehouse (100,000 sq ft)")
    print("   → Use with: warehouse_large_200_items.xlsx")
    print("   → Best for: 200+ items, regional distribution")

    print("\n4. Cold Storage Facility (35,000 sq ft)")
    print("   → Use with: cold_storage_inventory.xlsx")
    print("   → Best for: Temperature-sensitive items")

    print("\n5. Outdoor Storage Yard (105,000 sq ft)")
    print("   → Use with: outdoor_yard_inventory.xlsx")
    print("   → Best for: Weather-resistant equipment")

    print("\n6. Mega Distribution Complex (215,000 sq ft)")
    print("   → Use with: stress_test_500_items.xlsx")
    print("   → Best for: High-volume testing, 500+ items")

    print("\n" + "="*60)
    print("✓ Refresh your browser to see the new warehouses!")
    print("="*60)
