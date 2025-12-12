"""Allocation service for running capacity analysis."""
from typing import Dict, Any, List
from app.extensions import db
from app.models import InventoryUpload, Warehouse, AllocationResult
from app.core.allocation_engine import AllocationEngine


class AllocationService:
    """Service for allocation operations."""

    @staticmethod
    def run_allocation(upload_id: int,
                      warehouse_id: int,
                      bsf_factor: float = 0.63,
                      result_name: str = None) -> AllocationResult:
        """
        Run allocation analysis for an inventory upload against a warehouse.

        Args:
            upload_id: Inventory upload ID
            warehouse_id: Warehouse ID
            bsf_factor: Space utilization factor (0.0 - 1.0)
            result_name: Optional name for the allocation result

        Returns:
            AllocationResult object

        Raises:
            ValueError: If upload or warehouse not found or invalid parameters
        """
        # Validate BSF factor
        if not 0.0 <= bsf_factor <= 1.0:
            raise ValueError("BSF factor must be between 0.0 and 1.0")

        # Get inventory upload
        upload = InventoryUpload.query.get(upload_id)
        if not upload:
            raise ValueError(f"Inventory upload {upload_id} not found")

        # Get warehouse with zones
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse {warehouse_id} not found")

        zones = warehouse.zones.all()
        if not zones:
            raise ValueError(f"Warehouse {warehouse_id} has no zones defined")

        # Get inventory items
        items = upload.items.all()
        if not items:
            raise ValueError(f"Inventory upload {upload_id} has no items")

        # Prepare items for allocation engine
        items_data = []
        for item in items:
            # Calculate area if not set
            if not item.area and item.length and item.width:
                item.calculate_area()

            # Calculate PSF if not set
            if not item.psf:
                item.calculate_psf()

            items_data.append({
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'quantity': item.quantity,
                'weight': float(item.weight) if item.weight else 0,
                'area': float(item.area) if item.area else 0,
                'height': float(item.height) if item.height else 0,
                'psf': float(item.psf) if item.psf else 0,
                'service_branch': item.service_branch,
                'priority_order': item.priority_order,
                'requires_climate_control': item.requires_climate_control,
                'requires_special_handling': item.requires_special_handling
            })

        # Prepare zones for allocation engine
        zones_data = []
        for zone in zones:
            zones_data.append({
                'id': zone.id,
                'name': zone.name,
                'area': float(zone.area),
                'height': float(zone.height),
                'strength': float(zone.strength) if zone.strength else float('inf'),
                'volume': float(zone.volume) if zone.volume else float(zone.area) * float(zone.height),
                'climate_controlled': zone.climate_controlled,
                'special_handling': zone.special_handling,
                'container_capacity': zone.container_capacity,
                'is_weather_zone': zone.is_weather_zone
            })

        # Run allocation engine
        engine = AllocationEngine(bsf_factor=bsf_factor)
        allocation_result = engine.allocate(items_data, zones_data)

        # Save allocation result to database
        result = AllocationResult(
            upload_id=upload_id,
            warehouse_id=warehouse_id,
            result_name=result_name or f"Allocation - {warehouse.name}",
            bsf_factor=bsf_factor,
            total_allocated=allocation_result['summary']['total_allocated'],
            total_failed=allocation_result['summary']['total_failed'],
            overall_fit=allocation_result['overall_fit'],
            allocation_data=allocation_result
        )

        db.session.add(result)
        db.session.commit()

        return result

    @staticmethod
    def get_allocation_result(result_id: int) -> AllocationResult:
        """
        Get an allocation result by ID.

        Args:
            result_id: Allocation result ID

        Returns:
            AllocationResult object

        Raises:
            ValueError: If result not found
        """
        result = AllocationResult.query.get(result_id)
        if not result:
            raise ValueError(f"Allocation result {result_id} not found")
        return result

    @staticmethod
    def get_all_allocation_results(upload_id: int = None,
                                   warehouse_id: int = None) -> List[AllocationResult]:
        """
        Get all allocation results with optional filtering.

        Args:
            upload_id: Filter by inventory upload ID
            warehouse_id: Filter by warehouse ID

        Returns:
            List of AllocationResult objects
        """
        query = AllocationResult.query

        if upload_id:
            query = query.filter_by(upload_id=upload_id)

        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)

        return query.order_by(AllocationResult.created_at.desc()).all()

    @staticmethod
    def delete_allocation_result(result_id: int) -> None:
        """
        Delete an allocation result.

        Args:
            result_id: Allocation result ID

        Raises:
            ValueError: If result not found
        """
        result = AllocationResult.query.get(result_id)
        if not result:
            raise ValueError(f"Allocation result {result_id} not found")

        db.session.delete(result)
        db.session.commit()

    @staticmethod
    def compare_allocations(result_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple allocation results.

        Args:
            result_ids: List of allocation result IDs to compare

        Returns:
            Dictionary with comparison data

        Raises:
            ValueError: If any result not found
        """
        results = []
        for result_id in result_ids:
            result = AllocationResult.query.get(result_id)
            if not result:
                raise ValueError(f"Allocation result {result_id} not found")
            results.append(result)

        comparison = {
            'results': [],
            'best_fit': None,
            'best_utilization': None
        }

        best_allocation_rate = 0
        best_utilization_rate = 0

        for result in results:
            data = result.allocation_data
            summary = data['summary']

            result_info = {
                'id': result.id,
                'name': result.result_name,
                'bsf_factor': float(result.bsf_factor),
                'total_allocated': result.total_allocated,
                'total_failed': result.total_failed,
                'overall_fit': result.overall_fit,
                'allocation_rate': summary['allocation_rate'],
                'overall_utilization': summary['overall_utilization'],
                'created_at': result.created_at.isoformat()
            }

            comparison['results'].append(result_info)

            # Track best allocation rate (most items fit)
            if summary['allocation_rate'] > best_allocation_rate:
                best_allocation_rate = summary['allocation_rate']
                comparison['best_fit'] = result_info

            # Track best utilization (most efficient use of space)
            if summary['overall_utilization'] > best_utilization_rate:
                best_utilization_rate = summary['overall_utilization']
                comparison['best_utilization'] = result_info

        return comparison
