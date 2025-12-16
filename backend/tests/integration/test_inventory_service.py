"""Integration tests for InventoryService."""
import pytest
import tempfile
import os
from io import BytesIO
from unittest.mock import patch
from app.services.inventory_service import InventoryService
from app.models.inventory import InventoryUpload


@pytest.mark.integration
class TestInventoryServiceUpload:
    """Test InventoryService upload processing."""

    def test_process_upload_success(self, db, mock_file_upload):
        """Test successful file upload processing."""
        # Create a real temp file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'test_inventory.xlsx')

        # Patch the hardcoded /tmp path
        with patch('app.services.inventory_service.os.path.join', side_effect=lambda *args: temp_path):
            result = InventoryService.process_upload(
                file=mock_file_upload,
                upload_name='Test Upload',
                site='Test Site',
                bsf_factor=0.63
            )

            assert result is not None
            assert isinstance(result, InventoryUpload)
            assert result.upload_name == 'Test Upload'
            assert result.site == 'Test Site'
            assert float(result.bsf_factor) == pytest.approx(0.63)
            assert result.total_entries > 0

    def test_get_upload_with_items(self, db, sample_inventory_upload):
        """Test retrieving upload with items."""
        upload = InventoryService.get_upload_with_items(sample_inventory_upload.id)

        assert upload is not None
        assert upload.id == sample_inventory_upload.id
        assert upload.items.count() > 0

    def test_get_upload_not_found(self, db):
        """Test retrieving non-existent upload."""
        upload = InventoryService.get_upload_with_items(99999)
        assert upload is None

    def test_update_bsf_factor(self, db, sample_inventory_upload):
        """Test updating BSF factor."""
        original_bsf = float(sample_inventory_upload.bsf_factor)
        new_bsf = 0.75

        result = InventoryService.update_bsf_factor(sample_inventory_upload.id, new_bsf)

        assert result is not None
        assert isinstance(result, InventoryUpload)
        assert float(result.bsf_factor) == new_bsf
        # Refresh and check
        db.session.refresh(sample_inventory_upload)
        assert float(sample_inventory_upload.bsf_factor) == new_bsf
        assert float(sample_inventory_upload.bsf_factor) != original_bsf

    def test_update_bsf_invalid_range(self, db, sample_inventory_upload):
        """Test updating BSF with invalid value."""
        # Below 0
        with pytest.raises(ValueError):
            InventoryService.update_bsf_factor(sample_inventory_upload.id, -0.1)

        # Above 1
        with pytest.raises(ValueError):
            InventoryService.update_bsf_factor(sample_inventory_upload.id, 1.5)

    def test_delete_upload(self, db, sample_inventory_upload):
        """Test deleting upload."""
        upload_id = sample_inventory_upload.id

        # Delete should not raise an exception
        InventoryService.delete_upload(upload_id)

        # Verify deleted
        assert InventoryService.get_upload_with_items(upload_id) is None

    def test_get_summary_statistics(self, db, sample_inventory_upload):
        """Test getting summary statistics."""
        stats = InventoryService.get_summary_statistics(sample_inventory_upload.id)

        assert stats is not None
        assert 'categories' in stats
        assert 'service_branches' in stats
        assert isinstance(stats['categories'], dict)
        assert isinstance(stats['service_branches'], dict)


@pytest.mark.integration
class TestInventoryServiceItems:
    """Test InventoryService item operations."""

    def test_get_upload_items(self, db, sample_inventory_upload):
        """Test retrieving upload items."""
        items = InventoryService.get_upload_items(
            upload_id=sample_inventory_upload.id,
            limit=10,
            offset=0
        )

        assert isinstance(items, list)
        assert len(items) > 0
        # Check items are InventoryItem instances
        from app.models.inventory import InventoryItem
        assert all(isinstance(item, InventoryItem) for item in items)

    def test_get_upload_items_pagination(self, db, sample_inventory_upload):
        """Test item pagination with limit and offset."""
        # Get first 2 items
        page1 = InventoryService.get_upload_items(
            upload_id=sample_inventory_upload.id,
            limit=2,
            offset=0
        )

        # Get next 2 items
        page2 = InventoryService.get_upload_items(
            upload_id=sample_inventory_upload.id,
            limit=2,
            offset=2
        )

        # Should have different items (if there are enough items)
        if len(page2) > 0 and len(page1) > 0:
            assert page1[0].id != page2[0].id

    def test_get_upload_items_with_category_filter(self, db, sample_inventory_upload):
        """Test filtering items by category."""
        # Get first item's category
        first_item = sample_inventory_upload.items.first()
        category = first_item.category

        # Filter by that category
        items = InventoryService.get_upload_items(
            upload_id=sample_inventory_upload.id,
            category=category
        )

        # All items should have that category
        assert isinstance(items, list)
        for item in items:
            assert item.category == category
