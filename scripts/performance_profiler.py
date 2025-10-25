"""
Performance Profiler Module for v0.1.46
Provides profiling and bottleneck detection for workflow stages.

Components:
    - StageProfiler: Low-overhead profiling with decorators
    - BottleneckDetector: Identifies bottlenecks in workflow stages
    - ProfileAnalyzer: Analyzes patterns in profiling data
    - RecommendationEngine: Generates optimization recommendations

Author: GitHub Copilot
Version: 0.1.46
"""

from dataclasses import dataclass, field, asdict
from functools import wraps
from typing import Callable, Any, Dict, List, Tuple, Optional
import time
from datetime import datetime
import statistics


@dataclass
class ProfilePoint:
    """Single profiling measurement point."""
    stage_name: str
    execution_time: float
    memory_used: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class BottleneckInfo:
    """Information about a detected bottleneck."""
    stage_name: str
    avg_time: float
    max_time: float
    min_time: float
    variance: float
    execution_count: int
    severity: str  # "critical", "high", "medium", "low"
    percentile_95: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class Recommendation:
    """Optimization recommendation for a stage."""
    stage_name: str
    issue: str
    suggested_action: str
    expected_improvement: str
    priority: str  # "critical", "high", "medium", "low"
    confidence: float  # 0.0 - 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class StageProfiler:
    """
    Low-overhead profiling with decorators.
    
    Tracks execution time for workflow stages with minimal performance impact.
    Uses context managers or decorators for ease of use.
    """

    def __init__(self, threshold_ms: float = 0.1):
        """
        Initialize profiler.
        
        Args:
            threshold_ms: Minimum execution time to track (milliseconds)
        """
        self.threshold_ms = threshold_ms
        self.profiles: Dict[str, List[ProfilePoint]] = {}
        self.active_timers: Dict[str, float] = {}

    def profile_stage(self, stage_name: str) -> Callable:
        """
        Decorator for profiling stage functions.
        
        Args:
            stage_name: Name of the stage being profiled
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed_time = (time.perf_counter() - start_time) * 1000
                    if elapsed_time >= self.threshold_ms:
                        self._record_profile(stage_name, elapsed_time, {})
            return wrapper
        return decorator

    def start_stage(self, stage_name: str) -> None:
        """Start timing a stage."""
        self.active_timers[stage_name] = time.perf_counter()

    def end_stage(self, stage_name: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        End timing a stage and record profile.
        
        Args:
            stage_name: Name of the stage
            metadata: Optional metadata to record
            
        Returns:
            Elapsed time in milliseconds
        """
        if stage_name not in self.active_timers:
            return 0.0

        elapsed_time = (time.perf_counter() - self.active_timers[stage_name]) * 1000
        del self.active_timers[stage_name]

        if elapsed_time >= self.threshold_ms:
            self._record_profile(stage_name, elapsed_time, metadata or {})

        return elapsed_time

    def _record_profile(self, stage_name: str, execution_time: float, metadata: Dict[str, Any]) -> None:
        """Record a profile point."""
        if stage_name not in self.profiles:
            self.profiles[stage_name] = []

        profile_point = ProfilePoint(
            stage_name=stage_name,
            execution_time=execution_time,
            metadata=metadata
        )
        self.profiles[stage_name].append(profile_point)

    def get_stage_stats(self, stage_name: str) -> Dict[str, float]:
        """
        Get statistics for a stage.
        
        Args:
            stage_name: Name of the stage
            
        Returns:
            Dictionary with stats (avg, min, max, count, etc.)
        """
        if stage_name not in self.profiles or not self.profiles[stage_name]:
            return {}

        times = [p.execution_time for p in self.profiles[stage_name]]
        return {
            "count": len(times),
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "total": sum(times),
        }

    def reset(self) -> None:
        """Reset all profiling data."""
        self.profiles.clear()
        self.active_timers.clear()


