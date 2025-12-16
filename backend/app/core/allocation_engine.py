"""
Core allocation engine for warehouse capacity planning.

Based on the height-first, multi-constraint optimization algorithm from the
MAGTF Vessel Capacity Analyzer. Adapted for warehouse/zone allocation.
"""
from typing import List, Dict, Any, Optional


class AllocationEngine:
    """
    Allocation engine that assigns inventory items to warehouse zones.

    Uses height-first optimization with multi-constraint checking:
    - Height clearance
    - Floor area capacity (with BSF - Space Utilization Factor)
    - Floor strength (PSF - pounds per square foot)
    """

    def __init__(self, bsf_factor: float = 0.63):
        """
        Initialize the allocation engine.

        Args:
            bsf_factor: Space utilization factor (0.0 - 1.0)
                       Default 0.63 means 63% additional space needed for
                       aisles, clearances, tie-downs, access, etc.
        """
        self.bsf_factor = bsf_factor

    def allocate(self, items: List[Dict[str, Any]],
                 zones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Allocate inventory items to warehouse zones.

        Args:
            items: List of inventory items with dimensions and quantities
            zones: List of warehouse zones with capacity specifications

        Returns:
            Dictionary containing allocation results:
            - zone_allocations: List of zone allocation details
            - failures: List of items that couldn't be allocated
            - overall_fit: Boolean indicating if all items fit
            - summary: Summary statistics
        """
        # Initialize zone tracking
        zone_allocations = self._initialize_zones(zones)

        # Create individual items list (expand quantities)
        individual_items = self._expand_items(items)

        # Sort items (priority first if available, then height/weight)
        sorted_items = self._sort_items(individual_items)

        # Track allocation failures
        allocation_failures = []

        # Pre-calculate zone characteristics for performance
        zone_heights = [zone['height'] for zone in zones]
        zone_strengths = [zone.get('strength', float('inf')) for zone in zones]

        # Allocate each individual item
        for item in sorted_items:
            # Calculate required area with BSF
            required_area = item['area'] * (1 + self.bsf_factor)
            equipment_height = item['height']
            equipment_psf = item.get('psf', 0)
            requires_climate = item.get('requires_climate_control', False)
            requires_special = item.get('requires_special_handling', False)

            # Find eligible zones
            eligible_zones = []

            for zone_idx, zone_alloc in enumerate(zone_allocations):
                zone = zones[zone_idx]

                # Check basic constraints
                if not (equipment_height <= zone_heights[zone_idx] and
                        required_area <= zone_alloc['remaining_area'] and
                        equipment_psf <= zone_strengths[zone_idx]):
                    continue

                # Check climate control requirement
                if requires_climate and not zone.get('climate_controlled', False):
                    continue

                # Check special handling requirement
                if requires_special and not zone.get('special_handling', False):
                    continue

                # Calculate height waste (prefer minimal waste)
                height_waste = zone_heights[zone_idx] - equipment_height

                # Calculate priority score (higher is better)
                priority_score = 0

                # Bonus for exact climate match
                if requires_climate and zone.get('climate_controlled', False):
                    priority_score += 1000

                # Bonus for exact special handling match
                if requires_special and zone.get('special_handling', False):
                    priority_score += 1000

                eligible_zones.append({
                    'zone_idx': zone_idx,
                    'priority_score': priority_score,
                    'height_waste': height_waste,
                    'area_remaining': zone_alloc['remaining_area']
                })

            if eligible_zones:
                # Sort by priority (DESC), minimal height waste, then by available area
                eligible_zones.sort(key=lambda x: (-x['priority_score'], x['height_waste'], -x['area_remaining']))

                # Allocate to best zone
                best_zone = eligible_zones[0]
                zone_idx = best_zone['zone_idx']
                zone_alloc = zone_allocations[zone_idx]

                # Find existing entry for this item type
                existing_entry = None
                for entry in zone_alloc['allocated_items']:
                    if entry['item_id'] == item['item_id']:
                        existing_entry = entry
                        break

                if existing_entry:
                    # Add to existing entry
                    existing_entry['quantity'] += 1
                    existing_entry['total_area'] += required_area
                    existing_entry['total_weight'] += item['weight']
                else:
                    # Create new entry
                    zone_alloc['allocated_items'].append({
                        'item_id': item['item_id'],
                        'name': item['name'],
                        'category': item.get('category'),
                        'quantity': 1,
                        'weight': item['weight'],
                        'total_weight': item['weight'],
                        'area': item['area'],
                        'total_area': required_area,
                        'height': item['height'],
                        'psf': equipment_psf,
                        'service_branch': item.get('service_branch'),
                        'requires_climate_control': item.get('requires_climate_control', False),
                        'requires_special_handling': item.get('requires_special_handling', False)
                    })

                # Update zone utilization
                zone_alloc['remaining_area'] -= required_area
                zone_alloc['area_utilization'] = (
                    (zone_alloc['zone_info']['area'] - zone_alloc['remaining_area']) /
                    zone_alloc['zone_info']['area'] * 100
                )
                zone_alloc['total_items'] += 1
                zone_alloc['total_weight'] += item['weight']

                # Track constraints
                if equipment_height > (zone_heights[zone_idx] - 0.5):  # Within 6 inches of ceiling
                    zone_alloc['height_constrained_items'] += 1

                if equipment_psf > zone_strengths[zone_idx] * 0.9:  # Using >90% of strength
                    zone_alloc['strength_constrained_items'] += 1

                zone_alloc['max_equipment_psf'] = max(
                    zone_alloc['max_equipment_psf'],
                    equipment_psf
                )
            else:
                # Item doesn't fit - determine failure reason
                max_zone_height = max(zone_heights)
                max_zone_area = max(za['remaining_area'] for za in zone_allocations)
                max_zone_strength = max(zone_strengths)

                # Check for climate/special zones availability
                has_climate_zones = any(zone.get('climate_controlled', False) for zone in zones)
                has_special_zones = any(zone.get('special_handling', False) for zone in zones)

                failure_reasons = []

                if equipment_height > max_zone_height:
                    failure_reasons.append(
                        f"Height too tall ({equipment_height:.1f}' > {max_zone_height:.1f}')"
                    )

                if required_area > max_zone_area:
                    failure_reasons.append(
                        f"Area too large ({required_area:.1f} sq ft > {max_zone_area:.1f} sq ft available)"
                    )

                if equipment_psf > max_zone_strength:
                    failure_reasons.append(
                        f"Too heavy ({equipment_psf:.1f} PSF > {max_zone_strength:.1f} PSF max)"
                    )

                # NEW: Check climate control requirement
                if requires_climate and not has_climate_zones:
                    failure_reasons.append("Requires climate control (no zones available)")
                elif requires_climate:
                    # Has climate zones but still failed - likely space issue
                    failure_reasons.append("Requires climate control (no space in climate zones)")

                # NEW: Check special handling requirement
                if requires_special and not has_special_zones:
                    failure_reasons.append("Requires special handling (no zones available)")
                elif requires_special:
                    # Has special zones but still failed - likely space issue
                    failure_reasons.append("Requires special handling (no space in special zones)")

                if not failure_reasons:
                    failure_reasons.append("No suitable zone found")

                # Check if failure is just due to area (could fit if zone was empty)
                can_theoretically_fit = (
                    equipment_height <= max_zone_height and
                    equipment_psf <= max_zone_strength and
                    (not requires_climate or has_climate_zones) and
                    (not requires_special or has_special_zones)
                )

                allocation_failures.append({
                    'item_id': item['item_id'],
                    'name': item['name'],
                    'category': item.get('category'),
                    'quantity': 1,
                    'height': equipment_height,
                    'area': item['area'],
                    'required_area': required_area,
                    'psf': equipment_psf,
                    'failure_reason': "; ".join(failure_reasons),
                    'can_theoretically_fit': can_theoretically_fit
                })

        # Calculate summary statistics
        summary = self._calculate_summary(zone_allocations, allocation_failures)

        return {
            'zone_allocations': zone_allocations,
            'failures': allocation_failures,
            'overall_fit': len(allocation_failures) == 0,
            'summary': summary
        }

    def _initialize_zones(self, zones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Initialize zone tracking structures."""
        zone_allocations = []

        for zone in zones:
            zone_allocations.append({
                'zone_info': zone.copy(),
                'remaining_area': zone['area'],
                'allocated_items': [],
                'area_utilization': 0.0,
                'height_constrained_items': 0,
                'strength_constrained_items': 0,
                'max_equipment_psf': 0,
                'total_items': 0,
                'total_weight': 0
            })

        return zone_allocations

    def _expand_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Expand items by quantity to create individual item entries."""
        individual_items = []

        for item in items:
            quantity = item.get('quantity', 1)

            for i in range(quantity):
                individual_item = {
                    'item_id': item['id'],
                    'name': item['name'],
                    'category': item.get('category'),
                    'weight': item.get('weight', 0),
                    'area': item.get('area', 0),
                    'height': item.get('height', 0),
                    'psf': item.get('psf', 0),
                    'service_branch': item.get('service_branch'),
                    'priority_order': item.get('priority_order', 999),
                    'requires_climate_control': item.get('requires_climate_control', False),
                    'requires_special_handling': item.get('requires_special_handling', False),
                    'item_number': i + 1
                }
                individual_items.append(individual_item)

        return individual_items

    def _sort_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort items for optimal allocation.

        If priority information exists, sort by priority first,
        then by height and weight within each priority group.
        Otherwise, use height-first sorting (tallest and heaviest first).
        """
        # Check if any items have priority information
        has_priority = any(
            item.get('priority_order') is not None and
            item.get('priority_order') != 999
            for item in items
        )

        if has_priority:
            # Sort by priority, then height, then weight
            items.sort(key=lambda x: (
                x.get('priority_order', 999),
                -x.get('height', 0),
                -x.get('weight', 0)
            ))
        else:
            # Height-first sorting (tallest and heaviest first)
            items.sort(key=lambda x: (
                -x.get('height', 0),
                -x.get('weight', 0)
            ))

        return items

    def _calculate_summary(self,
                          zone_allocations: List[Dict[str, Any]],
                          failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for the allocation."""
        total_allocated = sum(za['total_items'] for za in zone_allocations)
        total_failed = len(failures)
        total_items = total_allocated + total_failed

        total_warehouse_area = sum(za['zone_info']['area'] for za in zone_allocations)
        total_used_area = sum(
            za['zone_info']['area'] - za['remaining_area']
            for za in zone_allocations
        )

        overall_utilization = (
            (total_used_area / total_warehouse_area * 100) if total_warehouse_area > 0 else 0
        )

        # Zone-wise statistics
        zone_stats = []
        for zone_alloc in zone_allocations:
            zone_stats.append({
                'zone_name': zone_alloc['zone_info']['name'],
                'zone_id': zone_alloc['zone_info'].get('id'),
                'total_items': zone_alloc['total_items'],
                'area_utilization': zone_alloc['area_utilization'],
                'total_weight': zone_alloc['total_weight'],
                'height_constrained_items': zone_alloc['height_constrained_items'],
                'strength_constrained_items': zone_alloc['strength_constrained_items']
            })

        return {
            'total_items': total_items,
            'total_allocated': total_allocated,
            'total_failed': total_failed,
            'allocation_rate': (total_allocated / total_items * 100) if total_items > 0 else 0,
            'overall_utilization': overall_utilization,
            'total_warehouse_area': total_warehouse_area,
            'total_used_area': total_used_area,
            'bsf_factor': self.bsf_factor,
            'zone_stats': zone_stats
        }
