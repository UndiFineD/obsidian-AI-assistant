#!/usr/bin/env python3
"""
OpenSpec Backlog Management Tool

List, analyze, and visualize OpenSpec changes with ASCII burndown charts.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


def find_changes_directory() -> Path:
    """Find the openspec/changes directory relative to script location."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    changes_dir = project_root / "openspec" / "changes"
    
    if not changes_dir.exists():
        raise FileNotFoundError(f"Changes directory not found: {changes_dir}")
    
    return changes_dir


def parse_change_id(change_id: str) -> Dict[str, any]:
    """
    Parse change ID to extract metadata.
    
    Format: YYYY-MM-DD-description or description
    """
    date_pattern = r'^(\d{4})-(\d{2})-(\d{2})-(.+)$'
    match = re.match(date_pattern, change_id)
    
    if match:
        year, month, day, description = match.groups()
        try:
            date = datetime(int(year), int(month), int(day))
            return {
                'id': change_id,
                'date': date,
                'description': description,
                'has_date': True
            }
        except ValueError:
            pass
    
    # No date prefix or invalid date
    return {
        'id': change_id,
        'date': None,
        'description': change_id,
        'has_date': False
    }


def get_change_age_days(change_info: Dict) -> Optional[int]:
    """Calculate age of change in days."""
    if not change_info['has_date'] or not change_info['date']:
        return None
    
    delta = datetime.now() - change_info['date']
    return delta.days


def list_active_changes(changes_dir: Path, exclude_archive: bool = True) -> List[Dict]:
    """
    List all active changes with metadata.
    
    Returns list of dicts with:
    - id: change identifier
    - date: creation date (if available)
    - description: change description
    - has_date: whether date prefix exists
    - age_days: age in days (if date available)
    - path: full path to change directory
    """
    changes = []
    
    for item in changes_dir.iterdir():
        if not item.is_dir():
            continue
        
        # Skip archive directory
        if exclude_archive and item.name == 'archive':
            continue
        
        change_info = parse_change_id(item.name)
        change_info['path'] = item
        change_info['age_days'] = get_change_age_days(change_info)
        
        changes.append(change_info)
    
    return changes


def generate_summary_stats(changes: List[Dict]) -> Dict:
    """Generate summary statistics for changes."""
    total = len(changes)
    with_dates = sum(1 for c in changes if c['has_date'])
    without_dates = total - with_dates
    
    aged_changes = [c for c in changes if c['age_days'] is not None]
    if aged_changes:
        avg_age = sum(c['age_days'] for c in aged_changes) / len(aged_changes)
        max_age = max(c['age_days'] for c in aged_changes)
        min_age = min(c['age_days'] for c in aged_changes)
    else:
        avg_age = max_age = min_age = None
    
    # Stale changes (>30 days)
    stale = sum(1 for c in aged_changes if c['age_days'] > 30)
    
    return {
        'total': total,
        'with_dates': with_dates,
        'without_dates': without_dates,
        'avg_age_days': avg_age,
        'max_age_days': max_age,
        'min_age_days': min_age,
        'stale_count': stale
    }


def generate_burndown_data(changes: List[Dict], days: int = 30) -> List[tuple]:
    """
    Generate burndown chart data for the last N days.
    
    Returns list of (date, count) tuples showing change count over time.
    """
    # Filter changes with dates
    dated_changes = [c for c in changes if c['has_date'] and c['date']]
    
    if not dated_changes:
        return []
    
    # Find date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Generate data points for each day
    burndown_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Count changes that existed on this date
        count = sum(1 for c in dated_changes if c['date'] <= current_date)
        burndown_data.append((current_date, count))
        current_date += timedelta(days=1)
    
    return burndown_data