class BottleneckDetector:
    """
    Identifies bottlenecks in workflow stages.
    
    Uses statistical analysis to detect stages that are significantly
    slower than baseline or show high variance in execution time.
    """

    def __init__(self, threshold_percentile: float = 95.0, variance_threshold: float = 0.5):
        """
        Initialize detector.
        
        Args:
            threshold_percentile: Percentile to use for bottleneck detection (0-100)
            variance_threshold: Coefficient of variation threshold for high variance (0-1)
        """
        self.threshold_percentile = threshold_percentile
        self.variance_threshold = variance_threshold

    def detect_bottlenecks(self, profiles: Dict[str, List[ProfilePoint]]) -> List[BottleneckInfo]:
        """
        Detect bottlenecks from profile data.
        
        Args:
            profiles: Dictionary of stage profiles
            
        Returns:
            List of detected bottlenecks
        """
        bottlenecks: List[BottleneckInfo] = []

        if not profiles:
            return bottlenecks

        # Calculate global statistics
        all_times = []
        for stage_profiles in profiles.values():
            all_times.extend([p.execution_time for p in stage_profiles])

        if not all_times:
            return bottlenecks

        global_avg = statistics.mean(all_times)
        global_percentile_95 = self._percentile(all_times, 95)

        # Analyze each stage
        for stage_name, stage_profiles in profiles.items():
            if not stage_profiles:
                continue

            times = [p.execution_time for p in stage_profiles]
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)
            variance = statistics.variance(times) if len(times) > 1 else 0.0
            stdev = statistics.stdev(times) if len(times) > 1 else 0.0
            percentile_95 = self._percentile(times, 95)

            # Determine severity
            severity = "low"
            cv = stdev / avg_time if avg_time > 0 else 0  # Coefficient of variation

            # Check for high execution time
            if avg_time > global_percentile_95:
                severity = "critical"
            elif avg_time > global_avg * 1.5:
                severity = "high"
            elif cv > self.variance_threshold:
                severity = "high"
            elif avg_time > global_avg * 1.2:
                severity = "medium"

            if severity != "low":
                bottleneck = BottleneckInfo(
                    stage_name=stage_name,
                    avg_time=avg_time,
                    max_time=max_time,
                    min_time=min_time,
                    variance=variance,
                    execution_count=len(times),
                    severity=severity,
                    percentile_95=percentile_95,
                )
                bottlenecks.append(bottleneck)

        return sorted(bottlenecks, key=lambda b: b.avg_time, reverse=True)

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (len(sorted_data) - 1) * percentile / 100
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)
        if lower_index == upper_index:
            return sorted_data[lower_index]
        lower_value = sorted_data[lower_index]
        upper_value = sorted_data[upper_index]
        return lower_value + (upper_value - lower_value) * (index - lower_index)


class ProfileAnalyzer:
    """
    Analyzes patterns in profiling data.
    
    Identifies trends, performance degradation, and optimization opportunities.
    """

    def __init__(self):
        """Initialize analyzer."""
        self.analysis_cache: Dict[str, Any] = {}

    def analyze_performance_trends(self, profiles: Dict[str, List[ProfilePoint]]) -> Dict[str, Any]:
        """
        Analyze performance trends.
        
        Args:
            profiles: Dictionary of stage profiles
            
        Returns:
            Dictionary with trend analysis
        """
        trends = {}

        for stage_name, stage_profiles in profiles.items():
            if len(stage_profiles) < 2:
                continue

            times = [p.execution_time for p in stage_profiles]

            # Simple trend detection: compare first half vs second half
            mid_point = len(times) // 2
            first_half_avg = statistics.mean(times[:mid_point])
            second_half_avg = statistics.mean(times[mid_point:])

            trend = "stable"
            if second_half_avg > first_half_avg * 1.1:
                trend = "degrading"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "improving"

            trends[stage_name] = {
                "trend": trend,
                "first_half_avg": first_half_avg,
                "second_half_avg": second_half_avg,
                "change_percent": ((second_half_avg - first_half_avg) / first_half_avg * 100)
                    if first_half_avg > 0 else 0,
            }

        return trends

    def calculate_overhead(self, profiles: Dict[str, List[ProfilePoint]]) -> float:
        """
        Calculate profiling overhead percentage.
        
        Args:
            profiles: Dictionary of stage profiles
            
        Returns:
            Overhead as percentage (0-100)
        """
        if not profiles:
            return 0.0

        # Estimate overhead: ~1-2% per stage tracked
        stage_count = len(profiles)
        estimated_overhead = min(stage_count * 1.5, 5.0)  # Cap at 5%

        return estimated_overhead

    def identify_optimization_opportunities(
        self, profiles: Dict[str, List[ProfilePoint]], bottlenecks: List[BottleneckInfo]
    ) -> Dict[str, Any]:
        """
        Identify optimization opportunities.
        
        Args:
            profiles: Dictionary of stage profiles
            bottlenecks: List of detected bottlenecks
            
        Returns:
            Dictionary with opportunities
        """
        opportunities: Dict[str, Any] = {
            "high_variance_stages": [],
            "slow_stages": [],
            "candidate_for_parallelization": [],
        }

        for bottleneck in bottlenecks:
            if bottleneck.severity in ["critical", "high"]:
                opportunities["slow_stages"].append(bottleneck.stage_name)

                # Check if high variance
                if bottleneck.stage_name in profiles:
                    times = [p.execution_time for p in profiles[bottleneck.stage_name]]
                    if len(times) > 1:
                        cv = statistics.stdev(times) / statistics.mean(times)
                        if cv > 0.3:
                            opportunities["high_variance_stages"].append(bottleneck.stage_name)

        return opportunities


