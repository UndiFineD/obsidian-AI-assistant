#!/usr/bin/env python3
"""
Workflow Resumption Module - Checkpoint-based Recovery

Enables resumption of interrupted workflows from the last completed stage.
Detects incomplete workflows, prompts user for recovery options, and restores
execution state from saved checkpoints.

Features:
- Automatic detection of incomplete workflows
- Interactive resume/restart prompts
- Checkpoint recovery from .checkpoints/state.json
- Timing preservation across resumptions
- Detailed resumption reports
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class WorkflowResumption:
    """Handle workflow resumption and checkpoint management"""

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize resumption handler.

        Args:
            checkpoint_dir: Directory containing checkpoint files (default: .checkpoints/)
        """
        self.checkpoint_dir = checkpoint_dir or Path.cwd() / ".checkpoints"
        self.state_file = self.checkpoint_dir / "state.json"
        self.status_file = self.checkpoint_dir / "status.json"

    def detect_incomplete_workflow(self, change_id: str) -> Optional[Dict[str, Any]]:
        """
        Detect if there's an incomplete workflow for the given change ID.

        Args:
            change_id: The workflow change ID to check

        Returns:
            Workflow info dict if incomplete, None otherwise
        """
        if not self.state_file.exists():
            return None

        try:
            state = json.loads(self.state_file.read_text(encoding="utf-8"))
            workflow = state.get("workflows", {}).get(change_id)

            if workflow is None:
                return None

            # Check if workflow is incomplete
            status = workflow.get("status")
            if status == "INCOMPLETE":
                return workflow
            return None

        except Exception:
            return None

    def get_incomplete_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get all incomplete workflows"""
        if not self.state_file.exists():
            return {}

        try:
            state = json.loads(self.state_file.read_text(encoding="utf-8"))
            incomplete = {}
            for change_id, workflow in state.get("workflows", {}).items():
                if workflow.get("status") == "INCOMPLETE":
                    incomplete[change_id] = workflow
            return incomplete
        except Exception:
            return {}

    def prompt_for_recovery(self, workflow: Dict[str, Any]) -> str:
        """
        Prompt user to resume or restart workflow.

        Args:
            workflow: Workflow information dict

        Returns:
            "resume" or "restart"
        """
        change_id = workflow.get("change_id", "unknown")
        last_stage = workflow.get("last_completed_stage", 0)
        stage_name = workflow.get("last_stage_name", "unknown")

        print("\n" + "=" * 70)
        print("⚠️  INCOMPLETE WORKFLOW DETECTED")
        print("=" * 70)
        print(f"\nChange ID: {change_id}")
        print(f"Last completed: Stage {last_stage} - {stage_name}")
        print(f"Last updated: {workflow.get('last_updated', 'unknown')}")
        print("\n" + "-" * 70)
        print("Options:")
        print("  1. Resume from stage {} ({})".format(last_stage + 1, workflow.get("next_stage_name", "unknown")))
        print("  2. Start fresh (will recreate files)")
        print("  3. Cancel")
        print("-" * 70)

        while True:
            choice = input("\nEnter choice (1-3): ").strip()
            if choice == "1":
                return "resume"
            elif choice == "2":
                return "restart"
            elif choice == "3":
                return "cancel"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    def load_checkpoint(self, stage_num: int) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint data for a specific stage.

        Args:
            stage_num: Stage number to load checkpoint for

        Returns:
            Checkpoint data dict or None if not found
        """
        checkpoint_file = self.checkpoint_dir / f"checkpoint-{stage_num}.json"

        if not checkpoint_file.exists():
            return None

        try:
            return json.loads(checkpoint_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def save_checkpoint(self, stage_num: int, data: Dict[str, Any]) -> bool:
        """
        Save checkpoint data for a stage.

        Args:
            stage_num: Stage number
            data: Data to save

        Returns:
            True if successful
        """
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_file = self.checkpoint_dir / f"checkpoint-{stage_num}.json"

        try:
            # Add metadata
            checkpoint = {
                "stage": stage_num,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }
            checkpoint_file.write_text(
                json.dumps(checkpoint, indent=2),
                encoding="utf-8",
            )
            return True
        except Exception:
            return False

    def update_workflow_state(
        self,
        change_id: str,
        status: str,
        last_completed_stage: int,
        last_stage_name: str,
        next_stage_num: int,
        next_stage_name: str,
    ) -> bool:
        """
        Update workflow state in state.json.

        Args:
            change_id: Workflow change ID
            status: Workflow status (INCOMPLETE, COMPLETED, FAILED)
            last_completed_stage: Last completed stage number
            last_stage_name: Name of last stage
            next_stage_num: Next stage to run
            next_stage_name: Name of next stage

        Returns:
            True if successful
        """
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load existing state
        state = {}
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Ensure workflows dict exists
        if "workflows" not in state:
            state["workflows"] = {}

        # Update workflow
        state["workflows"][change_id] = {
            "change_id": change_id,
            "status": status,
            "last_completed_stage": last_completed_stage,
            "last_stage_name": last_stage_name,
            "next_stage_num": next_stage_num,
            "next_stage_name": next_stage_name,
            "last_updated": datetime.now().isoformat(),
        }

        # Save state
        try:
            temp_file = self.state_file.with_suffix(".tmp")
            temp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            temp_file.replace(self.state_file)
            return True
        except Exception:
            return False

    def clear_workflow_state(self, change_id: str) -> bool:
        """
        Clear completed workflow state.

        Args:
            change_id: Workflow to clear

        Returns:
            True if successful
        """
        if not self.state_file.exists():
            return True

        try:
            state = json.loads(self.state_file.read_text(encoding="utf-8"))
            if change_id in state.get("workflows", {}):
                del state["workflows"][change_id]
                self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def get_resumption_report(self, workflow: Dict[str, Any]) -> str:
        """Generate a resumption report for the workflow"""
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    WORKFLOW RESUMPTION REPORT                     ║
╚═══════════════════════════════════════════════════════════════════╝

Change ID:              {workflow.get('change_id', 'unknown')}
Status:                 {workflow.get('status', 'unknown')}
Last Completed Stage:   {workflow.get('last_completed_stage', -1)} - {workflow.get('last_stage_name', 'unknown')}
Next Stage to Resume:   {workflow.get('next_stage_num', 0)} - {workflow.get('next_stage_name', 'unknown')}
Last Updated:           {workflow.get('last_updated', 'unknown')}

Saved Checkpoints:
"""
        checkpoint_dir = self.checkpoint_dir
        if checkpoint_dir.exists():
            checkpoints = sorted(checkpoint_dir.glob("checkpoint-*.json"))
            if checkpoints:
                for cp in checkpoints:
                    try:
                        cp_data = json.loads(cp.read_text(encoding="utf-8"))
                        stage = cp_data.get("stage", "?")
                        timestamp = cp_data.get("timestamp", "?")
                        report += f"  - Stage {stage}: {timestamp}\n"
                    except Exception:
                        pass
            else:
                report += "  - None available\n"
        else:
            report += "  - No checkpoint directory\n"

        report += "\n" + "=" * 70 + "\n"
        return report


def create_resumption_handler(checkpoint_dir: Optional[Path] = None) -> WorkflowResumption:
    """Factory function to create resumption handler"""
    return WorkflowResumption(checkpoint_dir)


if __name__ == "__main__":
    # Example usage
    handler = create_resumption_handler()

    # Update workflow state
    handler.update_workflow_state(
        change_id="test-change",
        status="INCOMPLETE",
        last_completed_stage=3,
        last_stage_name="Task Breakdown",
        next_stage_num=4,
        next_stage_name="Implementation Checklist",
    )

    # Detect incomplete workflow
    workflow = handler.detect_incomplete_workflow("test-change")
    if workflow:
        print(handler.get_resumption_report(workflow))
        print("Workflow found and can be resumed!")
    else:
        print("No incomplete workflow detected")

    # List all incomplete workflows
    incomplete = handler.get_incomplete_workflows()
    print(f"\nTotal incomplete workflows: {len(incomplete)}")
    for change_id, wf in incomplete.items():
        print(f"  - {change_id}: Stage {wf.get('last_completed_stage', 0)}")
