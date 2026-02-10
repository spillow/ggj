"""
test_device_system.py

Unit tests for the DeviceState class that tracks the 5 Convergence Amplifier
components.
"""

import pytest
from src.core.device_state import DeviceState, ComponentStatus


class TestDeviceStateInit:
    """Tests for DeviceState initialization."""

    def test_all_components_start_missing(self):
        ds = DeviceState()
        for comp in DeviceState.COMPONENTS:
            assert not ds.is_component_built(comp)

    def test_has_five_components(self):
        ds = DeviceState()
        assert len(DeviceState.COMPONENTS) == 5

    def test_component_names(self):
        expected = [
            "device-frame",
            "wiring-harness",
            "power-core",
            "focusing-array",
            "convergence-device",
        ]
        assert DeviceState.COMPONENTS == expected

    def test_ae_phase_starts_at_zero(self):
        ds = DeviceState()
        assert ds.ae_phase == 0

    def test_count_built_starts_at_zero(self):
        ds = DeviceState()
        assert ds.count_built_components() == 0

    def test_count_missing_starts_at_five(self):
        ds = DeviceState()
        assert ds.count_missing_components() == 5

    def test_device_not_complete_initially(self):
        ds = DeviceState()
        assert not ds.is_device_complete()

    def test_get_built_components_empty_initially(self):
        ds = DeviceState()
        assert ds.get_built_components() == []

    def test_get_missing_components_all_initially(self):
        ds = DeviceState()
        assert ds.get_missing_components() == DeviceState.COMPONENTS


class TestBuildComponent:
    """Tests for building components."""

    def test_build_single_component(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        assert ds.is_component_built("device-frame")

    def test_build_component_updates_count(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        assert ds.count_built_components() == 1
        assert ds.count_missing_components() == 4

    def test_build_multiple_components(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        ds.build_component("wiring-harness")
        assert ds.count_built_components() == 2
        assert ds.count_missing_components() == 3

    def test_build_all_components_makes_complete(self):
        ds = DeviceState()
        for comp in DeviceState.COMPONENTS:
            ds.build_component(comp)
        assert ds.is_device_complete()
        assert ds.count_built_components() == 5
        assert ds.count_missing_components() == 0

    def test_build_invalid_component_raises(self):
        ds = DeviceState()
        with pytest.raises(ValueError, match="Unknown component"):
            ds.build_component("phaser-array")

    def test_build_already_built_is_idempotent(self):
        ds = DeviceState()
        ds.build_component("power-core")
        ds.build_component("power-core")
        assert ds.is_component_built("power-core")
        assert ds.count_built_components() == 1


class TestRemoveComponent:
    """Tests for removing components."""

    def test_remove_built_component(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        ds.remove_component("device-frame")
        assert not ds.is_component_built("device-frame")

    def test_remove_updates_count(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        ds.build_component("wiring-harness")
        ds.remove_component("device-frame")
        assert ds.count_built_components() == 1
        assert ds.count_missing_components() == 4

    def test_remove_invalid_component_raises(self):
        ds = DeviceState()
        with pytest.raises(ValueError, match="Unknown component"):
            ds.remove_component("flux-capacitor")

    def test_remove_already_missing_is_idempotent(self):
        ds = DeviceState()
        ds.remove_component("power-core")
        assert not ds.is_component_built("power-core")

    def test_remove_breaks_completeness(self):
        ds = DeviceState()
        for comp in DeviceState.COMPONENTS:
            ds.build_component(comp)
        assert ds.is_device_complete()
        ds.remove_component("convergence-device")
        assert not ds.is_device_complete()


class TestIsComponentBuilt:
    """Tests for is_component_built queries."""

    def test_invalid_component_raises(self):
        ds = DeviceState()
        with pytest.raises(ValueError, match="Unknown component"):
            ds.is_component_built("nonexistent")

    def test_each_component_individually(self):
        ds = DeviceState()
        for comp in DeviceState.COMPONENTS:
            assert not ds.is_component_built(comp)
            ds.build_component(comp)
            assert ds.is_component_built(comp)


class TestGetComponents:
    """Tests for get_built_components and get_missing_components."""

    def test_built_list_after_partial_build(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        ds.build_component("power-core")
        built = ds.get_built_components()
        assert "device-frame" in built
        assert "power-core" in built
        assert len(built) == 2

    def test_missing_list_after_partial_build(self):
        ds = DeviceState()
        ds.build_component("device-frame")
        ds.build_component("power-core")
        missing = ds.get_missing_components()
        assert "wiring-harness" in missing
        assert "focusing-array" in missing
        assert "convergence-device" in missing
        assert len(missing) == 3

    def test_built_and_missing_sum_to_five(self):
        ds = DeviceState()
        ds.build_component("wiring-harness")
        ds.build_component("focusing-array")
        ds.build_component("convergence-device")
        assert len(ds.get_built_components()) + len(ds.get_missing_components()) == 5