class RecommendationEngine:
    """
    Generates optimization recommendations based on profiling data.
    
    Provides actionable suggestions for improving workflow performance.
    """

    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize engine.
        
        Args:
            confidence_threshold: Minimum confidence for recommendations (0-1)
        """
        self.confidence_threshold = confidence_threshold

    def generate_recommendations(
        self,
        bottlenecks: List[BottleneckInfo],
        trends: Dict[str, Any],
        opportunities: Dict[str, Any],
    ) -> List[Recommendation]:
        """
        Generate recommendations.
        
        Args:
            bottlenecks: List of detected bottlenecks
            trends: Trend analysis data
            opportunities: Identified opportunities
            
        Returns:
            List of recommendations
        """
        recommendations: List[Recommendation] = []

        # Recommend caching for high-variance stages
        for stage_name in opportunities.get("high_variance_stages", []):
            rec = Recommendation(
                stage_name=stage_name,
                issue="High variance in execution time",
                suggested_action="Implement caching or add input validation",
                expected_improvement="Reduce variance by 30-50%, improve predictability",
                priority="high",
                confidence=0.75,
            )
            recommendations.append(rec)

        # Recommend optimization for slow stages
        for stage_name in opportunities.get("slow_stages", []):
            if stage_name in trends:
                trend_info = trends[stage_name]
                if trend_info["trend"] == "degrading":
                    rec = Recommendation(
                        stage_name=stage_name,
                        issue="Performance degrading over time",
                        suggested_action="Check for memory leaks or resource accumulation",
                        expected_improvement="Stabilize performance, reduce degradation",
                        priority="critical",
                        confidence=0.8,
                    )
                    recommendations.append(rec)

        # Recommend parallelization opportunities
        for stage_name in opportunities.get("candidate_for_parallelization", []):
            rec = Recommendation(
                stage_name=stage_name,
                issue="Long execution time identified",
                suggested_action="Analyze for parallelization opportunities",
                expected_improvement="Reduce execution time by 20-40%",
                priority="medium",
                confidence=0.65,
            )
            recommendations.append(rec)

        return [r for r in recommendations if r.confidence >= self.confidence_threshold]


def create_profiler_pipeline() -> Tuple[StageProfiler, BottleneckDetector, ProfileAnalyzer, RecommendationEngine]:
    """
    Factory function to create complete profiler pipeline.
    
    Returns:
        Tuple of (profiler, detector, analyzer, engine)
    """
    return (
        StageProfiler(threshold_ms=0.1),
        BottleneckDetector(threshold_percentile=95.0, variance_threshold=0.5),
        ProfileAnalyzer(),
        RecommendationEngine(confidence_threshold=0.6),
    )
