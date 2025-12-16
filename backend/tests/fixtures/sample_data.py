"""Sample test data for warehouse capacity planner tests."""
from typing import Dict, List, Any


# Sample Warehouses
SAMPLE_WAREHOUSES = [
    {
        'name': 'Test Warehouse 1',
        'warehouse_type': 'Distribution Center',
        'description': 'Primary test warehouse with mixed zones',
        'is_custom': True
    },
    {
        'name': 'Test Warehouse 2',
        'warehouse_type': 'Cold Storage',
        'description': 'Climate-controlled test warehouse',
        'is_custom': True
    }
]


# Sample Zones
SAMPLE_ZONES = [
    {
        'name': 'Zone A - Standard',
        'area': 1000.0,
        'height': 12.0,
        'strength': 300.0,
        'zone_order': 1,
        'climate_controlled': False,
        'special_handling': False
    },
    {
        'name': 'Zone B - Climate Controlled',
        'area': 800.0,
        'height': 15.0,
        'strength': 500.0,
        'zone_order': 2,
        'climate_controlled': True,
        'temperature_min': 35.0,
        'temperature_max': 45.0,
        'special_handling': False
    },
    {
        'name': 'Zone C - Special Handling',
        'area': 500.0,
        'height': 10.0,
        'strength': 200.0,
        'zone_order': 3,
        'climate_controlled': False,
        'special_handling': True
    }
]


# Sample Inventory Items
SAMPLE_ITEMS = [
    {
        'name': 'Standard Pallet 1',
        'description': 'Standard pallet with regular items',
        'quantity': 5,
        'weight': 1000.0,
        'length': 4.0,
        'width': 4.0,
        'height': 6.0,
        'area': 16.0,
        'psf': 62.5,  # 1000 / 16
        'category': 'General',
        'service_branch': 'Navy',
        'requires_climate_control': False,
        'requires_special_handling': False
    },
    {
        'name': 'Tall Equipment',
        'description': 'Tall equipment requiring high ceiling',
        'quantity': 2,
        'weight': 2000.0,
        'length': 5.0,
        'width': 5.0,
        'height': 14.0,
        'area': 25.0,
        'psf': 80.0,
        'category': 'Equipment',
        'service_branch': 'Army',
        'requires_climate_control': False,
        'requires_special_handling': False
    },
    {
        'name': 'Heavy Machinery',
        'description': 'Heavy machinery requiring strong floor',
        'quantity': 1,
        'weight': 10000.0,
        'length': 10.0,
        'width': 10.0,
        'height': 8.0,
        'area': 100.0,
        'psf': 100.0,
        'category': 'Machinery',
        'service_branch': 'Marine Corps',
        'requires_climate_control': False,
        'requires_special_handling': False
    },
    {
        'name': 'Climate Sensitive Item',
        'description': 'Item requiring climate control',
        'quantity': 3,
        'weight': 500.0,
        'length': 3.0,
        'width': 3.0,
        'height': 4.0,
        'area': 9.0,
        'psf': 55.6,
        'category': 'Medical',
        'service_branch': 'Air Force',
        'requires_climate_control': True,
        'requires_special_handling': False
    },
    {
        'name': 'Hazardous Material',
        'description': 'Item requiring special handling',
        'quantity': 2,
        'weight': 300.0,
        'length': 2.0,
        'width': 2.0,
        'height': 3.0,
        'area': 4.0,
        'psf': 75.0,
        'category': 'Hazmat',
        'service_branch': 'Navy',
        'requires_climate_control': False,
        'requires_special_handling': True
    }
]


# Sample Inventory Items with Priority
SAMPLE_ITEMS_WITH_PRIORITY = [
    {
        'name': 'Priority 1 Item',
        'description': 'Highest priority item',
        'quantity': 2,
        'weight': 500.0,
        'length': 3.0,
        'width': 3.0,
        'height': 5.0,
        'area': 9.0,
        'psf': 55.6,
        'category': 'Critical',
        'priority_order': 1,
        'requires_climate_control': False,
        'requires_special_handling': False
    },
    {
        'name': 'Priority 2 Item',
        'description': 'Second priority item',
        'quantity': 3,
        'weight': 800.0,
        'length': 4.0,
        'width': 4.0,
        'height': 6.0,
        'area': 16.0,
        'psf': 50.0,
        'category': 'Important',
        'priority_order': 2,
        'requires_climate_control': False,
        'requires_special_handling': False
    },
    {
        'name': 'No Priority Item',
        'description': 'Item without priority',
        'quantity': 1,
        'weight': 1000.0,
        'length': 5.0,
        'width': 5.0,
        'height': 7.0,
        'area': 25.0,
        'psf': 40.0,
        'category': 'Standard',
        'requires_climate_control': False,
        'requires_special_handling': False
    }
]


def create_sample_warehouse_dict() -> Dict[str, Any]:
    """Create a sample warehouse dictionary for testing."""
    return SAMPLE_WAREHOUSES[0].copy()


def create_sample_zones_dict() -> List[Dict[str, Any]]:
    """Create sample zones dictionary for testing."""
    return [zone.copy() for zone in SAMPLE_ZONES]


def create_sample_items_dict() -> List[Dict[str, Any]]:
    """Create sample items dictionary for testing."""
    return [item.copy() for item in SAMPLE_ITEMS]


def create_simple_item(name: str = "Test Item",
                      height: float = 6.0,
                      area: float = 16.0,
                      weight: float = 1000.0,
                      psf: float = 62.5,
                      quantity: int = 1,
                      requires_climate: bool = False,
                      requires_special: bool = False) -> Dict[str, Any]:
    """Create a simple test item with specified dimensions."""
    return {
        'name': name,
        'description': f'Test item: {name}',
        'quantity': quantity,
        'weight': weight,
        'length': 4.0,
        'width': 4.0,
        'height': height,
        'area': area,
        'psf': psf,
        'category': 'Test',
        'service_branch': 'Navy',
        'requires_climate_control': requires_climate,
        'requires_special_handling': requires_special
    }


def create_simple_zone(name: str = "Test Zone",
                      area: float = 1000.0,
                      height: float = 12.0,
                      strength: float = 300.0,
                      climate_controlled: bool = False,
                      special_handling: bool = False) -> Dict[str, Any]:
    """Create a simple test zone with specified specifications."""
    return {
        'name': name,
        'area': area,
        'height': height,
        'strength': strength,
        'zone_order': 1,
        'climate_controlled': climate_controlled,
        'special_handling': special_handling
    }
