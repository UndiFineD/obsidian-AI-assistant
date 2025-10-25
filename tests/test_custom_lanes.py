"""
Unit Tests for Custom Lanes Module (v0.1.46)

Tests for:
- Lane definition validation
- YAML schema validation
- Lane registry operations
- Custom lane loading and merging
- Error handling and edge cases
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from scripts.custom_lanes import (
    LaneDefinition,
    QualityGateConfig,
    LaneRegistry,
    LaneValidator,
    get_registry,
    get_lane_by_name,
    list_all_lanes,
    get_all_lane_names,
    validate_lane,
    validate_yaml_file,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def quality_gate_config() -> QualityGateConfig:
    """Create a quality gate configuration."""
    return QualityGateConfig(
        enabled=True,
        ruff=True,
        mypy=True,
        pytest=True,
        bandit=True,
        coverage_threshold=75.0,
        required_passes=["ruff", "mypy", "pytest"],
    )


@pytest.fixture
def lane_definition() -> LaneDefinition:
    """Create a lane definition."""
    return LaneDefinition(
        name="test_lane",
        description="Test lane for unit testing",
        stages=[0, 1, 2, 3, 4],
        quality_gates=QualityGateConfig(),
        parallel=True,
        timeout=1800,
        metadata={"owner": "test", "version": "1.0"},
    )


@pytest.fixture
def temp_yaml_file() -> Path:
    """Create a temporary YAML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def fresh_registry() -> LaneRegistry:
    """Create a fresh lane registry."""
    return LaneRegistry()


# ============================================================================
# Test QualityGateConfig
# ============================================================================


class TestQualityGateConfig:
    """Tests for QualityGateConfig."""

    def test_default_initialization(self):
        """Test default quality gate initialization."""
        config = QualityGateConfig()

        assert config.enabled is True
        assert config.ruff is True
        assert config.mypy is True
        assert config.pytest is True
        assert config.coverage_threshold == 70.0

    def test_custom_initialization(self, quality_gate_config):
        """Test custom quality gate initialization."""
        assert quality_gate_config.coverage_threshold == 75.0
        assert "ruff" in quality_gate_config.required_passes

    def test_validate_valid_config(self, quality_gate_config):
        """Test validation of valid config."""
        valid, errors = quality_gate_config.validate()

        assert valid is True
        assert len(errors) == 0

    def test_validate_invalid_coverage_threshold(self):
        """Test validation with invalid coverage threshold."""
        config = QualityGateConfig(coverage_threshold=150.0)
        valid, errors = config.validate()

        assert valid is False
        assert len(errors) > 0
        assert "coverage_threshold" in errors[0]

    def test_validate_invalid_gate(self):
        """Test validation with invalid gate."""
        config = QualityGateConfig(required_passes=["ruff", "invalid_gate"])
        valid, errors = config.validate()

        assert valid is False
        assert any("invalid_gate" in err for err in errors)

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "enabled": True,
            "ruff": False,
            "coverage_threshold": 80.0,
            "required_passes": ["ruff", "pytest"],
        }

        config = QualityGateConfig.from_dict(data)

        assert config.enabled is True
        assert config.ruff is False
        assert config.coverage_threshold == 80.0
        assert config.required_passes == ["ruff", "pytest"]

    def test_from_dict_with_defaults(self):
        """Test creating from dict with missing keys uses defaults."""
        data = {"enabled": True}

        config = QualityGateConfig.from_dict(data)

        assert config.enabled is True
        assert config.pytest is True  # Default
        assert config.coverage_threshold == 70.0  # Default


# ============================================================================
# Test LaneDefinition
# ============================================================================


