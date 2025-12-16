"""Integration tests for AllocationService."""
import pytest
from app.services.allocation_service import AllocationService
from app.models.allocation import AllocationResult


@pytest.mark.integration
class TestAllocationServiceRunAllocation:
    """Test AllocationService.run_allocation() method."""

    def test_run_allocation_success(self, db, sample_warehouse, sample_inventory_upload):
        """Test successful allocation."""
        result = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            bsf_factor=0.63,
            result_name='Test Allocation'
        )

        assert result is not None
        assert isinstance(result, AllocationResult)
        assert result.id is not None
        assert result.upload_id == sample_inventory_upload.id
        assert result.warehouse_id == sample_warehouse.id
        assert float(result.bsf_factor) == pytest.approx(0.63)
        assert result.result_name == 'Test Allocation'
        assert result.allocation_data is not None

    def test_run_allocation_invalid_upload_id(self, db, sample_warehouse):
        """Test allocation with invalid upload ID."""
        with pytest.raises(ValueError, match="Inventory upload .* not found"):
            AllocationService.run_allocation(
                upload_id=99999,
                warehouse_id=sample_warehouse.id,
                bsf_factor=0.63
            )

    def test_run_allocation_invalid_warehouse_id(self, db, sample_inventory_upload):
        """Test allocation with invalid warehouse ID."""
        with pytest.raises(ValueError, match="Warehouse .* not found"):
            AllocationService.run_allocation(
                upload_id=sample_inventory_upload.id,
                warehouse_id=99999,
                bsf_factor=0.63
            )

    def test_run_allocation_bsf_below_zero(self, db, sample_warehouse, sample_inventory_upload):
        """Test allocation with BSF factor below 0."""
        with pytest.raises(ValueError, match="BSF factor must be between 0.0 and 1.0"):
            AllocationService.run_allocation(
                upload_id=sample_inventory_upload.id,
                warehouse_id=sample_warehouse.id,
                bsf_factor=-0.1
            )

    def test_run_allocation_bsf_above_one(self, db, sample_warehouse, sample_inventory_upload):
        """Test allocation with BSF factor above 1.0."""
        with pytest.raises(ValueError, match="BSF factor must be between 0.0 and 1.0"):
            AllocationService.run_allocation(
                upload_id=sample_inventory_upload.id,
                warehouse_id=sample_warehouse.id,
                bsf_factor=1.5
            )

    def test_run_allocation_warehouse_no_zones(self, db, empty_warehouse, sample_inventory_upload):
        """Test allocation with warehouse that has no zones."""
        with pytest.raises(ValueError, match="has no zones defined"):
            AllocationService.run_allocation(
                upload_id=sample_inventory_upload.id,
                warehouse_id=empty_warehouse.id,
                bsf_factor=0.63
            )

    def test_run_allocation_stores_summary_data(self, db, sample_warehouse, sample_inventory_upload):
        """Test that allocation stores summary statistics."""
        result = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            bsf_factor=0.63
        )

        assert result.total_allocated >= 0
        assert result.total_failed >= 0
        assert result.total_allocated + result.total_failed > 0
        assert result.overall_fit is not None

    def test_run_allocation_with_default_bsf(self, db, sample_warehouse, sample_inventory_upload):
        """Test allocation with default BSF factor."""
        result = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id
            # bsf_factor defaults to 0.63
        )

        assert float(result.bsf_factor) == pytest.approx(0.63)

    def test_run_allocation_with_zero_bsf(self, db, sample_warehouse, sample_inventory_upload):
        """Test allocation with zero BSF factor (no additional space)."""
        result = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            bsf_factor=0.0
        )

        assert result.bsf_factor == 0.0
        # Should still succeed (just uses exact item areas)
        assert result is not None


@pytest.mark.integration
class TestAllocationServiceRetrieval:
    """Test AllocationService retrieval methods."""

    def test_get_allocation_result(self, db, sample_warehouse, sample_inventory_upload):
        """Test retrieving an allocation result."""
        # Create result first
        result = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            bsf_factor=0.63
        )

        # Retrieve it
        retrieved = AllocationService.get_allocation_result(result.id)

        assert retrieved is not None
        assert retrieved.id == result.id
        assert retrieved.allocation_data is not None

    def test_get_allocation_result_not_found(self, db):
        """Test retrieving non-existent allocation result."""
        with pytest.raises(ValueError, match="Allocation result .* not found"):
            AllocationService.get_allocation_result(99999)

    def test_get_all_allocation_results(self, db, sample_warehouse, sample_inventory_upload):
        """Test retrieving all allocation results."""
        # Create multiple results
        result1 = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            result_name='Result 1'
        )
        result2 = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            result_name='Result 2'
        )

        # Retrieve all
        results = AllocationService.get_all_allocation_results()

        assert len(results) >= 2
        result_ids = [r.id for r in results]
        assert result1.id in result_ids
        assert result2.id in result_ids

    def test_delete_allocation_result(self, db, sample_warehouse, sample_inventory_upload):
        """Test deleting an allocation result."""
        # Create result
        result = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id
        )
        result_id = result.id

        # Delete it (returns None on success)
        AllocationService.delete_allocation_result(result_id)

        # Verify it's gone (should raise ValueError)
        with pytest.raises(ValueError, match="Allocation result .* not found"):
            AllocationService.get_allocation_result(result_id)

    def test_delete_allocation_result_not_found(self, db):
        """Test deleting non-existent allocation result."""
        with pytest.raises(ValueError, match="Allocation result .* not found"):
            AllocationService.delete_allocation_result(99999)


@pytest.mark.integration
class TestAllocationServiceComparison:
    """Test AllocationService comparison functionality."""

    def test_compare_allocations(self, db, sample_warehouse, sample_inventory_upload):
        """Test comparing multiple allocation results."""
        # Create results with different BSF factors
        result1 = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            bsf_factor=0.5,
            result_name='BSF 0.5'
        )
        result2 = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id,
            bsf_factor=0.63,
            result_name='BSF 0.63'
        )

        # Compare them
        comparison = AllocationService.compare_allocations([result1.id, result2.id])

        assert comparison is not None
        assert 'results' in comparison
        assert len(comparison['results']) == 2
        assert 'best_fit' in comparison
        assert 'best_utilization' in comparison

    def test_compare_allocations_empty_list(self, db):
        """Test comparison with empty list."""
        comparison = AllocationService.compare_allocations([])
        assert comparison is not None
        assert comparison['results'] == []

    def test_compare_allocations_invalid_id(self, db, sample_warehouse, sample_inventory_upload):
        """Test comparison with invalid result ID."""
        result1 = AllocationService.run_allocation(
            upload_id=sample_inventory_upload.id,
            warehouse_id=sample_warehouse.id
        )

        # Include invalid ID - should raise ValueError
        with pytest.raises(ValueError, match="Allocation result .* not found"):
            AllocationService.compare_allocations([result1.id, 99999])
