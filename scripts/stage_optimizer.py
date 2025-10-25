"""
Stage Optimizer Module for v0.1.46

Provides ML-powered stage optimization to predict optimal stage sequences for
workflow execution based on change characteristics and historical data.

Features:
    - Machine learning model training on workflow history
    - Stage prediction with confidence scoring
    - Execution time estimation
    - Graceful degradation if scikit-learn unavailable
    - Recommendation engine for optimization

Key Classes:
    - WorkflowHistoryCollector: Collects workflow execution data
    - StagePredictor: Predicts optimal stages using ML model
    - Recommendation: Data class for optimization recommendations
    - OptimizationStats: Statistics tracking for predictions

Key Functions:
    - collect_workflow_history(): Gather historical data
    - predict_stages(): Predict optimal stage sequence
    - estimate_execution_time(): Estimate time for given stages
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Try to import scikit-learn, but don't fail if unavailable
try:
    from sklearn.ensemble import RandomForestClassifier  # noqa: F401

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class WorkflowExecution:
    """Record of a single workflow execution."""

    change_id: str
    timestamp: str
    change_type: str  # "docs", "feature", "bugfix", "refactor", "chore"
    file_count: int
    file_types: List[str] = field(default_factory=list)
    stages_executed: List[int] = field(default_factory=list)
    duration_seconds: float = 0.0
    success: bool = True
    quality_gates_passed: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowExecution":
        """Create from dictionary."""
        return cls(
            change_id=data.get("change_id", ""),
            timestamp=data.get("timestamp", ""),
            change_type=data.get("change_type", "chore"),
            file_count=int(data.get("file_count", 0)),
            file_types=data.get("file_types", []),
            stages_executed=data.get("stages_executed", []),
            duration_seconds=float(data.get("duration_seconds", 0.0)),
            success=data.get("success", True),
            quality_gates_passed=int(data.get("quality_gates_passed", 0)),
            errors=data.get("errors", []),
        )


@dataclass
class Recommendation:
    """Optimization recommendation."""

    title: str
    description: str
    stages: List[int]
    expected_duration: float
    confidence: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class OptimizationStats:
    """Statistics for stage predictions."""

    total_predictions: int = 0
    successful_predictions: int = 0
    average_confidence: float = 0.0
    average_error_rate: float = 0.0
    model_training_time: float = 0.0
    last_training: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OptimizationStats":
        """Create from dictionary."""
        return cls(
            total_predictions=int(data.get("total_predictions", 0)),
            successful_predictions=int(data.get("successful_predictions", 0)),
            average_confidence=float(data.get("average_confidence", 0.0)),
            average_error_rate=float(data.get("average_error_rate", 0.0)),
            model_training_time=float(data.get("model_training_time", 0.0)),
            last_training=data.get("last_training"),
        )


# ============================================================================
# History Collection
# ============================================================================


class WorkflowHistoryCollector:
    """Collects and manages workflow execution history."""

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize collector with optional history file."""
        self.history_file = history_file or Path("./workflow_history.json")
        self.history: List[WorkflowExecution] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load history from file if exists."""
        if not self.history_file.exists():
            logger.debug("No existing history file found")
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data.get("history", []):
                self.history.append(WorkflowExecution.from_dict(item))

            logger.debug(f"Loaded {len(self.history)} historical executions")

        except Exception as e:
            logger.warning(f"Failed to load history: {e}")

    def add_execution(self, execution: WorkflowExecution) -> None:
        """Add workflow execution to history."""
        self.history.append(execution)
        logger.debug(f"Added execution: {execution.change_id}")

    def get_history(self, limit: Optional[int] = None) -> List[WorkflowExecution]:
        """Get workflow history, optionally limited to most recent N."""
        if limit is None:
            return self.history.copy()

        return self.history[-limit:] if len(self.history) > limit else self.history

    def save_to_file(self) -> Tuple[bool, Optional[str]]:
        """Save history to file."""
        try:
            data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "count": len(self.history),
                "history": [e.to_dict() for e in self.history],
            }

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(self.history)} executions to {self.history_file}")
            return True, None

        except Exception as e:
            return False, f"Error saving history: {str(e)}"

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from history."""
        if not self.history:
            return {
                "total": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "change_type_distribution": {},
            }

        successful = sum(1 for e in self.history if e.success)
        total_duration = sum(e.duration_seconds for e in self.history)
        change_types: Dict[str, int] = {}

        for execution in self.history:
            change_types[execution.change_type] = (
                change_types.get(execution.change_type, 0) + 1
            )

        return {
            "total": len(self.history),
            "success_rate": successful / len(self.history) if self.history else 0.0,
            "average_duration": (
                total_duration / len(self.history) if self.history else 0.0
            ),
            "change_type_distribution": change_types,
        }


# ============================================================================
# Stage Prediction
# ============================================================================