class TestLaneDefinition:
    """Tests for LaneDefinition."""

    def test_valid_lane(self, lane_definition):
        """Test valid lane definition."""
        valid, errors = lane_definition.validate()

        assert valid is True
        assert len(errors) == 0

    def test_missing_name(self):
        """Test lane with missing name."""
        lane = LaneDefinition(name="", description="Test")
        valid, errors = lane.validate()

        assert valid is False
        assert any("name" in err.lower() for err in errors)

    def test_missing_stages(self):
        """Test lane with missing stages."""
        lane = LaneDefinition(name="test", description="Test", stages=[])
        valid, errors = lane.validate()

        assert valid is False
        assert any("stage" in err.lower() for err in errors)

    def test_invalid_stage_number(self):
        """Test lane with invalid stage number."""
        lane = LaneDefinition(
            name="test",
            description="Test",
            stages=[0, 1, 15],  # 15 is out of range
        )
        valid, errors = lane.validate()

        assert valid is False
        assert any("stage" in err.lower() for err in errors)

    def test_negative_timeout(self):
        """Test lane with negative timeout."""
        lane = LaneDefinition(name="test", description="Test", stages=[0, 1], timeout=-100)
        valid, errors = lane.validate()

        assert valid is False
        assert any("timeout" in err.lower() for err in errors)

    def test_to_dict(self, lane_definition):
        """Test converting lane to dictionary."""
        lane_dict = lane_definition.to_dict()

        assert lane_dict["name"] == lane_definition.name
        assert lane_dict["stages"] == lane_definition.stages
        assert lane_dict["parallel"] == lane_definition.parallel
        assert "quality_gates" in lane_dict

    def test_from_dict(self):
        """Test creating lane from dictionary."""
        data = {
            "name": "test_lane",
            "description": "Test lane",
            "stages": [0, 1, 2],
            "parallel": True,
            "timeout": 1800,
            "quality_gates": {"enabled": True, "coverage_threshold": 75.0},
            "metadata": {"owner": "test"},
        }

        lane = LaneDefinition.from_dict(data)

        assert lane.name == "test_lane"
        assert lane.stages == [0, 1, 2]
        assert lane.parallel is True
        assert lane.timeout == 1800

    def test_from_dict_with_defaults(self):
        """Test creating lane from minimal dict."""
        data = {"name": "test", "description": "Test", "stages": [0, 1]}

        lane = LaneDefinition.from_dict(data)

        assert lane.name == "test"
        assert lane.parallel is False  # Default
        assert lane.timeout == 3600  # Default


# ============================================================================
# Test LaneValidator
# ============================================================================


class TestLaneValidator:
    """Tests for LaneValidator."""

    def test_validate_valid_stages(self):
        """Test validation of valid stage sequence."""
        valid, errors = LaneValidator.validate_stage_sequence([0, 1, 2, 3])

        assert valid is True
        assert len(errors) == 0

    def test_validate_empty_stages(self):
        """Test validation of empty stages."""
        valid, errors = LaneValidator.validate_stage_sequence([])

        assert valid is False
        assert len(errors) > 0

    def test_validate_stage_out_of_range(self):
        """Test validation of out-of-range stage."""
        valid, errors = LaneValidator.validate_stage_sequence([0, 1, 15])

        assert valid is False
        assert len(errors) > 0

    def test_validate_duplicate_stages(self):
        """Test validation of duplicate stages."""
        valid, errors = LaneValidator.validate_stage_sequence([0, 1, 1, 2])

        assert valid is False
        assert any("duplicate" in err.lower() for err in errors)

    def test_validate_yaml_file_not_exists(self, temp_yaml_file):
        """Test validation of non-existent YAML file."""
        non_existent = temp_yaml_file.parent / "non_existent.yaml"
        valid, errors = LaneValidator.validate_yaml_file(non_existent)

        # Should not error if file doesn't exist
        assert valid is True
        assert len(errors) == 0

    def test_validate_yaml_file_invalid_syntax(self, temp_yaml_file):
        """Test validation of YAML with invalid syntax."""
        with open(temp_yaml_file, "w") as f:
            f.write("invalid: [yaml: syntax:")

        valid, errors = LaneValidator.validate_yaml_file(temp_yaml_file)

        assert valid is False
        assert len(errors) > 0

    def test_validate_yaml_file_wrong_extension(self, temp_yaml_file):
        """Test validation with wrong file extension."""
        wrong_ext = temp_yaml_file.parent / "file.txt"
        wrong_ext.write_text("test")

        valid, errors = LaneValidator.validate_yaml_file(wrong_ext)

        assert valid is False
        wrong_ext.unlink()

    def test_validate_lane_definition(self, lane_definition):
        """Test lane definition validation."""
        valid, errors = LaneValidator.validate_lane_definition(lane_definition)

        assert valid is True
        assert len(errors) == 0


# ============================================================================
# Test LaneRegistry
# ============================================================================


