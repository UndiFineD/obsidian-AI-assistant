#!/usr/bin/env python3
"""
Stage Timing & Performance Estimation Module

Tracks stage execution times, estimates remaining time, and provides
performance insights for workflow optimization.

Features:
- Track individual stage execution times
- Estimate total workflow duration
- Identify bottleneck stages
- Provide performance recommendations
- Store historical timing data

Author: Obsidian AI Agent Team
License: MIT
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class StageTimingData:
    """Timing data for a single stage execution"""
    stage_id: int
    stage_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    status: str = "running"  # running, completed, failed, skipped

    def complete(self, status: str = "completed"):
        """Mark stage as complete and calculate duration"""
        self.end_time = datetime.now()
        self.status = status
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
        }


@dataclass
class WorkflowTimingProfile:
    """Timing profile for a complete workflow execution"""
    workflow_id: str
    lane: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    stages: List[StageTimingData] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def add_stage(self, stage_id: int, stage_name: str) -> StageTimingData:
        """Start tracking a new stage"""
        stage = StageTimingData(stage_id, stage_name, datetime.now())
        self.stages.append(stage)
        return stage

    def complete(self):
        """Mark workflow as complete"""
        self.end_time = datetime.now()
        self.total_duration_seconds = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "lane": self.lane,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": self.total_duration_seconds,
            "stages": [s.to_dict() for s in self.stages],
            "metadata": self.metadata,
        }


class PerformanceEstimator:
    """Estimates workflow performance based on historical data"""

    def __init__(self, history_file: Path):
        """
        Initialize performance estimator.

        Args:
            history_file: Path to JSON file storing historical timing data
        """
        self.history_file = Path(history_file)
        self.history: List[WorkflowTimingProfile] = []
        self.load_history()

    def load_history(self):
        """Load historical timing data"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    data = json.load(f)
                    # Parse historical profiles (simplified for now)
                    self.history = data.get("profiles", [])
            except Exception:
                self.history = []

    def save_history(self):
        """Save historical timing data"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump({"profiles": self.history}, f, indent=2)

    def get_average_stage_time(self, stage_id: int, lane: str) -> Optional[float]:
        """
        Get average execution time for a stage across all historical runs.

        Args:
            stage_id: Stage ID
            lane: Workflow lane

        Returns:
            Average duration in seconds, or None if no history
        """
        times = []
        for profile in self.history:
            if profile.get("lane") == lane:
                for stage in profile.get("stages", []):
                    if stage.get("stage_id") == stage_id and stage.get("status") == "completed":
                        times.append(stage.get("duration_seconds", 0))

        return sum(times) / len(times) if times else None

    def estimate_remaining_time(
        self, current_profile: Dict, completed_stage_id: int, lane: str
    ) -> Dict:
        """
        Estimate remaining time based on historical data.

        Args:
            current_profile: Current workflow profile
            completed_stage_id: Last completed stage ID
            lane: Workflow lane

        Returns:
            Dict with estimate, confidence, and breakdown
        """
        remaining_stages = current_profile.get("stages", [])
        remaining_stages = [s for s in remaining_stages if s.get("stage_id", -1) > completed_stage_id]

        estimated_seconds = 0
        stage_estimates = {}

        for stage in remaining_stages:
            stage_id = stage.get("stage_id")
            avg_time = self.get_average_stage_time(stage_id, lane)

            if avg_time:
                estimated_seconds += avg_time
                stage_estimates[stage_id] = avg_time
            else:
                # If no historical data, use conservative estimate
                estimated_seconds += 120  # 2 minutes default

        return {
            "estimated_seconds": estimated_seconds,
            "confidence": len([s for s in stage_estimates if s]) / len(stage_estimates) if stage_estimates else 0,
            "stage_estimates": stage_estimates,
        }

    def identify_bottlenecks(self, lane: str) -> List[Dict]:
        """
        Identify stages that are bottlenecks.

        Args:
            lane: Workflow lane

        Returns:
            List of bottleneck stages sorted by impact
        """
        stage_times = {}

        for profile in self.history:
            if profile.get("lane") == lane:
                for stage in profile.get("stages", []):
                    if stage.get("status") == "completed":
                        stage_id = stage.get("stage_id")
                        if stage_id not in stage_times:
                            stage_times[stage_id] = []
                        stage_times[stage_id].append(stage.get("duration_seconds", 0))

        # Calculate averages and identify top bottlenecks
        bottlenecks = []
        for stage_id, times in stage_times.items():
            avg_time = sum(times) / len(times)
            bottlenecks.append({
                "stage_id": stage_id,
                "average_duration": avg_time,
                "executions": len(times),
            })

        return sorted(bottlenecks, key=lambda x: x["average_duration"], reverse=True)

    def get_performance_summary(self, lane: str) -> Dict:
        """
        Get overall performance summary for a lane.

        Args:
            lane: Workflow lane

        Returns:
            Performance summary with metrics and recommendations
        """
        lane_profiles = [p for p in self.history if p.get("lane") == lane]

        if not lane_profiles:
            return {"status": "insufficient_data"}

        total_times = [p.get("total_duration_seconds", 0) for p in lane_profiles]
        avg_total = sum(total_times) / len(total_times)
        min_total = min(total_times)
        max_total = max(total_times)

        bottlenecks = self.identify_bottlenecks(lane)

        recommendations = []
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            if top_bottleneck["average_duration"] > avg_total * 0.3:
                recommendations.append(
                    f"Stage {top_bottleneck['stage_id']} is a significant bottleneck "
                    f"({top_bottleneck['average_duration']:.1f}s avg). "
                    f"Consider optimization opportunities."
                )

        return {
            "lane": lane,
            "executions": len(lane_profiles),
            "average_duration": avg_total,
            "min_duration": min_total,
            "max_duration": max_total,
            "bottlenecks": bottlenecks[:3],  # Top 3 bottlenecks
            "recommendations": recommendations,
        }


class TimingTracker:
    """Tracks timing for a workflow execution"""

    def __init__(self, workflow_id: str, lane: str):
        """Initialize timing tracker"""
        self.profile = WorkflowTimingProfile(workflow_id=workflow_id, lane=lane)
        self.current_stage: Optional[StageTimingData] = None

    def start_stage(self, stage_id: int, stage_name: str):
        """Start tracking a stage"""
        self.current_stage = self.profile.add_stage(stage_id, stage_name)

    def complete_stage(self, status: str = "completed"):
        """Mark current stage as complete"""
        if self.current_stage:
            self.current_stage.complete(status)
            self.current_stage = None

    def complete_workflow(self):
        """Mark workflow as complete"""
        self.profile.complete()

    def get_summary(self) -> Dict:
        """Get workflow timing summary"""
        summary = {
            "workflow_id": self.profile.workflow_id,
            "lane": self.profile.lane,
            "total_duration": self.profile.total_duration_seconds,
            "stages": []
        }

        for stage in self.profile.stages:
            summary["stages"].append({
                "id": stage.stage_id,
                "name": stage.stage_name,
                "duration": stage.duration_seconds,
                "status": stage.status,
            })

        return summary

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.profile.to_dict()
