"""
Custom Lanes Module for v0.1.46

Provides YAML-based lane customization allowing users to define custom workflow lanes
beyond the built-in docs, standard, and heavy lanes. Supports schema validation,
lane merging, and registry management.

Key Classes:
    - LaneDefinition: Data structure for lane configuration
    - LaneRegistry: Manages built-in and custom lanes
    - LaneValidator: Validates YAML schemas and configurations

Key Functions:
    - load_custom_lanes(): Load lanes from YAML file
    - get_lane(): Retrieve lane by name with defaults
    - validate_lane(): Validate single lane configuration
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class QualityGateConfig:
    """Configuration for quality gates in a lane."""

    enabled: bool = True
    ruff: bool = True
    mypy: bool = True
    pytest: bool = True
    bandit: bool = True
    coverage_threshold: float = 70.0
    required_passes: List[str] = field(default_factory=lambda: ["ruff", "mypy", "pytest"])

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate quality gate configuration."""
        errors = []

        if self.coverage_threshold < 0 or self.coverage_threshold > 100:
            errors.append(f"coverage_threshold must be 0-100, got {self.coverage_threshold}")

        for gate in self.required_passes:
            if gate not in ["ruff", "mypy", "pytest", "bandit"]:
                errors.append(f"Unknown gate: {gate}")

        return len(errors) == 0, errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityGateConfig":
        """Create from dictionary, using defaults for missing keys."""
        return cls(
            enabled=data.get("enabled", True),
            ruff=data.get("ruff", True),
            mypy=data.get("mypy", True),
            pytest=data.get("pytest", True),
            bandit=data.get("bandit", True),
            coverage_threshold=float(data.get("coverage_threshold", 70.0)),
            required_passes=data.get("required_passes", ["ruff", "mypy", "pytest"]),
        )


@dataclass
class LaneDefinition:
    """Defines a workflow lane with stages and quality gates."""

    name: str
    description: str
    stages: List[int] = field(default_factory=list)
    quality_gates: QualityGateConfig = field(default_factory=QualityGateConfig)
    parallel: bool = False
    timeout: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate lane definition."""
        errors = []

        # Validate required fields
        if not self.name:
            errors.append("Lane name is required")
        if not self.description:
            errors.append("Lane description is required")

        # Validate stages
        if not self.stages:
            errors.append("At least one stage is required")
        for stage in self.stages:
            if not isinstance(stage, int) or stage < 0 or stage > 12:
                errors.append(f"Invalid stage number: {stage} (must be 0-12)")

        # Validate quality gates
        gates_valid, gate_errors = self.quality_gates.validate()
        if not gates_valid:
            errors.extend(gate_errors)

        # Validate timeout
        if self.timeout <= 0:
            errors.append(f"Timeout must be positive, got {self.timeout}")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "stages": self.stages,
            "quality_gates": asdict(self.quality_gates),
            "parallel": self.parallel,
            "timeout": self.timeout,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LaneDefinition":
        """Create LaneDefinition from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            stages=data.get("stages", []),
            quality_gates=QualityGateConfig.from_dict(data.get("quality_gates", {})),
            parallel=data.get("parallel", False),
            timeout=int(data.get("timeout", 3600)),
            metadata=data.get("metadata", {}),
        )


# ============================================================================
# Lane Registry & Management
# ============================================================================

