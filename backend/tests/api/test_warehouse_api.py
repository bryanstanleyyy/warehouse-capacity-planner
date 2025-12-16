"""API tests for warehouse endpoints."""
import pytest
import json


@pytest.mark.api
class TestWarehouseAPI:
    """Test warehouse CRUD API endpoints."""

    def test_get_warehouses_empty(self, client, db):
        """Test GET /warehouses with no warehouses."""
        response = client.get('/api/v1/warehouses')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_warehouses(self, client, db, sample_warehouse):
        """Test GET /warehouses."""
        response = client.get('/api/v1/warehouses')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]['name'] == sample_warehouse.name

    def test_create_warehouse(self, client, db):
        """Test POST /warehouses to create a warehouse."""
        payload = {
            'name': 'New Test Warehouse',
            'warehouse_type': 'Distribution',
            'description': 'Test warehouse',
            'is_custom': True
        }

        response = client.post(
            '/api/v1/warehouses',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Test Warehouse'
        assert data['warehouse_type'] == 'Distribution'
        assert 'id' in data

    def test_create_warehouse_duplicate_name(self, client, db, sample_warehouse):
        """Test creating warehouse with duplicate name."""
        payload = {
            'name': sample_warehouse.name,  # Duplicate
            'warehouse_type': 'Distribution',
            'is_custom': True
        }

        response = client.post(
            '/api/v1/warehouses',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Should fail (conflict or bad request)
        assert response.status_code in [400, 409]

    def test_get_warehouse_by_id(self, client, db, sample_warehouse):
        """Test GET /warehouses/<id>."""
        response = client.get(f'/api/v1/warehouses/{sample_warehouse.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_warehouse.id
        assert data['name'] == sample_warehouse.name
        # Should include zones
        assert 'zones' in data or 'zone_count' in data

    def test_get_warehouse_not_found(self, client, db):
        """Test GET /warehouses/<id> with invalid ID."""
        response = client.get('/api/v1/warehouses/99999')

        assert response.status_code == 404

    def test_update_warehouse(self, client, db, sample_warehouse):
        """Test PUT /warehouses/<id>."""
        payload = {
            'name': 'Updated Warehouse Name',
            'description': 'Updated description'
        }

        response = client.put(
            f'/api/v1/warehouses/{sample_warehouse.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Warehouse Name'
        assert data['description'] == 'Updated description'

    def test_delete_warehouse(self, client, db, sample_warehouse):
        """Test DELETE /warehouses/<id>."""
        warehouse_id = sample_warehouse.id

        response = client.delete(f'/api/v1/warehouses/{warehouse_id}')

        assert response.status_code in [200, 204]

        # Verify deleted
        get_response = client.get(f'/api/v1/warehouses/{warehouse_id}')
        assert get_response.status_code == 404


@pytest.mark.api
class TestZoneAPI:
    """Test zone CRUD API endpoints."""

    def test_get_zones(self, client, db, sample_warehouse):
        """Test GET /warehouses/<id>/zones."""
        response = client.get(f'/api/v1/warehouses/{sample_warehouse.id}/zones')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 3  # Sample warehouse has 3 zones

    def test_create_zone(self, client, db, sample_warehouse):
        """Test POST /warehouses/<id>/zones."""
        payload = {
            'name': 'New Zone',
            'area': 600.0,
            'height': 14.0,
            'strength': 350.0,
            'zone_order': 4
        }

        response = client.post(
            f'/api/v1/warehouses/{sample_warehouse.id}/zones',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Zone'
        assert data['area'] == 600.0
        assert data['height'] == 14.0

    def test_get_zone_by_id(self, client, db, sample_warehouse):
        """Test GET /warehouses/<id>/zones/<zone_id>."""
        zone = sample_warehouse.zones.first()

        response = client.get(
            f'/api/v1/warehouses/{sample_warehouse.id}/zones/{zone.id}'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == zone.id
        assert data['name'] == zone.name

    def test_update_zone(self, client, db, sample_warehouse):
        """Test PUT /warehouses/<id>/zones/<zone_id>."""
        zone = sample_warehouse.zones.first()
        payload = {
            'name': 'Updated Zone Name',
            'area': 1200.0
        }

        response = client.put(
            f'/api/v1/warehouses/{sample_warehouse.id}/zones/{zone.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Zone Name'
        assert data['area'] == 1200.0

    def test_delete_zone(self, client, db, sample_warehouse):
        """Test DELETE /warehouses/<id>/zones/<zone_id>."""
        zone = sample_warehouse.zones.first()
        zone_id = zone.id

        response = client.delete(
            f'/api/v1/warehouses/{sample_warehouse.id}/zones/{zone_id}'
        )

        assert response.status_code in [200, 204]

        # Verify deleted
        get_response = client.get(
            f'/api/v1/warehouses/{sample_warehouse.id}/zones/{zone_id}'
        )
        assert get_response.status_code == 404


@pytest.mark.api
class TestWarehouseAPIValidation:
    """Test API input validation."""

    def test_create_warehouse_missing_name(self, client, db):
        """Test creating warehouse without name."""
        payload = {
            'warehouse_type': 'Distribution',
            # Missing 'name'
        }

        response = client.post(
            '/api/v1/warehouses',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_zone_missing_required_fields(self, client, db, sample_warehouse):
        """Test creating zone without required fields."""
        payload = {
            'name': 'Incomplete Zone',
            # Missing area, height
        }

        response = client.post(
            f'/api/v1/warehouses/{sample_warehouse.id}/zones',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_zone_invalid_warehouse(self, client, db):
        """Test creating zone for non-existent warehouse."""
        payload = {
            'name': 'Test Zone',
            'area': 1000.0,
            'height': 12.0
        }

        response = client.post(
            '/api/v1/warehouses/99999/zones',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 404
