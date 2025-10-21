"""
OpenSpec Governance Module
Provides automated management and validation for OpenSpec changes
"""

# Removed unused imports: os, json, yaml
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenSpecChange:
    """Represents a single OpenSpec change proposal"""

    def __init__(self, change_id: str, base_path: Path):
        self.change_id = change_id
        self.base_path = base_path
        self.change_path = base_path / "openspec" / "changes" / change_id

    def exists(self) -> bool:
        """Check if change directory exists"""
        return self.change_path.exists()

    def get_proposal(self) -> Dict[str, Any]:
        """Parse and return proposal.md content"""
        proposal_file = self.change_path / "proposal.md"
        if not proposal_file.exists():
            return {"error": "proposal.md not found"}

        try:
            content = proposal_file.read_text(encoding="utf-8")
            return self._parse_proposal(content)
        except Exception as e:
            return {"error": f"Failed to parse proposal: {str(e)}"}

    def get_tasks(self) -> Dict[str, Any]:
        """Parse and return tasks.md content with completion status"""
        tasks_file = self.change_path / "tasks.md"
        if not tasks_file.exists():
            return {"error": "tasks.md not found"}

        try:
            content = tasks_file.read_text(encoding="utf-8")
            return self._parse_tasks(content)
        except Exception as e:
            return {"error": f"Failed to parse tasks: {str(e)}"}

    def validate(self) -> Dict[str, Any]:
        """Validate the change proposal"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": [],
        }

        # Check required files
        required_files = ["proposal.md", "tasks.md"]
        for filename in required_files:
            if not (self.change_path / filename).exists():
                validation_results["errors"].append(
                    f"Missing required file: {filename}"
                )
                validation_results["valid"] = False

        # Validate proposal format
        proposal = self.get_proposal()
        if "error" in proposal:
            validation_results["errors"].append(
                f"Proposal validation: {proposal['error']}"
            )
            validation_results["valid"] = False
        else:
            if not proposal.get("why"):
                validation_results["warnings"].append("Proposal missing 'Why' section")
            if not proposal.get("what_changes"):
                validation_results["warnings"].append(
                    "Proposal missing 'What Changes' section"
                )
            if not proposal.get("impact"):
                validation_results["warnings"].append(
                    "Proposal missing 'Impact' section"
                )

        # Validate tasks format
        tasks = self.get_tasks()
        if "error" in tasks:
            validation_results["errors"].append(f"Tasks validation: {tasks['error']}")
            validation_results["valid"] = False
        else:
            total_tasks = tasks.get("total_tasks", 0)
            if total_tasks == 0:
                validation_results["warnings"].append("No tasks defined")

            completion_rate = tasks.get("completion_rate", 0)
            completed = tasks.get("completed_tasks", 0)
            validation_results["info"].append(
                f"Task completion: {completion_rate:.1f}% ({completed}/{total_tasks})"
            )

        return validation_results

    def get_status(self) -> str:
        """Determine change status based on content and completion"""
        if not self.exists():
            return "not_found"

        tasks = self.get_tasks()
        if "error" in tasks:
            return "invalid"

        completion_rate = tasks.get("completion_rate", 0)
        if completion_rate == 100:
            return "completed"
        elif completion_rate > 0:
            return "in_progress"
        else:
            return "pending"

    def _parse_checklist_items(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse markdown checklist items into a structured list."""
        items: List[Dict[str, Any]] = []
        for raw in lines:
            s = raw.strip()
            if s.startswith("- [ ]") or s.startswith("- [x]"):
                items.append(
                    {
                        "text": s[5:].strip(),
                        "completed": s.startswith("- [x]"),
                    }
                )
        return items

    def _finalize_section(
        self,
        result: Dict[str, Any],
        current_section: Optional[str],
        current_content: List[str],
    ) -> None:
        """Finalize and store the current section into the result map."""
        if current_section and current_content:
            section_text = "\n".join(current_content).strip()
            if current_section == "acceptance_criteria":
                result[current_section] = self._parse_checklist_items(current_content)
            else:
                result[current_section] = section_text

    def _parse_proposal(self, content: str) -> Dict[str, Any]:
        """Parse proposal.md markdown content"""
        result = {
            "title": "",
            "why": "",
            "what_changes": "",
            "impact": "",
            "implementation_plan": "",
            "acceptance_criteria": [],
            "security_considerations": "",
        }

        lines = content.split("\n")
        current_section: Optional[str] = None
        current_content: List[str] = []

        for line in lines:
            s = line.strip()
            if s.startswith("# "):
                result["title"] = s[2:].strip()
            elif s.startswith("## "):
                # Save previous section
                self._finalize_section(result, current_section, current_content)

                # Start new section
                section_name = s[3:].strip().lower().replace(" ", "_")
                current_section = section_name
                current_content = []
            else:
                if current_section:
                    current_content.append(s)

        # Handle last section
        self._finalize_section(result, current_section, current_content)

        return result

    def _parse_tasks(self, content: str) -> Dict[str, Any]:
        """Parse tasks.md content and calculate completion status"""
        result = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "completion_rate": 0,
            "task_sections": [],
            "all_tasks": [],
        }

        lines = content.split("\n")
        current_section: Optional[str] = None
        current_tasks: List[Dict[str, Any]] = []

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("## "):
                # Save previous section
                if current_section and current_tasks:
                    result["task_sections"].append(
                        {
                            "name": current_section,
                            "tasks": current_tasks.copy(),
                        }
                    )

                # Start new section
                current_section = line_stripped[3:].strip()
                current_tasks = []
            elif line_stripped.startswith("- [ ]") or line_stripped.startswith("- [x]"):
                # Task item
                task = {
                    "text": line_stripped[5:].strip(),
                    "completed": line_stripped.startswith("- [x]"),
                    "indent_level": (len(line) - len(line.lstrip())) // 2,
                }
                current_tasks.append(task)
                result["all_tasks"].append(task)
                result["total_tasks"] += 1
                if task["completed"]:
                    result["completed_tasks"] += 1

        # Handle last section
        if current_section and current_tasks:
            result["task_sections"].append(
                {"name": current_section, "tasks": current_tasks}
            )

        # Calculate completion rate
        if result["total_tasks"] > 0:
            result["completion_rate"] = (
                result["completed_tasks"] / result["total_tasks"]
            ) * 100

        return result


