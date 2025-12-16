"""Unit tests for the AllocationEngine core algorithm.

This test module aims for 100% coverage of the allocation engine,
which is the most critical business logic component.
"""
import pytest
from app.core.allocation_engine import AllocationEngine
from tests.fixtures.sample_data import create_simple_zone, create_simple_item


@pytest.mark.unit
class TestAllocationEngineBasic:
    """Test basic allocation functionality."""

    def test_allocate_single_item(self, simple_zone_dict, simple_item_dict):
        """Test allocating a single item to a single zone."""
        engine = AllocationEngine(bsf_factor=0.63)
        result = engine.allocate(
            items=[simple_item_dict],
            zones=[simple_zone_dict]
        )

        assert result['overall_fit'] is True
        assert len(result['failures']) == 0
        assert len(result['zone_allocations']) == 1

        zone_alloc = result['zone_allocations'][0]
        assert zone_alloc['total_items'] == 1
        assert len(zone_alloc['allocated_items']) == 1
        assert zone_alloc['allocated_items'][0]['quantity'] == 1
        assert zone_alloc['area_utilization'] > 0

    def test_allocate_multiple_items_same_type(self):
        """Test allocating multiple items of the same type."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = create_simple_item(quantity=5)
        item['id'] = 1
        zone = create_simple_zone(area=500.0)
        zone['id'] = 1

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True
        zone_alloc = result['zone_allocations'][0]
        assert zone_alloc['total_items'] == 5
        # Should have single entry with quantity=5
        assert len(zone_alloc['allocated_items']) == 1
        assert zone_alloc['allocated_items'][0]['quantity'] == 5

    def test_allocate_multiple_different_items(self):
        """Test allocating multiple different item types."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='Item 1', quantity=2), 'id': 1},
            {**create_simple_item(name='Item 2', quantity=3), 'id': 2}
        ]
        zone = create_simple_zone(area=1000.0)
        zone['id'] = 1

        result = engine.allocate(items=items, zones=[zone])

        assert result['overall_fit'] is True
        zone_alloc = result['zone_allocations'][0]
        assert zone_alloc['total_items'] == 5
        assert len(zone_alloc['allocated_items']) == 2


