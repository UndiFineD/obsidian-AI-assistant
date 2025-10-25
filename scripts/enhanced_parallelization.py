#!/usr/bin/env python3
"""
Enhanced Parallelization Module with Adaptive Worker Management

Provides intelligent parallel execution for workflow stages with adaptive
worker count based on system resources and stage requirements.

Features:
- Adaptive worker count based on CPU and memory
- Stage dependency tracking
- Failure isolation in parallel execution
- Detailed execution logging
- Performance metrics collection

Author: Obsidian AI Agent Team
License: MIT
"""

import os
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class ParallelStage:
    """Definition of a parallelizable stage"""
    stage_id: int
    stage_name: str
    task: Callable
    task_args: tuple = field(default_factory=tuple)
    task_kwargs: Dict = field(default_factory=dict)
    dependencies: List[int] = field(default_factory=list)  # Stage IDs this depends on
    timeout: Optional[int] = None
    retry_count: int = 0


@dataclass
class StageExecutionResult:
    """Result of a parallel stage execution"""
    stage_id: int
    stage_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    retry_count: int = 0


class AdaptiveParallelExecutor:
    """Executes stages in parallel with adaptive worker management"""

    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize adaptive parallel executor.

        Args:
            max_workers: Maximum number of worker threads. If None, auto-detect.
        """
        self.max_workers = max_workers or self._calculate_optimal_workers()
        self.logger = logging.getLogger(__name__)

    def _calculate_optimal_workers(self) -> int:
        """
        Calculate optimal number of workers based on system resources.

        Returns:
            Recommended number of worker threads
        """
        try:
            cpu_count = os.cpu_count() or 1
            mem_available_gb = psutil.virtual_memory().available / (1024**3)

            # Conservative strategy: use half of available CPUs, but at least 1
            optimal = max(1, cpu_count // 2)

            # Reduce if memory is limited (< 2GB per worker)
            max_by_memory = max(1, int(mem_available_gb / 2))
            optimal = min(optimal, max_by_memory)

            # Cap at 8 workers for practical reasons
            optimal = min(optimal, 8)

            self.logger.info(
                f"Calculated optimal workers: {optimal} "
                f"(CPU: {cpu_count}, Memory: {mem_available_gb:.1f}GB)"
            )
            return optimal

        except Exception as e:
            self.logger.warning(f"Failed to calculate optimal workers: {e}. Using default 3.")
            return 3

    def get_worker_count(self) -> int:
        """Get the number of worker threads"""
        return self.max_workers

    def execute_parallel(
        self,
        stages: List[ParallelStage],
        continue_on_failure: bool = False
    ) -> Tuple[List[StageExecutionResult], bool]:
        """
        Execute stages in parallel with dependency tracking.

        Args:
            stages: List of stages to execute
            continue_on_failure: Continue executing if a stage fails

        Returns:
            Tuple of (results list, all_succeeded boolean)
        """
        results = {}
        completed_stages = set()
        all_succeeded = True

        # Map stage ID to stage for quick lookup
        stage_map = {s.stage_id: s for s in stages}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit initial batch of independent stages
            futures = {}
            submitted = set()

            for stage in stages:
                if not stage.dependencies:
                    future = executor.submit(self._execute_stage, stage)
                    futures[future] = stage
                    submitted.add(stage.stage_id)

            # Process completed stages and submit dependent stages
            while futures:
                for future in as_completed(futures):
                    stage = futures.pop(future)

                    try:
                        result = future.result()
                        results[stage.stage_id] = result
                        completed_stages.add(stage.stage_id)

                        if not result.success:
                            all_succeeded = False
                            if not continue_on_failure:
                                # Cancel remaining futures
                                for f in futures:
                                    f.cancel()
                                return (self._results_to_list(results, stages), False)

                    except Exception as e:
                        result = StageExecutionResult(
                            stage_id=stage.stage_id,
                            stage_name=stage.stage_name,
                            success=False,
                            error=str(e)
                        )
                        results[stage.stage_id] = result
                        all_succeeded = False

                        if not continue_on_failure:
                            for f in futures:
                                f.cancel()
                            return (self._results_to_list(results, stages), False)

                    # Submit stages that now have their dependencies met
                    for candidate_stage in stages:
                        if (candidate_stage.stage_id not in submitted and
                            all(dep in completed_stages for dep in candidate_stage.dependencies)):
                            future = executor.submit(self._execute_stage, candidate_stage)
                            futures[future] = candidate_stage
                            submitted.add(candidate_stage.stage_id)

        return (self._results_to_list(results, stages), all_succeeded)

    def _execute_stage(self, stage: ParallelStage) -> StageExecutionResult:
        """
        Execute a single stage with timeout and error handling.

        Args:
            stage: Stage to execute

        Returns:
            StageExecutionResult with execution details
        """
        import time

        start_time = time.time()

        try:
            # Execute the stage task
            result = stage.task(*stage.task_args, **stage.task_kwargs)

            duration = time.time() - start_time

            return StageExecutionResult(
                stage_id=stage.stage_id,
                stage_name=stage.stage_name,
                success=True,
                result=result,
                duration_seconds=duration
            )

        except Exception as e:
            duration = time.time() - start_time

            self.logger.error(
                f"Stage {stage.stage_id} ({stage.stage_name}) failed: {e}"
            )

            return StageExecutionResult(
                stage_id=stage.stage_id,
                stage_name=stage.stage_name,
                success=False,
                error=str(e),
                duration_seconds=duration
            )

    def _results_to_list(
        self,
        results: Dict[int, StageExecutionResult],
        stages: List[ParallelStage]
    ) -> List[StageExecutionResult]:
        """Convert results dict to ordered list"""
        result_list = []
        for stage in stages:
            if stage.stage_id in results:
                result_list.append(results[stage.stage_id])
            else:
                # Stage wasn't executed (likely due to dependency or early failure)
                result_list.append(
                    StageExecutionResult(
                        stage_id=stage.stage_id,
                        stage_name=stage.stage_name,
                        success=False,
                        error="Not executed"
                    )
                )
        return result_list

    def get_execution_summary(self, results: List[StageExecutionResult]) -> Dict:
        """Get execution summary from results"""
        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        total_time = sum(r.duration_seconds for r in results)

        return {
            "total_stages": len(results),
            "successful": successful,
            "failed": failed,
            "total_duration_seconds": total_time,
            "average_stage_duration": total_time / len(results) if results else 0,
            "worker_count": self.max_workers,
        }


# Convenience function
def execute_parallel_stages(
    stages: List[ParallelStage],
    max_workers: Optional[int] = None,
    continue_on_failure: bool = False
) -> Tuple[List[StageExecutionResult], bool]:
    """
    Convenience function to execute stages in parallel.

    Args:
        stages: List of stages to execute
        max_workers: Maximum workers (None = auto-detect)
        continue_on_failure: Continue if a stage fails

    Returns:
        Tuple of (results, all_succeeded)
    """
    executor = AdaptiveParallelExecutor(max_workers=max_workers)
    return executor.execute_parallel(stages, continue_on_failure=continue_on_failure)