class TestLaneRegistry:
    """Tests for LaneRegistry."""

    def test_built_in_lanes_loaded(self, fresh_registry):
        """Test that built-in lanes are loaded."""
        lanes = fresh_registry.get_lane_names()

        assert "docs" in lanes
        assert "standard" in lanes
        assert "heavy" in lanes

    def test_get_lane_by_name(self, fresh_registry):
        """Test retrieving lane by name."""
        docs_lane = fresh_registry.get_lane("docs")

        assert docs_lane is not None
        assert docs_lane.name == "docs"
        assert len(docs_lane.stages) > 0

    def test_get_nonexistent_lane(self, fresh_registry):
        """Test retrieving non-existent lane."""
        lane = fresh_registry.get_lane("non_existent")

        assert lane is None

    def test_register_custom_lane(self, fresh_registry, lane_definition):
        """Test registering a custom lane."""
        success, error = fresh_registry.register_lane("custom", lane_definition)

        assert success is True
        assert error is None
        assert fresh_registry.get_lane("custom") is not None

    def test_register_invalid_lane(self, fresh_registry):
        """Test registering an invalid lane."""
        lane = LaneDefinition(name="test", description="", stages=[])  # Invalid
        success, error = fresh_registry.register_lane("test", lane)

        assert success is False
        assert error is not None

    def test_cannot_override_built_in_lane(self, fresh_registry, lane_definition):
        """Test that built-in lanes cannot be overridden."""
        success, error = fresh_registry.register_lane("docs", lane_definition)

        assert success is False
        assert "built-in" in error.lower()

    def test_override_built_in_with_flag(self, fresh_registry, lane_definition):
        """Test overriding built-in lane with overwrite flag."""
        success, error = fresh_registry.register_lane("docs", lane_definition, overwrite=True)

        assert success is True

    def test_list_lanes(self, fresh_registry):
        """Test listing all lanes."""
        lanes = fresh_registry.list_lanes()

        assert len(lanes) >= 3  # At least 3 built-in lanes
        assert "docs" in lanes
        assert isinstance(lanes["docs"], LaneDefinition)

    def test_validate_all_lanes(self, fresh_registry):
        """Test validating all lanes."""
        valid, errors = fresh_registry.validate_all()

        assert valid is True
        assert len(errors) == 0

    def test_merge_with_defaults(self, fresh_registry):
        """Test merging lanes with defaults."""
        merged = fresh_registry.merge_with_defaults()

        assert "docs" in merged
        assert "standard" in merged
        assert "heavy" in merged
        assert merged["docs"]["name"] == "docs"

    def test_export_to_yaml(self, fresh_registry, temp_yaml_file):
        """Test exporting lanes to YAML."""
        # Add a custom lane first
        lane = LaneDefinition(
            name="custom",
            description="Custom lane",
            stages=[0, 1, 2],
        )
        fresh_registry.register_lane("custom", lane)

        # Export
        success, error = fresh_registry.export_to_yaml(temp_yaml_file)

        assert success is True
        assert error is None
        assert temp_yaml_file.exists()

        # Verify exported content
        with open(temp_yaml_file) as f:
            data = yaml.safe_load(f)

        assert "custom" in data
        assert data["custom"]["name"] == "custom"


# ============================================================================
# Test Custom Lane Loading
# ============================================================================


class TestCustomLaneLoading:
    """Tests for loading custom lanes from YAML."""

    def test_load_valid_custom_lanes(self, fresh_registry, temp_yaml_file):
        """Test loading valid custom lanes."""
        custom_lanes = {
            "fast": {
                "name": "fast",
                "description": "Fast lane",
                "stages": [0, 1],
                "timeout": 300,
            },
            "full": {
                "name": "full",
                "description": "Full lane",
                "stages": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "timeout": 3600,
            },
        }

        with open(temp_yaml_file, "w") as f:
            yaml.dump(custom_lanes, f)

        success, errors = fresh_registry.load_custom_lanes(temp_yaml_file)

        assert success is True
        assert len(errors) == 0
        assert fresh_registry.get_lane("fast") is not None
        assert fresh_registry.get_lane("full") is not None

    def test_load_custom_lanes_with_invalid_entry(self, fresh_registry, temp_yaml_file):
        """Test loading custom lanes with invalid entry."""
        custom_lanes = {
            "valid": {
                "name": "valid",
                "description": "Valid lane",
                "stages": [0, 1],
            },
            "invalid": {
                "name": "invalid",
                "description": "Invalid lane",
                "stages": [],  # Invalid: no stages
            },
        }

        with open(temp_yaml_file, "w") as f:
            yaml.dump(custom_lanes, f)

        success, errors = fresh_registry.load_custom_lanes(temp_yaml_file)

        assert success is False
        assert len(errors) > 0
        # Valid lane should still be loaded
        assert fresh_registry.get_lane("valid") is not None

    def test_load_custom_lanes_empty_file(self, fresh_registry, temp_yaml_file):
        """Test loading empty custom lanes file."""
        temp_yaml_file.write_text("")

        success, errors = fresh_registry.load_custom_lanes(temp_yaml_file)

        assert success is True
        assert len(errors) == 0

    def test_load_custom_lanes_malformed_yaml(self, fresh_registry, temp_yaml_file):
        """Test loading malformed YAML file."""
        temp_yaml_file.write_text("invalid: [yaml: syntax:")

        success, errors = fresh_registry.load_custom_lanes(temp_yaml_file)

        assert success is False
        assert len(errors) > 0

    def test_load_custom_lanes_not_found(self, fresh_registry):
        """Test loading non-existent custom lanes file."""
        non_existent = Path("/tmp/non_existent_lanes_12345.yaml")

        success, errors = fresh_registry.load_custom_lanes(non_existent)

        # Should succeed silently (file not found is OK)
        assert success is True
        assert len(errors) == 0