class OpenSpecGovernance:
    """Main governance system for managing OpenSpec changes"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.changes_path = self.base_path / "openspec" / "changes"
        self.specs_path = self.base_path / "openspec" / "specs"
        self.archive_path = self.changes_path / "archive"

    def list_changes(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        """List all OpenSpec changes with their status"""
        changes = []

        if not self.changes_path.exists():
            return changes

        for change_dir in self.changes_path.iterdir():
            if not change_dir.is_dir():
                continue

            # Skip archive directory unless explicitly requested
            if change_dir.name == "archive" and not include_archived:
                continue

            # Handle archived changes
            if change_dir.name == "archive" and include_archived:
                for archived_change in change_dir.iterdir():
                    if archived_change.is_dir():
                        change_id = archived_change.name
                        change = OpenSpecChange(change_id, self.base_path)
                        # Override path for archived changes
                        change.change_path = archived_change
                        changes.append(
                            {
                                "change_id": change_id,
                                "status": "archived",
                                "archived": True,
                                "path": str(archived_change),
                                "modified": datetime.fromtimestamp(
                                    archived_change.stat().st_mtime
                                ).isoformat(),
                            }
                        )
                continue

            change_id = change_dir.name
            change = OpenSpecChange(change_id, self.base_path)

            changes.append(
                {
                    "change_id": change_id,
                    "status": change.get_status(),
                    "archived": False,
                    "path": str(change_dir),
                    "modified": datetime.fromtimestamp(
                        change_dir.stat().st_mtime
                    ).isoformat(),
                }
            )

        # Sort deterministically by numeric part of change_id ascending (change-001, change-002, ...)
        def _change_sort_key(item: Dict[str, Any]):
            cid = item.get("change_id", "")
            try:
                # Extract numeric suffix, default to large number if not present
                part = cid.split("-")[-1]
                return int(part)
            except Exception:
                return 10**9

        return sorted(changes, key=_change_sort_key)

    def get_change_details(self, change_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific change"""
        change = OpenSpecChange(change_id, self.base_path)

        if not change.exists():
            return {"error": f"Change '{change_id}' not found"}

        return {
            "change_id": change_id,
            "status": change.get_status(),
            "proposal": change.get_proposal(),
            "tasks": change.get_tasks(),
            "validation": change.validate(),
        }

    def validate_change(self, change_id: str) -> Dict[str, Any]:
        """Validate a specific change"""
        change = OpenSpecChange(change_id, self.base_path)

        if not change.exists():
            return {"error": f"Change '{change_id}' not found"}

        return change.validate()

    def apply_change(self, change_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """Apply an approved change (implementation would depend on change type)"""
        change = OpenSpecChange(change_id, self.base_path)

        if not change.exists():
            return {"error": f"Change '{change_id}' not found"}

        validation = change.validate()
        if not validation["valid"]:
            return {"error": "Change validation failed", "validation": validation}

        tasks = change.get_tasks()
        if tasks.get("completion_rate", 0) < 100:
            return {"error": "Change not ready for application - tasks incomplete"}

        # This is a placeholder - actual implementation would depend on change type
        result = {
            "success": not dry_run,
            "dry_run": dry_run,
            "actions_taken": [],
            "warnings": [],
        }

        if dry_run:
            result["actions_taken"].append(
                "DRY RUN: Would apply change to " "specifications"
            )
        else:
            result["actions_taken"].append("Applied change to specifications")
            # Actual application logic would go here

        return result

    def archive_change(
        self,
        change_id: str,
        create_timestamp: bool = True,
    ) -> Dict[str, Any]:
        """Archive a completed change"""
        change = OpenSpecChange(change_id, self.base_path)

        if not change.exists():
            return {"error": f"Change '{change_id}' not found"}

        if change.get_status() != "completed":
            return {"error": "Only completed changes can be archived"}

        # Create archive directory if it doesn't exist
        self.archive_path.mkdir(exist_ok=True)

        # Determine archive name
        if create_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            archive_name = f"{timestamp}-{change_id}"
        else:
            archive_name = change_id

        archive_dest = self.archive_path / archive_name

        try:
            shutil.move(str(change.change_path), str(archive_dest))
            return {
                "success": True,
                "archived_to": str(archive_dest),
                "original_path": str(change.change_path),
            }
        except Exception as e:
            return {"error": f"Failed to archive change: {str(e)}"}

    def bulk_validate(self, change_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate multiple changes in bulk"""
        if change_ids is None:
            # Validate all non-archived changes
            all_changes = self.list_changes(include_archived=False)
            change_ids = [c["change_id"] for c in all_changes]

        results = {}
        summary = {
            "total": len(change_ids),
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
        }

        for change_id in change_ids:
            validation = self.validate_change(change_id)
            results[change_id] = validation

            if "error" in validation:
                summary["invalid"] += 1
            elif validation.get("valid", False):
                summary["valid"] += 1
                if validation.get("warnings"):
                    summary["warnings"] += 1
            else:
                summary["invalid"] += 1

        return {
            "summary": summary,
            "results": results,
        }

    def get_governance_metrics(self) -> Dict[str, Any]:
        """Get overall governance metrics and statistics"""
        all_changes = self.list_changes(include_archived=True)

        status_counts = {}
        for change in all_changes:
            status = change["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate completion metrics
        non_archived = [c for c in all_changes if not c.get("archived", False)]
        total_tasks = 0
        completed_tasks = 0

        for change in non_archived:
            change_details = self.get_change_details(change["change_id"])
            if "tasks" in change_details and "error" not in change_details["tasks"]:
                tasks = change_details["tasks"]
                total_tasks += tasks.get("total_tasks", 0)
                completed_tasks += tasks.get("completed_tasks", 0)

        overall_completion = (completed_tasks / max(total_tasks, 1)) * 100

        return {
            "total_changes": len(all_changes),
            "status_distribution": status_counts,
            "active_changes": len(non_archived),
            "archived_changes": len(
                [c for c in all_changes if c.get("archived", False)]
            ),
            "overall_task_completion": round(overall_completion, 1),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
        }


# Factory function for easy initialization
def get_openspec_governance(base_path: str = ".") -> OpenSpecGovernance:
    """Get OpenSpec governance instance"""
    return OpenSpecGovernance(base_path)
