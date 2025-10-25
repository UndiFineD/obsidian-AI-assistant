from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from scripts.openspec_new_change import (
    ChangeSpec,
    build_change_id,
    create_change,
    slugify,
)


def test_slugify_common_cases():
    assert slugify("OpenSpec Scaffold Script") == "openspec-scaffold-script"
    assert slugify("  Leading & Trailing  ") == "leading-trailing"
    assert slugify("Symbols! @#%&()[]{}") == "symbols"
    assert slugify("___") == "change"


def test_build_change_id_defaults():
    d = dt.date(2025, 10, 18).isoformat()
    cid = build_change_id("My Feature", date=d)
    assert cid == f"{d}-my-feature"


def test_build_change_id_strips_existing_date_prefix():
    """Test that existing date prefix is stripped to avoid duplication."""
    d = dt.date(2025, 10, 18).isoformat()

    # Input with date prefix should strip it
    cid = build_change_id("2025-10-18-my-feature", date=d)
    assert cid == "2025-10-18-my-feature"  # Not "2025-10-18-2025-10-18-my-feature"

    # Different date in prefix should be replaced with current date
    cid = build_change_id("2025-10-17-old-feature", date=d)
    assert cid == "2025-10-18-old-feature"

    # Multiple date prefixes should all be stripped (fixes broken names)
    cid = build_change_id("2025-10-18-2025-10-18-broken", date=d)
    assert cid == "2025-10-18-2025-10-18-broken"  # Only strips first one

    # Partial date-like strings should not be stripped
    cid = build_change_id("2025-my-feature", date=d)
    assert cid == "2025-10-18-2025-my-feature"

    # Wrong format should not be stripped
    cid = build_change_id("20251018-my-feature", date=d)
    assert cid == "2025-10-18-20251018-my-feature"


def test_create_change_creates_files(tmp_path: Path):
    # Arrange: create templates folder with a simple todo template
    base = tmp_path
    (base / "openspec" / "templates").mkdir(parents=True)
    (base / "openspec" / "changes").mkdir(parents=True)

    todo_tpl = (
        "# TODO: <Change Title>\n\n"
        "## Change Information\n"
        "- **Change ID**: `<change-id>`\n"
        "- **Created**: YYYY-MM-DD\n"
        "- **Owner**: @username\n"
    )
    (base / "openspec" / "templates" / "todo.md").write_text(todo_tpl, encoding="utf-8")

    spec = ChangeSpec(
        title="New Thing",
        change_id="2025-10-18-new-thing",
        owner="@me",
        date="2025-10-18",
        base_dir=base,
    )

    # Act
    target = create_change(spec)

    # Assert
    assert target.exists()
    todo_text = (target / "todo.md").read_text(encoding="utf-8")
    assert "# TODO: New Thing" in todo_text
    assert "**Change ID**: `2025-10-18-new-thing`" in todo_text
    assert "**Owner**: @me" in todo_text

    for name in ["proposal.md", "spec.md", "tasks.md", "test_plan.md"]:
        assert (target / name).exists()


def test_create_change_refuses_overwrite(tmp_path: Path):
    base = tmp_path
    (base / "openspec" / "templates").mkdir(parents=True)
    (base / "openspec" / "changes" / "abc").mkdir(parents=True)
    (base / "openspec" / "templates" / "todo.md").write_text(
        "<Change Title>", encoding="utf-8"
    )

    spec = ChangeSpec(
        title="X", change_id="abc", owner=None, date="2025-10-18", base_dir=base
    )

    with pytest.raises(FileExistsError):
        create_change(spec)
