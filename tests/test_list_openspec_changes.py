"""
Tests for list_openspec_changes.py backlog management tool.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add scripts to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from list_openspec_changes import (
    generate_burndown_data,
    generate_summary_stats,
    get_change_age_days,
    list_active_changes,
    parse_change_id,
    render_ascii_burndown,
)


class TestParseChangeId:
    """Test change ID parsing."""

    def test_parse_with_date_prefix(self):
        """Test parsing change ID with date prefix."""
        result = parse_change_id("2025-10-18-my-feature")

        assert result["id"] == "2025-10-18-my-feature"
        assert result["date"] == datetime(2025, 10, 18)
        assert result["description"] == "my-feature"
        assert result["has_date"] is True

    def test_parse_without_date_prefix(self):
        """Test parsing change ID without date prefix."""
        result = parse_change_id("my-feature")

        assert result["id"] == "my-feature"
        assert result["date"] is None
        assert result["description"] == "my-feature"
        assert result["has_date"] is False

    def test_parse_invalid_date(self):
        """Test parsing change ID with invalid date."""
        result = parse_change_id("2025-13-32-invalid")

        assert result["id"] == "2025-13-32-invalid"
        assert result["date"] is None
        assert result["description"] == "2025-13-32-invalid"
        assert result["has_date"] is False

    def test_parse_complex_description(self):
        """Test parsing with complex description."""
        result = parse_change_id("2025-10-18-feature-with-many-dashes")

        assert result["date"] == datetime(2025, 10, 18)
        assert result["description"] == "feature-with-many-dashes"


class TestGetChangeAgeDays:
    """Test age calculation."""

    def test_age_calculation_today(self):
        """Test age for change created today."""
        change_info = {"has_date": True, "date": datetime.now()}

        age = get_change_age_days(change_info)
        assert age == 0

    def test_age_calculation_past(self):
        """Test age for change created in past."""
        change_info = {"has_date": True, "date": datetime.now() - timedelta(days=5)}

        age = get_change_age_days(change_info)
        assert age == 5

    def test_age_no_date(self):
        """Test age when no date available."""
        change_info = {"has_date": False, "date": None}

        age = get_change_age_days(change_info)
        assert age is None


class TestListActiveChanges:
    """Test listing active changes."""

    def test_list_changes_exists(self):
        """Test that listing returns results from actual workspace."""
        # Find real changes directory
        script_dir = Path(__file__).parent.parent / "scripts"
        project_root = script_dir.parent
        changes_dir = project_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("Changes directory not found")

        changes = list_active_changes(changes_dir, exclude_archive=True)

        # Should have some changes
        assert len(changes) > 0

        # Each change should have required fields
        for change in changes:
            assert "id" in change
            assert "date" in change or change["date"] is None
            assert "description" in change
            assert "has_date" in change
            assert "age_days" in change or change["age_days"] is None
            assert "path" in change

    def test_exclude_archive(self):
        """Test that archive directory is excluded."""
        script_dir = Path(__file__).parent.parent / "scripts"
        project_root = script_dir.parent
        changes_dir = project_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("Changes directory not found")

        changes = list_active_changes(changes_dir, exclude_archive=True)

        # No change should be named 'archive'
        for change in changes:
            assert change["id"] != "archive"

    def test_include_archive(self):
        """Test including archive if it exists."""
        script_dir = Path(__file__).parent.parent / "scripts"
        project_root = script_dir.parent
        changes_dir = project_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("Changes directory not found")

        # Check if archive exists
        archive_dir = changes_dir / "archive"
        if not archive_dir.exists():
            pytest.skip("Archive directory not found")

        changes = list_active_changes(changes_dir, exclude_archive=False)

        # Archive should be in list
        archive_ids = [c["id"] for c in changes]
        assert "archive" in archive_ids


class TestGenerateSummaryStats:
    """Test summary statistics generation."""

    def test_summary_with_dates(self):
        """Test summary stats with dated changes."""
        changes = [
            {
                "id": "2025-10-18-feature1",
                "has_date": True,
                "date": datetime.now(),
                "age_days": 0,
            },
            {
                "id": "2025-10-10-feature2",
                "has_date": True,
                "date": datetime.now() - timedelta(days=8),
                "age_days": 8,
            },
            {"id": "feature3", "has_date": False, "date": None, "age_days": None},
        ]

        stats = generate_summary_stats(changes)

        assert stats["total"] == 3
        assert stats["with_dates"] == 2
        assert stats["without_dates"] == 1
        assert stats["avg_age_days"] == 4.0  # (0 + 8) / 2
        assert stats["max_age_days"] == 8
        assert stats["min_age_days"] == 0
        assert stats["stale_count"] == 0

    def test_summary_stale_changes(self):
        """Test stale change detection (>30 days)."""
        changes = [
            {
                "id": "2025-01-01-old",
                "has_date": True,
                "date": datetime.now() - timedelta(days=60),
                "age_days": 60,
            },
            {
                "id": "2025-10-01-recent",
                "has_date": True,
                "date": datetime.now() - timedelta(days=17),
                "age_days": 17,
            },
        ]

        stats = generate_summary_stats(changes)

        assert stats["stale_count"] == 1

    def test_summary_no_dates(self):
        """Test summary with no dated changes."""
        changes = [
            {"id": "feature1", "has_date": False, "date": None, "age_days": None}
        ]

        stats = generate_summary_stats(changes)

        assert stats["total"] == 1
        assert stats["with_dates"] == 0
        assert stats["avg_age_days"] is None
        assert stats["max_age_days"] is None


class TestGenerateBurndownData:
    """Test burndown chart data generation."""

    def test_burndown_basic(self):
        """Test basic burndown data generation."""
        changes = [
            {
                "id": "2025-10-01-change1",
                "has_date": True,
                "date": datetime.now() - timedelta(days=10),
            },
            {
                "id": "2025-10-05-change2",
                "has_date": True,
                "date": datetime.now() - timedelta(days=6),
            },
            {"id": "2025-10-15-change3", "has_date": True, "date": datetime.now()},
        ]

        burndown_data = generate_burndown_data(changes, days=15)

        # Should have 16 data points (15 days + today)
        assert len(burndown_data) == 16

        # First data point should have 0 or 1 changes
        assert burndown_data[0][1] <= 1

        # Last data point should have all 3 changes
        assert burndown_data[-1][1] == 3

        # Counts should be non-decreasing (changes accumulate)
        counts = [count for _, count in burndown_data]
        for i in range(1, len(counts)):
            assert counts[i] >= counts[i - 1]

    def test_burndown_no_dated_changes(self):
        """Test burndown with no dated changes."""
        changes = [{"id": "change1", "has_date": False, "date": None}]

        burndown_data = generate_burndown_data(changes, days=30)

        assert len(burndown_data) == 0

    def test_burndown_custom_days(self):
        """Test burndown with custom day range."""
        changes = [
            {
                "id": "2025-10-01-change1",
                "has_date": True,
                "date": datetime.now() - timedelta(days=5),
            }
        ]

        burndown_data = generate_burndown_data(changes, days=7)

        # Should have 8 data points (7 days + today)
        assert len(burndown_data) == 8


class TestRenderAsciiBurndown:
    """Test ASCII burndown chart rendering."""

    def test_render_basic_chart(self):
        """Test basic chart rendering."""
        burndown_data = [
            (datetime.now() - timedelta(days=5), 1),
            (datetime.now() - timedelta(days=4), 2),
            (datetime.now() - timedelta(days=3), 3),
            (datetime.now() - timedelta(days=2), 3),
            (datetime.now() - timedelta(days=1), 4),
            (datetime.now(), 5),
        ]

        chart = render_ascii_burndown(burndown_data)

        # Should contain chart elements
        assert "Burndown Chart" in chart
        assert "│" in chart  # Y-axis
        assert "─" in chart  # X-axis
        assert "█" in chart  # Chart bars
        assert "Current:" in chart
        assert "Peak:" in chart
        assert "Trend:" in chart

    def test_render_empty_data(self):
        """Test rendering with no data."""
        chart = render_ascii_burndown([])

        assert "No data available" in chart

    def test_render_custom_dimensions(self):
        """Test rendering with custom width and height."""
        burndown_data = [
            (datetime.now() - timedelta(days=2), 2),
            (datetime.now() - timedelta(days=1), 3),
            (datetime.now(), 4),
        ]

        chart = render_ascii_burndown(burndown_data, width=40, height=10)

        # Should still contain chart elements
        assert "Burndown Chart" in chart
        assert "│" in chart

    def test_render_trend_calculation(self):
        """Test trend indicator in rendered chart."""
        # Increasing trend
        burndown_data_up = [
            (datetime.now() - timedelta(days=2), 2),
            (datetime.now() - timedelta(days=1), 3),
            (datetime.now(), 5),
        ]

        chart_up = render_ascii_burndown(burndown_data_up)
        assert "+3" in chart_up or "Trend:   +3" in chart_up

        # Decreasing trend
        burndown_data_down = [
            (datetime.now() - timedelta(days=2), 5),
            (datetime.now() - timedelta(days=1), 3),
            (datetime.now(), 2),
        ]

        chart_down = render_ascii_burndown(burndown_data_down)
        assert "-3" in chart_down or "Trend:   -3" in chart_down


class TestIntegration:
    """Integration tests using real workspace data."""

    def test_full_workflow(self):
        """Test complete workflow from listing to rendering."""
        script_dir = Path(__file__).parent.parent / "scripts"
        project_root = script_dir.parent
        changes_dir = project_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("Changes directory not found")

        # List changes
        changes = list_active_changes(changes_dir, exclude_archive=True)
        assert len(changes) > 0

        # Generate stats
        stats = generate_summary_stats(changes)
        assert stats["total"] == len(changes)
        assert stats["with_dates"] + stats["without_dates"] == stats["total"]

        # Generate burndown data
        burndown_data = generate_burndown_data(changes, days=30)

        # Render chart if data available
        if burndown_data:
            chart = render_ascii_burndown(burndown_data)
            assert "Burndown Chart" in chart
            assert len(chart) > 100  # Chart should have substantial content

    def test_sorting_by_age(self):
        """Test sorting changes by age."""
        script_dir = Path(__file__).parent.parent / "scripts"
        project_root = script_dir.parent
        changes_dir = project_root / "openspec" / "changes"

        if not changes_dir.exists():
            pytest.skip("Changes directory not found")

        changes = list_active_changes(changes_dir, exclude_archive=True)

        # Sort by age
        aged_changes = [c for c in changes if c["age_days"] is not None]
        if len(aged_changes) > 1:
            sorted_changes = sorted(
                aged_changes, key=lambda c: c["age_days"], reverse=True
            )

            # Verify sorting
            for i in range(1, len(sorted_changes)):
                assert (
                    sorted_changes[i - 1]["age_days"] >= sorted_changes[i]["age_days"]
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