class StagePredictor:
    """Predicts optimal workflow stages using ML model."""

    # Default stage mappings (used when model not trained)
    DEFAULT_STAGE_MAPPING = {
        "docs": [0, 1, 2, 3],
        "bugfix": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "feature": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "refactor": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "chore": [0, 1, 2, 3],
    }

    # Average stage durations (in seconds)
    STAGE_DURATIONS = {
        0: 5,  # Setup
        1: 10,  # Parse & Validate
        2: 15,  # Quality Gates
        3: 20,  # Pre-commit Hooks
        4: 25,  # Commit Validation
        5: 60,  # Unit Tests
        6: 120,  # Integration Tests
        7: 30,  # Type Checking
        8: 45,  # Code Quality Analysis
        9: 150,  # Performance Tests
        10: 300,  # Stress Testing
        11: 60,  # Security Scanning
        12: 120,  # Compliance Validation
    }

    def __init__(self):
        """Initialize predictor."""
        self.model = None
        self.label_encoders: Dict[str, Any] = {}
        self.stats = OptimizationStats()
        self.is_trained = False

    def train(
        self, history: List[WorkflowExecution], force: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Train ML model on workflow history.

        Args:
            history: List of past workflow executions
            force: Force retraining even if already trained

        Returns:
            (success, error_message)
        """
        if not SKLEARN_AVAILABLE:
            logger.info("scikit-learn not available, using default mappings")
            self.is_trained = False
            return True, None

        if self.is_trained and not force:
            logger.debug("Model already trained, skipping")
            return True, None

        if not history or len(history) < 5:
            logger.warning(
                f"Insufficient history for training: {len(history)} executions"
            )
            self.is_trained = False
            return True, None

        try:
            import time

            start_time = time.time()

            # Prepare features and targets
            X, y = self._prepare_training_data(history)

            if X is None or len(X) == 0:
                logger.warning("Could not prepare training data")
                return True, None

            # Train model
            self.model = RandomForestClassifier(
                n_estimators=50, max_depth=10, random_state=42, n_jobs=-1
            )

            # Convert stages list to string for classification
            assert y is not None  # Guaranteed by check above
            y_encoded = [",".join(map(str, stages)) for stages in y]

            self.model.fit(X, y_encoded)

            training_time = time.time() - start_time
            self.stats.model_training_time = training_time
            self.stats.last_training = datetime.now().isoformat()
            self.is_trained = True

            logger.debug(f"Model trained in {training_time:.2f}s on {len(X)} samples")
            return True, None

        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            self.is_trained = False
            return False, f"Training failed: {str(e)}"

    def _prepare_training_data(
        self, history: List[WorkflowExecution]
    ) -> Tuple[Optional[List[List[int]]], Optional[List[List[int]]]]:
        """Prepare features and targets from history."""
        X: List[List[int]] = []
        y: List[List[int]] = []

        for execution in history:
            if not execution.success:
                continue  # Skip failed executions

            # Features: change_type, file_count, number_of_file_types
            features = [
                self._encode_change_type(execution.change_type),
                execution.file_count,
                len(execution.file_types),
            ]

            # Target: stages executed
            if execution.stages_executed:
                X.append(features)
                y.append(execution.stages_executed)

        return (X, y) if X else (None, None)

    def _encode_change_type(self, change_type: str) -> int:
        """Encode change type as integer."""
        mapping = {"docs": 0, "bugfix": 1, "feature": 2, "refactor": 3, "chore": 4}
        return mapping.get(change_type, 4)

    def _decode_change_type(self, code: int) -> str:
        """Decode change type from integer."""
        mapping = {0: "docs", 1: "bugfix", 2: "feature", 3: "refactor", 4: "chore"}
        return mapping.get(code, "chore")

    def predict(
        self,
        change_type: str,
        file_count: int = 1,
        file_types: Optional[List[str]] = None,
    ) -> Tuple[List[int], float]:
        """Predict optimal stages for given change.

        Args:
            change_type: Type of change ("docs", "feature", "bugfix", "refactor", "chore")
            file_count: Number of files changed
            file_types: List of file types (extensions)

        Returns:
            (predicted_stages, confidence_score)
        """
        self.stats.total_predictions += 1

        if file_types is None:
            file_types = []

        # Prepare features
        features = [
            self._encode_change_type(change_type),
            file_count,
            len(file_types),
        ]

        # Use model if trained and available
        if self.is_trained and self.model is not None:
            try:
                prediction = self.model.predict([features])[0]
                confidence = max(self.model.predict_proba([features])[0])

                stages = [int(s) for s in prediction.split(",")]
                self.stats.successful_predictions += 1
                self.stats.average_confidence = (
                    self.stats.average_confidence
                    * (self.stats.successful_predictions - 1)
                    + confidence
                ) / self.stats.successful_predictions

                logger.debug(
                    f"Predicted stages for {change_type}: {stages} (confidence: {confidence:.2f})"
                )
                return stages, confidence

            except Exception as e:
                logger.warning(f"Prediction failed, falling back to defaults: {e}")

        # Fallback to default mapping
        default_stages = self.DEFAULT_STAGE_MAPPING.get(
            change_type, self.DEFAULT_STAGE_MAPPING["chore"]
        )
        logger.debug(f"Using default stages for {change_type}: {default_stages}")

        return default_stages, 0.5  # Low confidence for defaults

    def estimate_execution_time(self, stages: List[int]) -> float:
        """Estimate execution time for given stages.

        Args:
            stages: List of stage numbers

        Returns:
            Estimated duration in seconds
        """
        total_time = sum(self.STAGE_DURATIONS.get(stage, 30) for stage in stages)
        return float(total_time)

    def get_recommendations(self) -> List[Recommendation]:
        """Generate optimization recommendations.

        Returns:
            List of Recommendation objects
        """
        recommendations = []

        if not SKLEARN_AVAILABLE:
            recommendations.append(
                Recommendation(
                    title="Install scikit-learn",
                    description="ML-powered stage prediction requires scikit-learn",
                    stages=list(range(13)),
                    expected_duration=self.estimate_execution_time(list(range(13))),
                    confidence=0.5,
                    rationale="scikit-learn not available for model training",
                )
            )

        if not self.is_trained:
            recommendations.append(
                Recommendation(
                    title="Train ML model",
                    description="Accumulate more workflow history to train the ML model",
                    stages=list(range(13)),
                    expected_duration=self.estimate_execution_time(list(range(13))),
                    confidence=0.5,
                    rationale="ML model needs historical data for accurate predictions",
                )
            )

        # Add optimization recommendations
        if self.stats.average_confidence < 0.70:
            recommendations.append(
                Recommendation(
                    title="Improve prediction confidence",
                    description="Model confidence below 70%, continue collecting execution data",
                    stages=list(range(13)),
                    expected_duration=self.estimate_execution_time(list(range(13))),
                    confidence=0.5,
                    rationale=f"Current confidence: {self.stats.average_confidence:.2f}",
                )
            )

        return recommendations

    def get_stats(self) -> OptimizationStats:
        """Get optimizer statistics."""
        return self.stats


# ============================================================================
# Public API
# ============================================================================


def create_sample_history() -> List[WorkflowExecution]:
    """Create sample workflow history for testing."""
    return [
        WorkflowExecution(
            change_id="change-001",
            timestamp="2025-10-20T10:00:00",
            change_type="docs",
            file_count=2,
            file_types=[".md"],
            stages_executed=[0, 1, 2, 3],
            duration_seconds=50,
            success=True,
            quality_gates_passed=4,
        ),
        WorkflowExecution(
            change_id="change-002",
            timestamp="2025-10-20T11:00:00",
            change_type="bugfix",
            file_count=3,
            file_types=[".py"],
            stages_executed=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            duration_seconds=450,
            success=True,
            quality_gates_passed=10,
        ),
        WorkflowExecution(
            change_id="change-003",
            timestamp="2025-10-20T12:00:00",
            change_type="feature",
            file_count=5,
            file_types=[".py", ".md"],
            stages_executed=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            duration_seconds=520,
            success=True,
            quality_gates_passed=10,
        ),
        WorkflowExecution(
            change_id="change-004",
            timestamp="2025-10-20T13:00:00",
            change_type="refactor",
            file_count=8,
            file_types=[".py"],
            stages_executed=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            duration_seconds=480,
            success=True,
            quality_gates_passed=10,
        ),
        WorkflowExecution(
            change_id="change-005",
            timestamp="2025-10-20T14:00:00",
            change_type="chore",
            file_count=1,
            file_types=[".yaml"],
            stages_executed=[0, 1, 2, 3],
            duration_seconds=45,
            success=True,
            quality_gates_passed=4,
        ),
        WorkflowExecution(
            change_id="change-006",
            timestamp="2025-10-20T15:00:00",
            change_type="feature",
            file_count=10,
            file_types=[".py", ".md", ".yaml"],
            stages_executed=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            duration_seconds=1200,
            success=True,
            quality_gates_passed=13,
        ),
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Test basic functionality
    predictor = StagePredictor()

    # Test with sample history
    sample_history = create_sample_history()

    # Train model
    success, error = predictor.train(sample_history)
    print(f"Training: success={success}, error={error}")

    # Make predictions
    stages, confidence = predictor.predict(
        "feature", file_count=5, file_types=[".py", ".md"]
    )
    print(f"Predicted stages: {stages}, confidence: {confidence:.2f}")

    # Estimate time
    duration = predictor.estimate_execution_time(stages)
    print(f"Estimated duration: {duration:.0f}s")

    # Get recommendations
    recs = predictor.get_recommendations()
    print(f"Recommendations: {len(recs)}")
    for rec in recs:
        print(f"  - {rec.title}: {rec.rationale}")
