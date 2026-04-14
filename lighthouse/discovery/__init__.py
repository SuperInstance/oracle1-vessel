"""Discovery module — Fleet repo and capability scanner."""
from .fleet_scan import FleetScanner
from .capability import CapabilityMatcher

__all__ = ["FleetScanner", "CapabilityMatcher"]