def render_ascii_burndown(burndown_data: List[tuple], width: int = 60, height: int = 15) -> str:
    """
    Render ASCII burndown chart.
    
    Args:
        burndown_data: List of (date, count) tuples
        width: Chart width in characters
        height: Chart height in characters
    
    Returns:
        ASCII art string
    """
    if not burndown_data:
        return "No data available for burndown chart."
    
    # Extract counts
    counts = [count for _, count in burndown_data]
    max_count = max(counts) if counts else 1
    min_count = min(counts) if counts else 0
    
    # Calculate scale
    count_range = max_count - min_count if max_count > min_count else 1
    
    # Build chart
    lines = []
    lines.append("=" * (width + 10))
    lines.append(f"  Burndown Chart (Last {len(burndown_data)} days)")
    lines.append("=" * (width + 10))
    lines.append("")
    
    # Draw chart area
    for row in range(height):
        # Calculate threshold for this row (top to bottom = high to low)
        threshold = max_count - (row * count_range / (height - 1))
        
        # Y-axis label
        y_label = f"{int(threshold):3d} │"
        line = y_label
        
        # Plot points
        for col in range(len(burndown_data)):
            _, count = burndown_data[col]
            
            # Determine which character to use
            if count >= threshold:
                if col == 0 or burndown_data[col-1][1] < threshold:
                    char = '█'  # Start of filled area
                else:
                    char = '█'  # Continue filled area
            else:
                char = ' '
            
            # Scale column position
            scaled_col = int(col * width / len(burndown_data))
            if len(line) - len(y_label) <= scaled_col:
                line += char
        
        lines.append(line)
    
    # X-axis
    lines.append("    └" + "─" * width)
    
    # X-axis labels (start and end dates)
    start_date = burndown_data[0][0].strftime("%m/%d")
    end_date = burndown_data[-1][0].strftime("%m/%d")
    x_label = f"     {start_date}" + " " * (width - len(start_date) - len(end_date) - 5) + f"{end_date}"
    lines.append(x_label)
    
    lines.append("")
    lines.append(f"  Current: {counts[-1]} active changes")
    lines.append(f"  Peak:    {max_count} active changes")
    lines.append(f"  Trend:   {'+' if counts[-1] > counts[0] else '-'}{abs(counts[-1] - counts[0])} changes")
    lines.append("=" * (width + 10))
    
    return "\n".join(lines)


def print_change_list(changes: List[Dict], sort_by: str = 'date', limit: Optional[int] = None):
    """Print formatted list of changes."""
    # Sort changes
    if sort_by == 'date':
        changes = sorted(changes, key=lambda c: c['date'] if c['date'] else datetime.min, reverse=True)
    elif sort_by == 'age':
        changes = sorted(changes, key=lambda c: c['age_days'] if c['age_days'] is not None else -1, reverse=True)
    elif sort_by == 'name':
        changes = sorted(changes, key=lambda c: c['id'])
    
    # Apply limit
    if limit:
        changes = changes[:limit]
    
    print(f"\n{'ID':<50} {'Age':<10} {'Date':<12}")
    print("=" * 75)
    
    for change in changes:
        age_str = f"{change['age_days']}d" if change['age_days'] is not None else "N/A"
        date_str = change['date'].strftime("%Y-%m-%d") if change['date'] else "N/A"
        
        print(f"{change['id']:<50} {age_str:<10} {date_str:<12}")


def main():
    parser = argparse.ArgumentParser(
        description="List and analyze OpenSpec changes with burndown visualization"
    )
    parser.add_argument(
        '--sort',
        choices=['date', 'age', 'name'],
        default='date',
        help="Sort changes by date (default), age, or name"
    )
    parser.add_argument(
        '--limit',
        type=int,
        help="Limit number of changes displayed"
    )
    parser.add_argument(
        '--stale-only',
        action='store_true',
        help="Show only stale changes (>30 days old)"
    )
    parser.add_argument(
        '--burndown',
        action='store_true',
        help="Show ASCII burndown chart"
    )
    parser.add_argument(
        '--burndown-days',
        type=int,
        default=30,
        help="Number of days for burndown chart (default: 30)"
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help="Show summary statistics only"
    )
    parser.add_argument(
        '--include-archive',
        action='store_true',
        help="Include archived changes in analysis"
    )
    
    args = parser.parse_args()
    
    try:
        # Find changes directory
        changes_dir = find_changes_directory()
        
        # List changes
        changes = list_active_changes(changes_dir, exclude_archive=not args.include_archive)
        
        # Filter stale if requested
        if args.stale_only:
            changes = [c for c in changes if c['age_days'] and c['age_days'] > 30]
        
        # Generate stats
        stats = generate_summary_stats(changes)
        
        # Print summary
        print("\n" + "=" * 75)
        print("  OpenSpec Changes Summary")
        print("=" * 75)
        print(f"  Total Changes:      {stats['total']}")
        print(f"  With Dates:         {stats['with_dates']}")
        print(f"  Without Dates:      {stats['without_dates']}")
        
        if stats['avg_age_days'] is not None:
            print(f"  Average Age:        {stats['avg_age_days']:.1f} days")
            print(f"  Oldest Change:      {stats['max_age_days']} days")
            print(f"  Newest Change:      {stats['min_age_days']} days")
            print(f"  Stale Changes:      {stats['stale_count']} (>30 days)")
        
        print("=" * 75)
        
        # Show burndown chart if requested
        if args.burndown:
            burndown_data = generate_burndown_data(changes, days=args.burndown_days)
            if burndown_data:
                print("\n" + render_ascii_burndown(burndown_data))
            else:
                print("\nNo dated changes available for burndown chart.")
        
        # Show change list unless summary-only
        if not args.summary:
            print_change_list(changes, sort_by=args.sort, limit=args.limit)
            print()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