# ============================================================================
# Test Public API
# ============================================================================


class TestPublicAPI:
    """Tests for public API functions."""

    def test_get_lane_by_name_api(self):
        """Test public get_lane_by_name function."""
        lane = get_lane_by_name("docs")

        assert lane is not None
        assert lane.name == "docs"

    def test_list_all_lanes_api(self):
        """Test public list_all_lanes function."""
        lanes = list_all_lanes()

        assert len(lanes) >= 3
        assert "docs" in lanes
        assert "standard" in lanes
        assert "heavy" in lanes

    def test_get_all_lane_names_api(self):
        """Test public get_all_lane_names function."""
        names = get_all_lane_names()

        assert "docs" in names
        assert "standard" in names
        assert "heavy" in names

    def test_validate_lane_api(self, lane_definition):
        """Test public validate_lane function."""
        valid, errors = validate_lane(lane_definition)

        assert valid is True
        assert len(errors) == 0

    def test_validate_yaml_file_api(self, temp_yaml_file):
        """Test public validate_yaml_file function."""
        custom_lanes = {
            "test": {
                "name": "test",
                "description": "Test",
                "stages": [0, 1],
            }
        }

        with open(temp_yaml_file, "w") as f:
            yaml.dump(custom_lanes, f)

        valid, errors = validate_yaml_file(temp_yaml_file)

        assert valid is True
        assert len(errors) == 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for custom lanes."""

    def test_full_workflow(self, temp_yaml_file):
        """Test complete custom lanes workflow."""
        # 1. Create custom lanes file
        custom_lanes = {
            "fast": {
                "name": "fast",
                "description": "Fast CI lane",
                "stages": [0, 1, 2],
                "timeout": 600,
                "parallel": True,
                "quality_gates": {
                    "enabled": True,
                    "ruff": True,
                    "coverage_threshold": 50.0,
                },
            }
        }

        with open(temp_yaml_file, "w") as f:
            yaml.dump(custom_lanes, f)

        # 2. Create registry and load lanes
        registry = LaneRegistry()
        success, errors = registry.load_custom_lanes(temp_yaml_file)

        assert success is True
        assert len(errors) == 0

        # 3. Retrieve and validate lane
        lane = registry.get_lane("fast")

        assert lane is not None
        assert lane.stages == [0, 1, 2]
        assert lane.timeout == 600

        # 4. Merge with defaults
        merged = registry.merge_with_defaults()

        assert len(merged) >= 4  # 3 built-in + 1 custom
        assert "fast" in merged
        assert "docs" in merged

        # 5. Validate all
        valid, errors = registry.validate_all()

        assert valid is True
        assert len(errors) == 0

    def test_lane_stages_coverage(self):
        """Test that lanes cover expected stage ranges."""
        registry = LaneRegistry()

        docs_lane = registry.get_lane("docs")
        assert len(docs_lane.stages) == 4  # Minimal testing

        standard_lane = registry.get_lane("standard")
        assert len(standard_lane.stages) == 10  # Full validation + testing

        heavy_lane = registry.get_lane("heavy")
        assert len(heavy_lane.stages) == 13  # All stages

    def test_built_in_lane_immutability(self):
        """Test that modifying retrieved lane doesn't affect registry."""
        registry = LaneRegistry()

        docs_lane = registry.get_lane("docs")
        original_timeout = docs_lane.timeout

        # Attempt to modify
        docs_lane.timeout = 9999

        # Verify registry copy is unchanged
        fresh_lane = registry.get_lane("docs")
        assert fresh_lane.timeout == original_timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