class LaneValidator:
    """Validates lane configurations against schema."""

    VALID_LANES = {"docs", "standard", "heavy"}
    MIN_STAGE = 0
    MAX_STAGE = 12

    @staticmethod
    def validate_yaml_file(path: Path) -> Tuple[bool, List[str]]:
        """Validate YAML file syntax and structure."""
        errors = []

        if not path.exists():
            return True, []  # File doesn't exist, not an error

        if path.suffix.lower() not in [".yaml", ".yml"]:
            errors.append(f"File must be .yaml or .yml, got {path.suffix}")
            return False, errors

        try:
            with open(path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML: {str(e)}")
        except Exception as e:
            errors.append(f"Error reading file: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_stage_sequence(stages: List[int]) -> Tuple[bool, List[str]]:
        """Validate stage sequence."""
        errors = []

        if not stages:
            errors.append("At least one stage required")
            return False, errors

        for stage in stages:
            if not isinstance(stage, int):
                errors.append(f"Stage must be integer, got {type(stage)}")
            elif stage < LaneValidator.MIN_STAGE or stage > LaneValidator.MAX_STAGE:
                errors.append(f"Stage {stage} out of range (0-12)")

        # Check for duplicates
        if len(stages) != len(set(stages)):
            errors.append("Duplicate stages not allowed")

        return len(errors) == 0, errors

    @staticmethod
    def validate_lane_definition(lane: LaneDefinition) -> Tuple[bool, List[str]]:
        """Validate complete lane definition."""
        return lane.validate()


class LaneRegistry:
    """Manages workflow lanes (built-in and custom)."""

    # Built-in lanes
    BUILT_IN_LANES = {
        "docs": LaneDefinition(
            name="docs",
            description="Documentation-only changes (skip testing)",
            stages=[0, 1, 2, 3],
            quality_gates=QualityGateConfig(pytest=False, bandit=False),
            parallel=True,
            timeout=600,
        ),
        "standard": LaneDefinition(
            name="standard",
            description="Standard workflow (docs + code validation + tests)",
            stages=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            quality_gates=QualityGateConfig(),
            parallel=True,
            timeout=1800,
        ),
        "heavy": LaneDefinition(
            name="heavy",
            description="Heavy workflow (all stages including stress tests)",
            stages=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            quality_gates=QualityGateConfig(),
            parallel=False,
            timeout=3600,
        ),
    }

    def __init__(self):
        """Initialize lane registry with built-in lanes."""
        self.lanes: Dict[str, LaneDefinition] = {}
        self.custom_lanes_path: Optional[Path] = None
        self._load_built_in_lanes()

    def _load_built_in_lanes(self) -> None:
        """Load built-in lanes."""
        for name, lane in self.BUILT_IN_LANES.items():
            self.lanes[name] = lane
            logger.debug(f"Loaded built-in lane: {name}")

    def load_custom_lanes(self, path: Path) -> Tuple[bool, List[str]]:
        """Load custom lanes from YAML file."""
        errors = []

        # Validate file
        valid, file_errors = LaneValidator.validate_yaml_file(path)
        if not valid:
            return False, file_errors

        if not path.exists():
            logger.info(f"Custom lanes file not found: {path}")
            return True, []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                logger.info("Custom lanes file is empty")
                return True, []

            if not isinstance(data, dict):
                errors.append("YAML must be a dictionary of lanes")
                return False, errors

            # Load each lane
            for lane_name, lane_data in data.items():
                if not isinstance(lane_data, dict):
                    errors.append(f"Lane '{lane_name}' must be a dictionary")
                    continue

                try:
                    lane = LaneDefinition.from_dict(lane_data)
                    lane.name = lane_name  # Ensure name matches

                    # Validate lane
                    valid, lane_errors = LaneValidator.validate_lane_definition(lane)
                    if not valid:
                        errors.extend([f"Lane '{lane_name}': {err}" for err in lane_errors])
                        continue

                    self.lanes[lane_name] = lane
                    logger.debug(f"Loaded custom lane: {lane_name}")

                except Exception as e:
                    errors.append(f"Error loading lane '{lane_name}': {str(e)}")

            self.custom_lanes_path = path
            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Error reading custom lanes: {str(e)}"]

    def register_lane(
        self, name: str, definition: LaneDefinition, overwrite: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Register a new lane or update existing lane."""
        # Check if lane exists and is built-in
        if name in self.BUILT_IN_LANES and not overwrite:
            return False, f"Cannot override built-in lane '{name}' (use overwrite=True)"

        # Validate lane
        valid, errors = definition.validate()
        if not valid:
            return False, "; ".join(errors)

        self.lanes[name] = definition
        logger.debug(f"Registered lane: {name}")
        return True, None

    def get_lane(self, name: str) -> Optional[LaneDefinition]:
        """Get lane by name.
        
        Returns a copy to prevent external modifications.
        """
        lane = self.lanes.get(name)
        if lane is None:
            return None
        
        # Return a copy to prevent external modifications
        return LaneDefinition.from_dict(lane.to_dict())

    def list_lanes(self) -> Dict[str, LaneDefinition]:
        """Get all lanes."""
        return self.lanes.copy()

    def get_lane_names(self) -> List[str]:
        """Get list of all lane names."""
        return sorted(self.lanes.keys())

    def validate_all(self) -> Tuple[bool, List[str]]:
        """Validate all lanes."""
        errors = []

        for name, lane in self.lanes.items():
            valid, lane_errors = lane.validate()
            if not valid:
                errors.extend([f"Lane '{name}': {err}" for err in lane_errors])

        return len(errors) == 0, errors

    def merge_with_defaults(self) -> Dict[str, Any]:
        """Get all lanes merged with defaults."""
        result = {}

        for name, lane in self.lanes.items():
            result[name] = lane.to_dict()

        return result

    def export_to_yaml(self, path: Path) -> Tuple[bool, Optional[str]]:
        """Export all custom lanes to YAML file."""
        try:
            # Export only custom lanes (exclude built-in)
            custom_lanes = {}
            for name, lane in self.lanes.items():
                if name not in self.BUILT_IN_LANES:
                    custom_lanes[name] = lane.to_dict()

            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(custom_lanes, f, default_flow_style=False, sort_keys=False)

            logger.debug(f"Exported {len(custom_lanes)} custom lanes to {path}")
            return True, None

        except Exception as e:
            return False, f"Error exporting lanes: {str(e)}"


# ============================================================================
# Global Registry Instance
# ============================================================================

_global_registry: Optional[LaneRegistry] = None


def get_registry() -> LaneRegistry:
    """Get global lane registry instance (singleton)."""
    global _global_registry

    if _global_registry is None:
        _global_registry = LaneRegistry()

    return _global_registry


def initialize_registry(custom_lanes_path: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """Initialize global lane registry with optional custom lanes."""
    registry = get_registry()

    errors = []

    if custom_lanes_path:
        success, load_errors = registry.load_custom_lanes(custom_lanes_path)
        if not success:
            errors.extend(load_errors)

    # Validate all lanes
    valid, validation_errors = registry.validate_all()
    if not valid:
        errors.extend(validation_errors)

    return len(errors) == 0, errors


# ============================================================================
# Public API
# ============================================================================


def get_lane_by_name(name: str) -> Optional[LaneDefinition]:
    """Get lane by name from global registry."""
    registry = get_registry()
    return registry.get_lane(name)


def list_all_lanes() -> Dict[str, LaneDefinition]:
    """Get all lanes from global registry."""
    registry = get_registry()
    return registry.list_lanes()


def get_all_lane_names() -> List[str]:
    """Get all lane names from global registry."""
    registry = get_registry()
    return registry.get_lane_names()


def validate_lane(lane: LaneDefinition) -> Tuple[bool, List[str]]:
    """Validate a lane definition."""
    return LaneValidator.validate_lane_definition(lane)


def validate_yaml_file(path: Path) -> Tuple[bool, List[str]]:
    """Validate YAML file."""
    return LaneValidator.validate_yaml_file(path)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.DEBUG)

    # Create and use registry
    registry = LaneRegistry()
    print(f"Built-in lanes: {registry.get_lane_names()}")

    # Validate
    valid, errors = registry.validate_all()
    print(f"Valid: {valid}, Errors: {errors}")

    # Export to JSON for verification
    print("\nLanes structure:")
    print(json.dumps(registry.merge_with_defaults(), indent=2))