@pytest.mark.unit
class TestAllocationEngineConstraints:
    """Test constraint validation in allocation."""

    def test_height_constraint_success(self):
        """Test that item fits when height is within limit."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(height=10.0), 'id': 1}
        zone = {**create_simple_zone(height=12.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True
        assert len(result['failures']) == 0

    def test_height_constraint_failure(self):
        """Test that item fails when too tall for all zones."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(height=15.0), 'id': 1}
        zone = {**create_simple_zone(height=12.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is False
        assert len(result['failures']) == 1
        failure = result['failures'][0]
        assert 'Height too tall' in failure['failure_reason']
        assert failure['can_theoretically_fit'] is False

    def test_area_constraint_with_bsf(self):
        """Test that BSF factor is applied to area calculation."""
        engine = AllocationEngine(bsf_factor=0.5)  # 50% additional space
        item = {**create_simple_item(area=100.0, quantity=1), 'id': 1}
        zone = {**create_simple_zone(area=200.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        # Required area = 100 * (1 + 0.5) = 150
        # Zone has 200, so it should fit
        assert result['overall_fit'] is True
        zone_alloc = result['zone_allocations'][0]
        # Remaining should be 200 - 150 = 50
        assert zone_alloc['remaining_area'] == pytest.approx(50.0)

    def test_area_constraint_failure(self):
        """Test that item fails when area (with BSF) exceeds available space."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(area=100.0, quantity=1), 'id': 1}
        zone = {**create_simple_zone(area=150.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        # Required area = 100 * (1 + 0.63) = 163, exceeds 150
        assert result['overall_fit'] is False
        assert len(result['failures']) == 1
        failure = result['failures'][0]
        assert 'Area too large' in failure['failure_reason']
        assert failure['can_theoretically_fit'] is True  # Could fit if zone was bigger

    def test_psf_constraint_success(self):
        """Test that item fits when PSF is within strength limit."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(psf=250.0), 'id': 1}
        zone = {**create_simple_zone(strength=300.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True

    def test_psf_constraint_failure(self):
        """Test that item fails when PSF exceeds floor strength."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(psf=400.0), 'id': 1}
        zone = {**create_simple_zone(strength=300.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is False
        assert len(result['failures']) == 1
        failure = result['failures'][0]
        assert 'Too heavy' in failure['failure_reason']
        assert '400' in failure['failure_reason']
        assert failure['can_theoretically_fit'] is False

    def test_climate_control_requirement_success(self):
        """Test that climate item allocates to climate zone."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(requires_climate=True), 'id': 1}
        zone = {**create_simple_zone(climate_controlled=True), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True
        zone_alloc = result['zone_allocations'][0]
        assert zone_alloc['allocated_items'][0]['requires_climate_control'] is True

    def test_climate_control_requirement_failure_no_zones(self):
        """Test that climate item fails when no climate zones available."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(requires_climate=True), 'id': 1}
        zone = {**create_simple_zone(climate_controlled=False), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is False
        failure = result['failures'][0]
        assert 'Requires climate control (no zones available)' in failure['failure_reason']

    def test_special_handling_requirement_success(self):
        """Test that special item allocates to special handling zone."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(requires_special=True), 'id': 1}
        zone = {**create_simple_zone(special_handling=True), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True
        zone_alloc = result['zone_allocations'][0]
        assert zone_alloc['allocated_items'][0]['requires_special_handling'] is True

    def test_special_handling_requirement_failure_no_zones(self):
        """Test that special item fails when no special handling zones available."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(requires_special=True), 'id': 1}
        zone = {**create_simple_zone(special_handling=False), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is False
        failure = result['failures'][0]
        assert 'Requires special handling (no zones available)' in failure['failure_reason']

    def test_climate_requirement_failure_insufficient_space(self):
        """Test climate item fails when climate zone exists but lacks space."""
        engine = AllocationEngine(bsf_factor=0.63)
        # Large item requiring climate
        item = {**create_simple_item(requires_climate=True, area=200.0), 'id': 1}
        # Small climate zone
        zone = {**create_simple_zone(area=100.0, climate_controlled=True), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is False
        failure = result['failures'][0]
        # Should indicate space issue in climate zones, not missing zones
        assert 'no space in climate zones' in failure['failure_reason']


@pytest.mark.unit
class TestAllocationEngineSorting:
    """Test item sorting logic."""

    def test_height_first_sorting(self):
        """Test that items are sorted by height (tallest first) when no priority."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='Short', height=5.0), 'id': 1},
            {**create_simple_item(name='Tall', height=10.0), 'id': 2},
            {**create_simple_item(name='Medium', height=7.0), 'id': 3}
        ]

        sorted_items = engine._sort_items(items)

        # Should be sorted: Tall (10), Medium (7), Short (5)
        assert sorted_items[0]['name'] == 'Tall'
        assert sorted_items[1]['name'] == 'Medium'
        assert sorted_items[2]['name'] == 'Short'

    def test_weight_as_tie_breaker(self):
        """Test that weight is used as tie-breaker when heights are equal."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='Light', height=6.0, weight=500.0), 'id': 1},
            {**create_simple_item(name='Heavy', height=6.0, weight=1000.0), 'id': 2}
        ]

        sorted_items = engine._sort_items(items)

        # Same height, heavier comes first
        assert sorted_items[0]['name'] == 'Heavy'
        assert sorted_items[1]['name'] == 'Light'

    def test_priority_based_sorting(self):
        """Test that items with priority are sorted by priority first."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='No Priority', height=10.0), 'id': 1, 'priority_order': 999},
            {**create_simple_item(name='Priority 2', height=5.0), 'id': 2, 'priority_order': 2},
            {**create_simple_item(name='Priority 1', height=7.0), 'id': 3, 'priority_order': 1}
        ]

        sorted_items = engine._sort_items(items)

        # Should be sorted by priority: 1, 2, 999
        assert sorted_items[0]['name'] == 'Priority 1'
        assert sorted_items[1]['name'] == 'Priority 2'
        assert sorted_items[2]['name'] == 'No Priority'

    def test_height_within_priority_group(self):
        """Test that height sorting applies within same priority group."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='P1 Short', height=5.0), 'id': 1, 'priority_order': 1},
            {**create_simple_item(name='P1 Tall', height=10.0), 'id': 2, 'priority_order': 1}
        ]

        sorted_items = engine._sort_items(items)

        # Same priority, tallest first
        assert sorted_items[0]['name'] == 'P1 Tall'
        assert sorted_items[1]['name'] == 'P1 Short'


@pytest.mark.unit
class TestAllocationEngineZoneSelection:
    """Test zone selection and priority logic."""

    def test_zone_selection_minimal_height_waste(self):
        """Test that zone with minimal height waste is preferred."""
        engine = AllocationEngine(bsf_factor=0.0)  # No BSF for simplicity
        item = {**create_simple_item(height=8.0, area=10.0), 'id': 1}
        zones = [
            {**create_simple_zone(name='Tall', height=15.0, area=100.0), 'id': 1},
            {**create_simple_zone(name='Short', height=10.0, area=100.0), 'id': 2}
        ]

        result = engine.allocate(items=[item], zones=zones)

        # Should prefer zone 2 (10ft) over zone 1 (15ft) - less waste
        allocated_zone_name = result['zone_allocations'][1]['allocated_items'][0]['name']
        assert allocated_zone_name is not None
        # Verify item went to second zone
        assert result['zone_allocations'][1]['total_items'] == 1
        assert result['zone_allocations'][0]['total_items'] == 0

    def test_climate_zone_priority_bonus(self):
        """Test that climate items get priority bonus for climate zones."""
        engine = AllocationEngine(bsf_factor=0.0)
        item = {**create_simple_item(requires_climate=True, area=10.0), 'id': 1}
        zones = [
            {**create_simple_zone(name='Standard', area=100.0), 'id': 1},
            {**create_simple_zone(name='Climate', area=100.0, climate_controlled=True), 'id': 2}
        ]

        result = engine.allocate(items=[item], zones=zones)

        # Should strongly prefer climate zone due to +1000 priority bonus
        assert result['zone_allocations'][1]['total_items'] == 1
        assert result['zone_allocations'][0]['total_items'] == 0

    def test_special_handling_zone_priority_bonus(self):
        """Test that special items get priority bonus for special handling zones."""
        engine = AllocationEngine(bsf_factor=0.0)
        item = {**create_simple_item(requires_special=True, area=10.0), 'id': 1}
        zones = [
            {**create_simple_zone(name='Standard', area=100.0), 'id': 1},
            {**create_simple_zone(name='Special', area=100.0, special_handling=True), 'id': 2}
        ]

        result = engine.allocate(items=[item], zones=zones)

        # Should prefer special zone due to +1000 priority bonus
        assert result['zone_allocations'][1]['total_items'] == 1
        assert result['zone_allocations'][0]['total_items'] == 0


@pytest.mark.unit
class TestAllocationEngineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_items_list(self, simple_zone_dict):
        """Test allocation with no items."""
        engine = AllocationEngine(bsf_factor=0.63)
        result = engine.allocate(items=[], zones=[simple_zone_dict])

        assert result['overall_fit'] is True
        assert len(result['failures']) == 0
        assert result['summary']['total_items'] == 0
        assert result['summary']['total_allocated'] == 0

    def test_empty_zones_list(self, simple_item_dict):
        """Test allocation with no zones."""
        engine = AllocationEngine(bsf_factor=0.63)
        result = engine.allocate(items=[simple_item_dict], zones=[])

        assert result['overall_fit'] is False
        assert len(result['failures']) == 1
        assert result['summary']['total_failed'] == 1

    def test_bsf_factor_zero(self):
        """Test allocation with BSF=0.0 (no additional space)."""
        engine = AllocationEngine(bsf_factor=0.0)
        item = {**create_simple_item(area=100.0), 'id': 1}
        zone = {**create_simple_zone(area=100.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        # Should fit exactly with no BSF
        assert result['overall_fit'] is True
        assert result['zone_allocations'][0]['remaining_area'] == pytest.approx(0.0)

    def test_bsf_factor_one(self):
        """Test allocation with BSF=1.0 (100% additional space)."""
        engine = AllocationEngine(bsf_factor=1.0)
        item = {**create_simple_item(area=50.0), 'id': 1}
        zone = {**create_simple_zone(area=100.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        # Required area = 50 * (1 + 1.0) = 100
        assert result['overall_fit'] is True
        assert result['zone_allocations'][0]['remaining_area'] == pytest.approx(0.0)

    def test_infinite_strength_zone(self):
        """Test zone with no strength limit (infinite strength)."""
        engine = AllocationEngine(bsf_factor=0.63)
        # Very heavy item
        item = {**create_simple_item(psf=10000.0), 'id': 1}
        # Zone with no strength specified (defaults to inf)
        zone = create_simple_zone()
        zone.pop('strength', None)  # Remove strength key
        zone['id'] = 1

        result = engine.allocate(items=[item], zones=[zone])

        # Should fit despite high PSF (no strength constraint)
        assert result['overall_fit'] is True

    def test_item_at_exact_height_limit(self):
        """Test item at exact height limit of zone."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(height=12.0), 'id': 1}
        zone = {**create_simple_zone(height=12.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True

    def test_item_at_exact_psf_limit(self):
        """Test item at exact PSF limit of zone."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(psf=300.0), 'id': 1}
        zone = {**create_simple_zone(strength=300.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is True


@pytest.mark.unit
class TestAllocationEngineFailures:
    """Test failure scenarios and failure reason reporting."""

    def test_multiple_failure_reasons(self):
        """Test item that fails multiple constraints."""
        engine = AllocationEngine(bsf_factor=0.63)
        # Item that's too tall, too heavy, and too large
        item = {**create_simple_item(height=20.0, area=1000.0, psf=500.0), 'id': 1}
        zone = {**create_simple_zone(height=12.0, area=100.0, strength=300.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        assert result['overall_fit'] is False
        failure = result['failures'][0]
        # Should have all three failure reasons
        assert 'Height too tall' in failure['failure_reason']
        assert 'Area too large' in failure['failure_reason']
        assert 'Too heavy' in failure['failure_reason']

    def test_can_theoretically_fit_flag(self):
        """Test can_theoretically_fit flag on failures."""
        engine = AllocationEngine(bsf_factor=0.63)
        # Item that only fails area constraint
        item = {**create_simple_item(height=6.0, area=200.0, psf=100.0), 'id': 1}
        zone = {**create_simple_zone(height=12.0, area=100.0, strength=300.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        failure = result['failures'][0]
        # Could theoretically fit if zone had more area
        assert failure['can_theoretically_fit'] is True

        # Now test item that can't theoretically fit (too tall)
        item2 = {**create_simple_item(height=20.0), 'id': 2}
        result2 = engine.allocate(items=[item2], zones=[zone])

        failure2 = result2['failures'][0]
        # Cannot fit even in empty zone (fundamental constraint)
        assert failure2['can_theoretically_fit'] is False


@pytest.mark.unit
class TestAllocationEngineSummary:
    """Test summary statistics calculation."""

    def test_summary_with_all_allocated(self):
        """Test summary when all items fit."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(quantity=5), 'id': 1}
        ]
        zone = {**create_simple_zone(area=1000.0), 'id': 1}

        result = engine.allocate(items=items, zones=[zone])

        summary = result['summary']
        assert summary['total_items'] == 5
        assert summary['total_allocated'] == 5
        assert summary['total_failed'] == 0
        assert summary['allocation_rate'] == 100.0
        assert summary['overall_utilization'] > 0
        assert summary['bsf_factor'] == 0.63

    def test_summary_with_partial_allocation(self):
        """Test summary when some items don't fit."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='Fits', height=6.0), 'id': 1},
            {**create_simple_item(name='Too Tall', height=20.0), 'id': 2}
        ]
        zone = {**create_simple_zone(height=12.0), 'id': 1}

        result = engine.allocate(items=items, zones=[zone])

        summary = result['summary']
        assert summary['total_items'] == 2
        assert summary['total_allocated'] == 1
        assert summary['total_failed'] == 1
        assert summary['allocation_rate'] == pytest.approx(50.0)

    def test_summary_zone_stats(self):
        """Test zone-level statistics in summary."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {**create_simple_item(), 'id': 1}
        zone = {**create_simple_zone(name='Test Zone'), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        zone_stats = result['summary']['zone_stats']
        assert len(zone_stats) == 1
        assert zone_stats[0]['zone_name'] == 'Test Zone'
        assert zone_stats[0]['total_items'] == 1
        assert zone_stats[0]['area_utilization'] > 0

    def test_utilization_calculation(self):
        """Test area utilization percentage calculation."""
        engine = AllocationEngine(bsf_factor=0.0)  # No BSF for easier math
        item = {**create_simple_item(area=250.0), 'id': 1}
        zone = {**create_simple_zone(area=1000.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        # Used 250 out of 1000 = 25%
        assert result['zone_allocations'][0]['area_utilization'] == pytest.approx(25.0)
        assert result['summary']['overall_utilization'] == pytest.approx(25.0)


@pytest.mark.unit
class TestAllocationEngineItemExpansion:
    """Test item quantity expansion logic."""

    def test_expand_items_with_quantities(self):
        """Test that items are expanded by quantity."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='Item 1', quantity=3), 'id': 1},
            {**create_simple_item(name='Item 2', quantity=2), 'id': 2}
        ]

        expanded = engine._expand_items(items)

        # Should have 5 individual items total
        assert len(expanded) == 5
        # First 3 should be Item 1
        assert sum(1 for item in expanded if item['item_id'] == 1) == 3
        # Last 2 should be Item 2
        assert sum(1 for item in expanded if item['item_id'] == 2) == 2

    def test_expand_items_preserves_properties(self):
        """Test that expanded items preserve all properties."""
        engine = AllocationEngine(bsf_factor=0.63)
        item = {
            **create_simple_item(
                name='Test',
                height=10.0,
                area=20.0,
                requires_climate=True,
                quantity=2
            ),
            'id': 1
        }

        expanded = engine._expand_items([item])

        assert len(expanded) == 2
        for expanded_item in expanded:
            assert expanded_item['item_id'] == 1
            assert expanded_item['name'] == 'Test'
            assert expanded_item['height'] == 10.0
            assert expanded_item['area'] == 20.0
            assert expanded_item['requires_climate_control'] is True


@pytest.mark.unit
class TestAllocationEngineConstraintTracking:
    """Test tracking of constrained items."""

    def test_height_constrained_tracking(self):
        """Test tracking of items that are close to height limit."""
        engine = AllocationEngine(bsf_factor=0.63)
        # Item within 6 inches (0.5 ft) of ceiling
        item = {**create_simple_item(height=11.6), 'id': 1}
        zone = {**create_simple_zone(height=12.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        zone_alloc = result['zone_allocations'][0]
        # Should be tracked as height constrained
        assert zone_alloc['height_constrained_items'] == 1

    def test_strength_constrained_tracking(self):
        """Test tracking of items using >90% of floor strength."""
        engine = AllocationEngine(bsf_factor=0.63)
        # Item at 91% of strength (300 * 0.91 = 273)
        item = {**create_simple_item(psf=273.0), 'id': 1}
        zone = {**create_simple_zone(strength=300.0), 'id': 1}

        result = engine.allocate(items=[item], zones=[zone])

        zone_alloc = result['zone_allocations'][0]
        # Should be tracked as strength constrained
        assert zone_alloc['strength_constrained_items'] == 1

    def test_max_equipment_psf_tracking(self):
        """Test tracking of maximum PSF in zone."""
        engine = AllocationEngine(bsf_factor=0.63)
        items = [
            {**create_simple_item(name='Light', psf=100.0), 'id': 1},
            {**create_simple_item(name='Heavy', psf=250.0), 'id': 2}
        ]
        zone = {**create_simple_zone(strength=300.0), 'id': 1}

        result = engine.allocate(items=items, zones=[zone])

        zone_alloc = result['zone_allocations'][0]
        # Should track the maximum PSF
        assert zone_alloc['max_equipment_psf'] == 250.0
