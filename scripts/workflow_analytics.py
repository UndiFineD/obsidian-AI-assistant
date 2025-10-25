"""
Workflow Analytics Module for v0.1.46

Provides comprehensive metrics aggregation, trend analysis, dashboard generation,
and report formatting for workflow execution data.

Key Components:
- MetricsAggregator: Collect and aggregate workflow metrics
- TrendAnalyzer: Analyze trends and patterns across workflows
- DashboardGenerator: Create interactive HTML dashboards
- ReportFormatter: Format and export reports in multiple formats

Author: Obsidian AI Agent
License: MIT
"""

import csv
import json
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class WorkflowMetric:
    """Single workflow execution metric snapshot."""

    workflow_id: str
    execution_time: float  # seconds
    stage_count: int
    success: bool
    start_time: datetime
    end_time: datetime
    stage_times: Dict[int, float]  # stage_id -> execution_time
    error_count: int = 0
    warnings_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "execution_time": self.execution_time,
            "stage_count": self.stage_count,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "stage_times": self.stage_times,
            "error_count": self.error_count,
            "warnings_count": self.warnings_count,
            "metadata": self.metadata,
        }


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across multiple workflows."""

    total_workflows: int
    successful_workflows: int
    failed_workflows: int
    success_rate: float
    total_execution_time: float
    avg_execution_time: float
    median_execution_time: float
    min_execution_time: float
    max_execution_time: float
    stddev_execution_time: float
    avg_stage_count: float
    total_errors: int
    total_warnings: int
    time_period_start: datetime
    time_period_end: datetime
    stage_metrics: Dict[int, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_workflows": self.total_workflows,
            "successful_workflows": self.successful_workflows,
            "failed_workflows": self.failed_workflows,
            "success_rate": self.success_rate,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": self.avg_execution_time,
            "median_execution_time": self.median_execution_time,
            "min_execution_time": self.min_execution_time,
            "max_execution_time": self.max_execution_time,
            "stddev_execution_time": self.stddev_execution_time,
            "avg_stage_count": self.avg_stage_count,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "time_period_start": self.time_period_start.isoformat(),
            "time_period_end": self.time_period_end.isoformat(),
            "stage_metrics": self.stage_metrics,
        }


@dataclass
class TrendData:
    """Trend analysis results."""

    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_slope: float
    correlation_coefficient: float
    r_squared: float
    forecast_next_value: float
    confidence_level: float
    data_points: int


class MetricsAggregator:
    """Collects and aggregates workflow execution metrics."""

    def __init__(self) -> None:
        """Initialize metrics aggregator."""
        self.metrics: List[WorkflowMetric] = []
        self.metrics_by_id: Dict[str, WorkflowMetric] = {}

    def add_metric(self, metric: WorkflowMetric) -> None:
        """Add a workflow metric."""
        self.metrics.append(metric)
        self.metrics_by_id[metric.workflow_id] = metric

    def add_metrics_batch(self, metrics: List[WorkflowMetric]) -> None:
        """Add multiple metrics at once."""
        for metric in metrics:
            self.add_metric(metric)

    def get_metrics(self) -> List[WorkflowMetric]:
        """Get all metrics."""
        return self.metrics.copy()

    def get_metric_by_id(self, workflow_id: str) -> Optional[WorkflowMetric]:
        """Get metric by workflow ID."""
        return self.metrics_by_id.get(workflow_id)

    def aggregate(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> AggregatedMetrics:
        """Aggregate metrics for time period."""
        # Filter metrics by time period
        filtered_metrics = self._filter_by_time(start_time, end_time)

        if not filtered_metrics:
            # Return empty aggregation
            now = datetime.now()
            return AggregatedMetrics(
                total_workflows=0,
                successful_workflows=0,
                failed_workflows=0,
                success_rate=0.0,
                total_execution_time=0.0,
                avg_execution_time=0.0,
                median_execution_time=0.0,
                min_execution_time=0.0,
                max_execution_time=0.0,
                stddev_execution_time=0.0,
                avg_stage_count=0.0,
                total_errors=0,
                total_warnings=0,
                time_period_start=now,
                time_period_end=now,
            )

        # Calculate basic metrics
        total_workflows = len(filtered_metrics)
        successful_workflows = sum(1 for m in filtered_metrics if m.success)
        failed_workflows = total_workflows - successful_workflows
        success_rate = (
            successful_workflows / total_workflows if total_workflows > 0 else 0.0
        )

        # Calculate execution time metrics
        execution_times = [m.execution_time for m in filtered_metrics]
        total_execution_time = sum(execution_times)
        avg_execution_time = (
            total_execution_time / total_workflows if total_workflows > 0 else 0.0
        )
        median_execution_time = (
            statistics.median(execution_times) if execution_times else 0.0
        )
        min_execution_time = min(execution_times) if execution_times else 0.0
        max_execution_time = max(execution_times) if execution_times else 0.0
        stddev_execution_time = (
            statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
        )

        # Calculate stage metrics
        avg_stage_count = (
            statistics.mean([m.stage_count for m in filtered_metrics])
            if filtered_metrics
            else 0.0
        )

        # Aggregate stage-specific metrics
        stage_metrics = self._aggregate_stage_metrics(filtered_metrics)

        # Calculate error/warning metrics
        total_errors = sum(m.error_count for m in filtered_metrics)
        total_warnings = sum(m.warnings_count for m in filtered_metrics)

        # Time period
        period_start = min(m.start_time for m in filtered_metrics)
        period_end = max(m.end_time for m in filtered_metrics)

        return AggregatedMetrics(
            total_workflows=total_workflows,
            successful_workflows=successful_workflows,
            failed_workflows=failed_workflows,
            success_rate=success_rate,
            total_execution_time=total_execution_time,
            avg_execution_time=avg_execution_time,
            median_execution_time=median_execution_time,
            min_execution_time=min_execution_time,
            max_execution_time=max_execution_time,
            stddev_execution_time=stddev_execution_time,
            avg_stage_count=avg_stage_count,
            total_errors=total_errors,
            total_warnings=total_warnings,
            time_period_start=period_start,
            time_period_end=period_end,
            stage_metrics=stage_metrics,
        )

    def _filter_by_time(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[WorkflowMetric]:
        """Filter metrics by time period."""
        filtered = self.metrics

        if start_time:
            filtered = [m for m in filtered if m.start_time >= start_time]

        if end_time:
            filtered = [m for m in filtered if m.end_time <= end_time]

        return filtered

    def _aggregate_stage_metrics(
        self, metrics: List[WorkflowMetric]
    ) -> Dict[int, Dict[str, float]]:
        """Aggregate metrics by stage."""
        stage_times: Dict[int, List[float]] = defaultdict(list)

        for metric in metrics:
            for stage_id, stage_time in metric.stage_times.items():
                stage_times[stage_id].append(stage_time)

        stage_metrics: Dict[int, Dict[str, float]] = {}

        for stage_id, times in stage_times.items():
            stage_metrics[stage_id] = {
                "avg_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "min_time": min(times),
                "max_time": max(times),
                "stddev_time": statistics.stdev(times) if len(times) > 1 else 0.0,
                "count": len(times),
            }

        return stage_metrics


class TrendAnalyzer:
    """Analyzes trends and patterns in workflow metrics."""

    def __init__(self, aggregator: MetricsAggregator) -> None:
        """Initialize trend analyzer."""
        self.aggregator = aggregator

    def analyze_execution_time_trend(
        self, window_size: int = 10
    ) -> Optional[TrendData]:
        """Analyze trend in execution times."""
        metrics = self.aggregator.get_metrics()

        if len(metrics) < window_size:
            return None

        # Use recent metrics for trend
        recent_metrics = sorted(metrics, key=lambda m: m.start_time)[-window_size:]
        execution_times = [m.execution_time for m in recent_metrics]

        return self._calculate_trend(execution_times)

    def analyze_success_rate_trend(self, window_size: int = 10) -> Optional[TrendData]:
        """Analyze trend in success rates."""
        metrics = self.aggregator.get_metrics()

        if len(metrics) < window_size:
            return None

        recent_metrics = sorted(metrics, key=lambda m: m.start_time)[-window_size:]
        success_values = [1.0 if m.success else 0.0 for m in recent_metrics]

        return self._calculate_trend(success_values)

    def analyze_stage_count_trend(self, window_size: int = 10) -> Optional[TrendData]:
        """Analyze trend in stage counts."""
        metrics = self.aggregator.get_metrics()

        if len(metrics) < window_size:
            return None

        recent_metrics = sorted(metrics, key=lambda m: m.start_time)[-window_size:]
        stage_counts = [float(m.stage_count) for m in recent_metrics]

        return self._calculate_trend(stage_counts)

    def _calculate_trend(self, values: List[float]) -> TrendData:
        """Calculate trend using simple linear regression."""
        n = len(values)
        x_values = list(range(n))

        # Calculate means
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)

        # Calculate slope and intercept
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        slope = numerator / denominator if denominator != 0 else 0.0

        # Determine trend direction
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        # Calculate R-squared
        y_pred = [y_mean + slope * (x - x_mean) for x in x_values]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        # Forecast next value
        next_x = n
        forecast_next_value = y_mean + slope * (next_x - x_mean)

        # Calculate correlation coefficient
        correlation = (
            numerator / (denominator**0.5 * ss_tot**0.5)
            if denominator > 0 and ss_tot > 0
            else 0.0
        )

        # Confidence level based on R-squared
        confidence_level = max(0.0, min(1.0, abs(r_squared)))

        return TrendData(
            trend_direction=trend_direction,
            trend_slope=slope,
            correlation_coefficient=correlation,
            r_squared=r_squared,
            forecast_next_value=forecast_next_value,
            confidence_level=confidence_level,
            data_points=n,
        )


class DashboardGenerator:
    """Generates HTML dashboards and visualizations."""

    def __init__(self, aggregator: MetricsAggregator, analyzer: TrendAnalyzer) -> None:
        """Initialize dashboard generator."""
        self.aggregator = aggregator
        self.analyzer = analyzer

    def generate_dashboard(
        self, output_path: Path, title: str = "Workflow Analytics Dashboard"
    ) -> None:
        """Generate HTML dashboard."""
        metrics = self.aggregator.aggregate()
        execution_trend = self.analyzer.analyze_execution_time_trend()
        success_trend = self.analyzer.analyze_success_rate_trend()

        html_content = self._build_html(title, metrics, execution_trend, success_trend)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content)

    def _build_html(
        self,
        title: str,
        metrics: AggregatedMetrics,
        execution_trend: Optional[TrendData],
        success_trend: Optional[TrendData],
    ) -> str:
        """Build HTML dashboard content."""
        metrics_cards = self._generate_metrics_cards(metrics)
        trend_sections = self._generate_trend_sections(execution_trend, success_trend)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .metric-label {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .metric-value {{
            color: #333;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-subtitle {{
            color: #999;
            font-size: 13px;
        }}
        .trend-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .trend-section h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        .trend-status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 10px;
        }}
        .trend-increasing {{
            background: #d4edda;
            color: #155724;
        }}
        .trend-decreasing {{
            background: #f8d7da;
            color: #721c24;
        }}
        .trend-stable {{
            background: #cce5ff;
            color: #004085;
        }}
        .timestamp {{
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        <div class="metrics-grid">
            {metrics_cards}
        </div>
        {trend_sections}
        <div class="timestamp">
            Last updated: {datetime.now().isoformat()}
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_metrics_cards(self, metrics: AggregatedMetrics) -> str:
        """Generate metric cards HTML."""
        cards = f"""
        <div class="metric-card">
            <div class="metric-label">Total Workflows</div>
            <div class="metric-value">{metrics.total_workflows}</div>
            <div class="metric-subtitle">Success Rate: {metrics.success_rate * 100:.1f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Execution Time</div>
            <div class="metric-value">{metrics.avg_execution_time:.1f}s</div>
            <div class="metric-subtitle">Median: {metrics.median_execution_time:.1f}s</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Errors</div>
            <div class="metric-value">{metrics.total_errors}</div>
            <div class="metric-subtitle">Warnings: {metrics.total_warnings}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Stages</div>
            <div class="metric-value">{metrics.avg_stage_count:.1f}</div>
            <div class="metric-subtitle">Per Workflow</div>
        </div>
        """
        return cards

    def _generate_trend_sections(
        self,
        execution_trend: Optional[TrendData],
        success_trend: Optional[TrendData],
    ) -> str:
        """Generate trend analysis sections."""
        sections = ""

        if execution_trend:
            sections += f"""
        <div class="trend-section">
            <h3>Execution Time Trend</h3>
            <span class="trend-status trend-{execution_trend.trend_direction}">
                {execution_trend.trend_direction.title()}
            </span>
            <p>Slope: {execution_trend.trend_slope:.4f} | R²: {execution_trend.r_squared:.3f}</p>
            <p>Forecast: {execution_trend.forecast_next_value:.1f}s (Confidence: {execution_trend.confidence_level * 100:.0f}%)</p>
        </div>
        """

        if success_trend:
            sections += f"""
        <div class="trend-section">
            <h3>Success Rate Trend</h3>
            <span class="trend-status trend-{success_trend.trend_direction}">
                {success_trend.trend_direction.title()}
            </span>
            <p>Slope: {success_trend.trend_slope:.4f} | R²: {success_trend.r_squared:.3f}</p>
            <p>Forecast: {success_trend.forecast_next_value * 100:.1f}% (Confidence: {success_trend.confidence_level * 100:.0f}%)</p>
        </div>
        """

        return sections


class ReportFormatter:
    """Formats and exports analytics reports in multiple formats."""

    def __init__(self, aggregator: MetricsAggregator) -> None:
        """Initialize report formatter."""
        self.aggregator = aggregator

    def export_json(self, output_path: Path, include_metrics: bool = True) -> None:
        """Export analytics as JSON."""
        metrics = self.aggregator.aggregate()
        data: Dict[str, Any] = {"aggregated_metrics": metrics.to_dict()}

        if include_metrics:
            data["individual_metrics"] = [
                m.to_dict() for m in self.aggregator.get_metrics()
            ]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2))

    def export_csv(self, output_path: Path) -> None:
        """Export individual metrics as CSV."""
        metrics = self.aggregator.get_metrics()

        if not metrics:
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="") as csvfile:
            fieldnames = [
                "workflow_id",
                "execution_time",
                "stage_count",
                "success",
                "start_time",
                "end_time",
                "error_count",
                "warnings_count",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for metric in metrics:
                row = {
                    "workflow_id": metric.workflow_id,
                    "execution_time": metric.execution_time,
                    "stage_count": metric.stage_count,
                    "success": metric.success,
                    "start_time": metric.start_time.isoformat(),
                    "end_time": metric.end_time.isoformat(),
                    "error_count": metric.error_count,
                    "warnings_count": metric.warnings_count,
                }
                writer.writerow(row)

    def export_summary(self, output_path: Path) -> None:
        """Export summary report as plain text."""
        metrics = self.aggregator.aggregate()

        summary = f"""
WORKFLOW ANALYTICS SUMMARY REPORT
{"=" * 50}

Report Generated: {datetime.now().isoformat()}

OVERVIEW
{"-" * 50}
Total Workflows:      {metrics.total_workflows}
Successful:           {metrics.successful_workflows}
Failed:               {metrics.failed_workflows}
Success Rate:         {metrics.success_rate * 100:.1f}%

EXECUTION TIME
{"-" * 50}
Total Time:           {metrics.total_execution_time:.1f}s
Average:              {metrics.avg_execution_time:.1f}s
Median:               {metrics.median_execution_time:.1f}s
Min:                  {metrics.min_execution_time:.1f}s
Max:                  {metrics.max_execution_time:.1f}s
Std Dev:              {metrics.stddev_execution_time:.1f}s

QUALITY METRICS
{"-" * 50}
Total Errors:         {metrics.total_errors}
Total Warnings:       {metrics.total_warnings}
Avg Stages/Workflow:  {metrics.avg_stage_count:.1f}

TIME PERIOD
{"-" * 50}
Start: {metrics.time_period_start.isoformat()}
End:   {metrics.time_period_end.isoformat()}

"""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary)


# Public API functions
def create_analytics_pipeline() -> (
    Tuple[MetricsAggregator, TrendAnalyzer, DashboardGenerator, ReportFormatter]
):
    """Create a complete analytics pipeline."""
    aggregator = MetricsAggregator()
    analyzer = TrendAnalyzer(aggregator)
    dashboard_gen = DashboardGenerator(aggregator, analyzer)
    formatter = ReportFormatter(aggregator)

    return aggregator, analyzer, dashboard_gen, formatter
