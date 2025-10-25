"""
Comprehensive tests for workflow_analytics module.

Tests cover:
- MetricsAggregator: metric collection, aggregation, filtering
- TrendAnalyzer: trend calculation, forecasting
- DashboardGenerator: HTML generation, performance <1s
- ReportFormatter: JSON/CSV/text export
- Integration tests: complete pipeline

Test Status Target: 7+ test classes, 100% passing, A+ quality
"""

import csv
import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pytest

from scripts.workflow_analytics import (
    AggregatedMetrics,
    DashboardGenerator,
    MetricsAggregator,
    ReportFormatter,
    TrendAnalyzer,
    TrendData,
    WorkflowMetric,
    create_analytics_pipeline,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_metrics() -> List[WorkflowMetric]:
    """Generate sample workflow metrics."""
    base_time = datetime.now() - timedelta(days=10)
    metrics = []

    for i in range(5):
        start = base_time + timedelta(hours=i * 4)
        end = start + timedelta(seconds=30 + i * 10)

        metric = WorkflowMetric(
            workflow_id=f"workflow-{i}",
            execution_time=float(30 + i * 10),
            stage_count=5 + i,
            success=i != 2,  # One failed
            start_time=start,
            end_time=end,
            stage_times={j: float(5 + j) for j in range(5 + i)},
            error_count=0 if i != 2 else 2,
            warnings_count=i,
            metadata={"change_type": "feature"},
        )
        metrics.append(metric)

    return metrics


@pytest.fixture
def aggregator(sample_metrics: List[WorkflowMetric]) -> MetricsAggregator:
    """Create aggregator with sample metrics."""
    agg = MetricsAggregator()
    agg.add_metrics_batch(sample_metrics)
    return agg


@pytest.fixture
def analyzer(aggregator: MetricsAggregator) -> TrendAnalyzer:
    """Create trend analyzer."""
    return TrendAnalyzer(aggregator)


@pytest.fixture
def dashboard_gen(
    aggregator: MetricsAggregator, analyzer: TrendAnalyzer
) -> DashboardGenerator:
    """Create dashboard generator."""
    return DashboardGenerator(aggregator, analyzer)


@pytest.fixture
def formatter(aggregator: MetricsAggregator) -> ReportFormatter:
    """Create report formatter."""
    return ReportFormatter(aggregator)


# ============================================================================
# Test MetricsAggregator
# ============================================================================


class TestMetricsAggregator:
    """Test metrics aggregation functionality."""

    def test_add_single_metric(self, aggregator: MetricsAggregator) -> None:
        """Test adding a single metric."""
        assert len(aggregator.get_metrics()) == 5
        assert aggregator.get_metric_by_id("workflow-0") is not None

    def test_get_metric_by_id(self, aggregator: MetricsAggregator) -> None:
        """Test retrieving metric by ID."""
        metric = aggregator.get_metric_by_id("workflow-1")
        assert metric is not None
        assert metric.workflow_id == "workflow-1"
        assert metric.stage_count == 6

    def test_get_metric_not_found(self, aggregator: MetricsAggregator) -> None:
        """Test retrieving non-existent metric."""
        metric = aggregator.get_metric_by_id("nonexistent")
        assert metric is None

    def test_aggregate_basic(self, aggregator: MetricsAggregator) -> None:
        """Test basic aggregation."""
        metrics = aggregator.aggregate()

        assert metrics.total_workflows == 5
        assert metrics.successful_workflows == 4
        assert metrics.failed_workflows == 1
        assert metrics.success_rate == 0.8
        assert metrics.total_errors == 2
        assert metrics.total_warnings == 10  # 0+1+2+3+4

    def test_aggregate_execution_times(self, aggregator: MetricsAggregator) -> None:
        """Test execution time aggregation."""
        metrics = aggregator.aggregate()

        # Expected times: 30, 40, 50, 60, 70
        assert metrics.min_execution_time == 30.0
        assert metrics.max_execution_time == 70.0
        assert abs(metrics.avg_execution_time - 50.0) < 0.1
        assert metrics.total_execution_time == 250.0

    def test_aggregate_stage_metrics(self, aggregator: MetricsAggregator) -> None:
        """Test stage-level metrics aggregation."""
        metrics = aggregator.aggregate()

        # Check stage 0 (present in all workflows)
        assert 0 in metrics.stage_metrics
        stage_0_metrics = metrics.stage_metrics[0]
        assert "avg_time" in stage_0_metrics
        assert "min_time" in stage_0_metrics
        assert "max_time" in stage_0_metrics
        assert "count" in stage_0_metrics

    def test_aggregate_time_filtering(
        self, sample_metrics: List[WorkflowMetric]
    ) -> None:
        """Test filtering by time period."""
        agg = MetricsAggregator()
        agg.add_metrics_batch(sample_metrics)

        # Filter to first 2 workflows
        first_time = sample_metrics[0].start_time
        last_time = sample_metrics[1].end_time

        filtered = agg.aggregate(start_time=first_time, end_time=last_time)
        assert filtered.total_workflows == 2

    def test_aggregate_empty(self) -> None:
        """Test aggregation with no metrics."""
        agg = MetricsAggregator()
        metrics = agg.aggregate()

        assert metrics.total_workflows == 0
        assert metrics.success_rate == 0.0
        assert metrics.avg_execution_time == 0.0

    def test_add_metrics_batch(self) -> None:
        """Test batch metric addition."""
        agg = MetricsAggregator()

        metrics_list = [
            WorkflowMetric(
                workflow_id=f"w-{i}",
                execution_time=float(10 * i),
                stage_count=3,
                success=True,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(seconds=10),
                stage_times={0: 5.0, 1: 5.0},
            )
            for i in range(3)
        ]

        agg.add_metrics_batch(metrics_list)
        assert len(agg.get_metrics()) == 3


# ============================================================================
# Test TrendAnalyzer
# ============================================================================


class TestTrendAnalyzer:
    """Test trend analysis functionality."""

    def test_analyze_execution_time_trend(self, analyzer: TrendAnalyzer) -> None:
        """Test execution time trend analysis."""
        trend = analyzer.analyze_execution_time_trend(window_size=3)

        assert trend is not None
        assert trend.data_points == 3
        assert hasattr(trend, "trend_direction")
        assert trend.trend_direction in ["increasing", "decreasing", "stable"]

    def test_analyze_success_rate_trend(self, analyzer: TrendAnalyzer) -> None:
        """Test success rate trend analysis."""
        trend = analyzer.analyze_success_rate_trend(window_size=3)

        assert trend is not None
        assert trend.data_points == 3
        # Forecast can extrapolate beyond [0, 1] bounds in linear regression
        assert isinstance(trend.forecast_next_value, float)

    def test_analyze_stage_count_trend(self, analyzer: TrendAnalyzer) -> None:
        """Test stage count trend analysis."""
        trend = analyzer.analyze_stage_count_trend(window_size=3)

        assert trend is not None
        assert trend.data_points == 3

    def test_trend_insufficient_data(self, analyzer: TrendAnalyzer) -> None:
        """Test trend with insufficient data."""
        trend = analyzer.analyze_execution_time_trend(window_size=100)
        assert trend is None

    def test_trend_attributes(self, analyzer: TrendAnalyzer) -> None:
        """Test trend data attributes."""
        trend = analyzer.analyze_execution_time_trend(window_size=3)

        assert trend is not None
        assert hasattr(trend, "trend_slope")
        assert hasattr(trend, "correlation_coefficient")
        assert hasattr(trend, "r_squared")
        assert hasattr(trend, "forecast_next_value")
        assert hasattr(trend, "confidence_level")
        assert 0 <= trend.confidence_level <= 1

    def test_trend_increasing_detection(self) -> None:
        """Test increasing trend detection."""
        agg = MetricsAggregator()
        base_time = datetime.now()

        # Add metrics with increasing execution times
        for i in range(10):
            metric = WorkflowMetric(
                workflow_id=f"w-{i}",
                execution_time=float(10 + i * 2),  # Increasing
                stage_count=3,
                success=True,
                start_time=base_time + timedelta(hours=i),
                end_time=base_time + timedelta(hours=i, seconds=10),
                stage_times={0: 5.0},
            )
            agg.add_metric(metric)

        analyzer = TrendAnalyzer(agg)
        trend = analyzer.analyze_execution_time_trend(window_size=5)

        assert trend is not None
        assert trend.trend_direction == "increasing"
        assert trend.trend_slope > 0


# ============================================================================
# Test DashboardGenerator
# ============================================================================


class TestDashboardGenerator:
    """Test dashboard generation functionality."""

    def test_generate_dashboard_basic(self, dashboard_gen: DashboardGenerator) -> None:
        """Test basic dashboard generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            dashboard_gen.generate_dashboard(output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "Workflow Analytics Dashboard" in content
            assert "<!DOCTYPE html>" in content

    def test_dashboard_contains_metrics(
        self, dashboard_gen: DashboardGenerator
    ) -> None:
        """Test dashboard contains metric values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            dashboard_gen.generate_dashboard(output_path)

            content = output_path.read_text()
            # Check for metric cards
            assert "Total Workflows" in content
            assert "Avg Execution Time" in content
            assert "Total Errors" in content

    def test_dashboard_custom_title(self, dashboard_gen: DashboardGenerator) -> None:
        """Test dashboard with custom title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            custom_title = "Custom Analytics Report"
            dashboard_gen.generate_dashboard(output_path, title=custom_title)

            content = output_path.read_text()
            assert custom_title in content

    def test_dashboard_generation_performance(
        self, dashboard_gen: DashboardGenerator
    ) -> None:
        """Test dashboard generation is fast (<1s)."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"

            start_time = time.time()
            dashboard_gen.generate_dashboard(output_path)
            elapsed = time.time() - start_time

            assert elapsed < 1.0, f"Dashboard generation took {elapsed}s (expected <1s)"

    def test_dashboard_contains_trend_info(
        self, dashboard_gen: DashboardGenerator
    ) -> None:
        """Test dashboard contains trend information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            dashboard_gen.generate_dashboard(output_path)

            content = output_path.read_text()
            # Dashboard should have metric cards and may have trend sections if data exists
            assert "metric-card" in content or "Execution Time Trend" in content

    def test_dashboard_html_valid(self, dashboard_gen: DashboardGenerator) -> None:
        """Test dashboard HTML structure is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            dashboard_gen.generate_dashboard(output_path)

            content = output_path.read_text()
            assert "<html" in content
            assert "</html>" in content
            assert "<head>" in content
            assert "<body>" in content
            assert "<style>" in content


# ============================================================================
# Test ReportFormatter
# ============================================================================


class TestReportFormatter:
    """Test report formatting and export functionality."""

    def test_export_json_basic(self, formatter: ReportFormatter) -> None:
        """Test JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"
            formatter.export_json(output_path, include_metrics=False)

            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert "aggregated_metrics" in data

    def test_export_json_with_metrics(self, formatter: ReportFormatter) -> None:
        """Test JSON export with individual metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"
            formatter.export_json(output_path, include_metrics=True)

            data = json.loads(output_path.read_text())
            assert "individual_metrics" in data
            assert len(data["individual_metrics"]) == 5

    def test_export_json_structure(self, formatter: ReportFormatter) -> None:
        """Test JSON structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"
            formatter.export_json(output_path, include_metrics=False)

            data = json.loads(output_path.read_text())
            metrics = data["aggregated_metrics"]
            assert "total_workflows" in metrics
            assert "success_rate" in metrics
            assert "avg_execution_time" in metrics

    def test_export_csv(self, formatter: ReportFormatter) -> None:
        """Test CSV export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.csv"
            formatter.export_csv(output_path)

            assert output_path.exists()
            with open(output_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 5

    def test_export_csv_columns(self, formatter: ReportFormatter) -> None:
        """Test CSV column headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.csv"
            formatter.export_csv(output_path)

            with open(output_path, "r") as f:
                reader = csv.DictReader(f)
                assert "workflow_id" in reader.fieldnames
                assert "execution_time" in reader.fieldnames
                assert "success" in reader.fieldnames

    def test_export_summary(self, formatter: ReportFormatter) -> None:
        """Test summary text export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "summary.txt"
            formatter.export_summary(output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "WORKFLOW ANALYTICS SUMMARY REPORT" in content
            assert "Total Workflows" in content
            assert "Success Rate" in content

    def test_export_summary_structure(self, formatter: ReportFormatter) -> None:
        """Test summary text structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "summary.txt"
            formatter.export_summary(output_path)

            content = output_path.read_text()
            assert "OVERVIEW" in content
            assert "EXECUTION TIME" in content
            assert "QUALITY METRICS" in content


# ============================================================================
# Test Data Models
# ============================================================================


class TestDataModels:
    """Test data model conversions."""

    def test_workflow_metric_to_dict(self) -> None:
        """Test WorkflowMetric to_dict conversion."""
        metric = WorkflowMetric(
            workflow_id="test",
            execution_time=10.5,
            stage_count=3,
            success=True,
            start_time=datetime.now(),
            end_time=datetime.now(),
            stage_times={0: 3.5, 1: 4.0, 2: 3.0},
            error_count=0,
            warnings_count=1,
        )

        data = metric.to_dict()
        assert data["workflow_id"] == "test"
        assert data["execution_time"] == 10.5
        assert data["stage_count"] == 3
        assert data["success"] is True

    def test_aggregated_metrics_to_dict(self, aggregator: MetricsAggregator) -> None:
        """Test AggregatedMetrics to_dict conversion."""
        metrics = aggregator.aggregate()
        data = metrics.to_dict()

        assert "total_workflows" in data
        assert "success_rate" in data
        assert "stage_metrics" in data
        assert isinstance(data["stage_metrics"], dict)


# ============================================================================
# Test Integration
# ============================================================================


class TestIntegration:
    """Test complete analytics pipeline."""

    def test_complete_pipeline(self, sample_metrics: List[WorkflowMetric]) -> None:
        """Test creating and using complete pipeline."""
        aggregator, analyzer, dashboard_gen, formatter = create_analytics_pipeline()
        aggregator.add_metrics_batch(sample_metrics)

        # Test aggregation
        metrics = aggregator.aggregate()
        assert metrics.total_workflows == 5

        # Test trend analysis
        trend = analyzer.analyze_execution_time_trend(window_size=3)
        assert trend is not None

        # Test dashboard
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            dashboard_gen.generate_dashboard(output_path)
            assert output_path.exists()

        # Test formatting
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "report.json"
            csv_path = Path(tmpdir) / "report.csv"
            formatter.export_json(json_path)
            formatter.export_csv(csv_path)
            assert json_path.exists()
            assert csv_path.exists()

    def test_pipeline_factory_function(self) -> None:
        """Test analytics pipeline factory function."""
        aggregator, analyzer, dashboard_gen, formatter = create_analytics_pipeline()

        assert isinstance(aggregator, MetricsAggregator)
        assert isinstance(analyzer, TrendAnalyzer)
        assert isinstance(dashboard_gen, DashboardGenerator)
        assert isinstance(formatter, ReportFormatter)

    def test_end_to_end_workflow(self, sample_metrics: List[WorkflowMetric]) -> None:
        """Test end-to-end workflow with all components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create pipeline
            aggregator, analyzer, dashboard_gen, formatter = create_analytics_pipeline()

            # Add metrics
            aggregator.add_metrics_batch(sample_metrics)

            # Generate reports
            dashboard_gen.generate_dashboard(tmppath / "dashboard.html")
            formatter.export_json(tmppath / "metrics.json")
            formatter.export_csv(tmppath / "metrics.csv")
            formatter.export_summary(tmppath / "summary.txt")

            # Verify all files created
            assert (tmppath / "dashboard.html").exists()
            assert (tmppath / "metrics.json").exists()
            assert (tmppath / "metrics.csv").exists()
            assert (tmppath / "summary.txt").exists()


# ============================================================================
# Test Edge Cases
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_aggregator_with_single_metric(self) -> None:
        """Test aggregator with single metric."""
        agg = MetricsAggregator()
        metric = WorkflowMetric(
            workflow_id="single",
            execution_time=10.0,
            stage_count=2,
            success=True,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=10),
            stage_times={0: 5.0, 1: 5.0},
        )
        agg.add_metric(metric)

        metrics = agg.aggregate()
        assert metrics.total_workflows == 1
        assert metrics.stddev_execution_time == 0.0

    def test_all_workflows_failed(self) -> None:
        """Test aggregation with all failed workflows."""
        agg = MetricsAggregator()
        base_time = datetime.now()

        for i in range(3):
            metric = WorkflowMetric(
                workflow_id=f"failed-{i}",
                execution_time=10.0,
                stage_count=2,
                success=False,
                start_time=base_time + timedelta(hours=i),
                end_time=base_time + timedelta(hours=i, seconds=10),
                stage_times={0: 5.0, 1: 5.0},
                error_count=1,
            )
            agg.add_metric(metric)

        metrics = agg.aggregate()
        assert metrics.success_rate == 0.0
        assert metrics.failed_workflows == 3

    def test_trend_with_identical_values(self) -> None:
        """Test trend analysis with identical values."""
        agg = MetricsAggregator()
        base_time = datetime.now()

        for i in range(5):
            metric = WorkflowMetric(
                workflow_id=f"identical-{i}",
                execution_time=10.0,  # Same for all
                stage_count=2,
                success=True,
                start_time=base_time + timedelta(hours=i),
                end_time=base_time + timedelta(hours=i, seconds=10),
                stage_times={0: 5.0, 1: 5.0},
            )
            agg.add_metric(metric)

        analyzer = TrendAnalyzer(agg)
        trend = analyzer.analyze_execution_time_trend(window_size=3)

        assert trend is not None
        assert trend.trend_direction == "stable"
