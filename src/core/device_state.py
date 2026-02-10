"""
device_state.py

Tracks the state of the Convergence Amplifier device and its 5 components.
Each component can be BUILT or MISSING. The device is complete when all
components are BUILT.
"""

from __future__ import annotations

from enum import IntEnum


class ComponentStatus(IntEnum):
    """Status of an individual device component."""
    MISSING = 0
    BUILT = 1


class DeviceState:
    """
    Tracks the Convergence Amplifier's 5 components and the AE's build phase.

    Components:
        - device-frame: The physical frame (requires plywood, brackets, nails, hammer)
        - wiring-harness: Internal wiring (requires copper-wire, insulated-cable, soldering-iron)
        - power-core: Power source (requires battery-pack, copper-coil)
        - focusing-array: Signal focusing (requires crystal-oscillator, ice-cubes)
        - convergence-device: Final component (requires signal-amplifier)
    """

    COMPONENTS: list[str] = [
        "device-frame",
        "wiring-harness",
        "power-core",
        "focusing-array",
        "convergence-device",
    ]

    def __init__(self) -> None:
        """Initialize all components as MISSING and AE phase to 0."""
        self._components: dict[str, ComponentStatus] = {
            name: ComponentStatus.MISSING for name in self.COMPONENTS
        }
        self.ae_phase: int = 0  # 0 = not started, 1-5 = current phase

    def build_component(self, name: str) -> None:
        """
        Set a component's status to BUILT.

        Args:
            name: The component name (must be in COMPONENTS)

        Raises:
            ValueError: If the component name is not valid
        """
        if name not in self._components:
            raise ValueError(f"Unknown component: {name}")
        self._components[name] = ComponentStatus.BUILT

    def remove_component(self, name: str) -> None:
        """
        Set a component's status to MISSING.

        Args:
            name: The component name (must be in COMPONENTS)

        Raises:
            ValueError: If the component name is not valid
        """
        if name not in self._components:
            raise ValueError(f"Unknown component: {name}")
        self._components[name] = ComponentStatus.MISSING

    def is_component_built(self, name: str) -> bool:
        """
        Check whether a specific component is BUILT.

        Args:
            name: The component name

        Returns:
            True if the component is BUILT, False if MISSING

        Raises:
            ValueError: If the component name is not valid
        """
        if name not in self._components:
            raise ValueError(f"Unknown component: {name}")
        return self._components[name] == ComponentStatus.BUILT

    def count_built_components(self) -> int:
        """Return the number of BUILT components."""
        return sum(
            1 for status in self._components.values()
            if status == ComponentStatus.BUILT
        )

    def count_missing_components(self) -> int:
        """Return the number of MISSING components."""
        return sum(
            1 for status in self._components.values()
            if status == ComponentStatus.MISSING
        )

    def is_device_complete(self) -> bool:
        """Return True if all 5 components are BUILT."""
        return all(
            status == ComponentStatus.BUILT
            for status in self._components.values()
        )

    def get_built_components(self) -> list[str]:
        """Return a list of component names that are BUILT."""
        return [
            name for name, status in self._components.items()
            if status == ComponentStatus.BUILT
        ]

    def get_missing_components(self) -> list[str]:
        """Return a list of component names that are MISSING."""
        return [
            name for name, status in self._components.items()
            if status == ComponentStatus.MISSING
        ]
