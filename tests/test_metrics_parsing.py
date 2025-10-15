import re
import pytest
from pathlib import Path

# Coverage extraction helpers from scripts/update_test_metrics.py
COVERAGE_PATTERNS = [
    re.compile(r'<span class="pc_cov">(\d+)%</span>'),
    re.compile(r'(\d+)%\s+coverage', re.IGNORECASE),
]

PYTEST_SUMMARY_PATTERNS = [
    re.compile(r"(\d+) passed(?:,\s*(\d+) failed)?(?:,\s*(\d+) skipped)?.*? in ([0-9.]+s)"),
    re.compile(r"(\d+) passed.*? in ([0-9.]+s)"),
]

def test_coverage_patterns():
    html1 = '<span class="pc_cov">97%</span>'
    html2 = '97% coverage of lines'
    assert COVERAGE_PATTERNS[0].search(html1).group(1) == '97'
    assert COVERAGE_PATTERNS[1].search(html2).group(1) == '97'


def test_pytest_summary_patterns():
    out1 = '684 passed, 2 failed, 1 skipped in 141.90s'
    out2 = '691 passed in 120.31s'
    m1 = PYTEST_SUMMARY_PATTERNS[0].search(out1)
    m2 = PYTEST_SUMMARY_PATTERNS[1].search(out2)
    assert m1.group(1) == '684'
    assert m1.group(2) == '2'
    assert m1.group(3) == '1'
    assert m1.group(4) == '141.90s'
    assert m2.group(1) == '691'
    assert m2.group(2) == '120.31s'
