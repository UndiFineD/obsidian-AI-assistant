#!/bin/bash

###############################################################################
# CI/CD Lane Detection Automation Script
# 
# Purpose: Automatically detect which workflow lane to use based on changed files
# 
# Usage:
#   ./detect_lane.sh [base_ref] [head_ref]
#   ./detect_lane.sh main HEAD                          # Detect from main to HEAD
#   ./detect_lane.sh HEAD~1 HEAD                         # Detect from previous commit
#   export BASE_REF=main HEAD_REF=HEAD; ./detect_lane.sh # Use env vars
# 
# Output: Prints lane name (docs, standard, heavy) to stdout
# Exit Code: 0 (success), 1 (error), 2 (no changes)
# 
# Environment Variables:
#   BASE_REF           - Base git reference (default: main or origin/main)
#   HEAD_REF           - Head git reference (default: HEAD)
#   VERBOSE            - Enable verbose output (true/false, default: false)
#   SKIP_VERIFICATION  - Skip validation (for testing, default: false)
#
# Detected Lanes:
#   docs:     Only documentation, config, or markdown changes
#   standard: Mixed changes (code + docs, single feature)
#   heavy:    Complex changes (multiple features, large refactors, security updates)
#
# Detection Logic:
#   1. Analyze file types in changeset
#   2. Count files by category (code, docs, config, tests, infrastructure)
#   3. Check for specific patterns (breaking changes, security fixes, etc.)
#   4. Apply decision tree to determine lane
#   5. Output lane decision with confidence score
#
###############################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_REF="${BASE_REF:-}"
HEAD_REF="${HEAD_REF:-HEAD}"
VERBOSE="${VERBOSE:-false}"
SKIP_VERIFICATION="${SKIP_VERIFICATION:-false}"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}✓${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*" >&2
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

log_debug() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}DEBUG:${NC} $*" >&2
    fi
}

###############################################################################
# Determine base reference
###############################################################################
determine_base_ref() {
    if [[ -z "$BASE_REF" ]]; then
        # Try main first, then master, then origin/main
        if git rev-parse --verify main >/dev/null 2>&1; then
            BASE_REF="main"
        elif git rev-parse --verify origin/main >/dev/null 2>&1; then
            BASE_REF="origin/main"
        elif git rev-parse --verify master >/dev/null 2>&1; then
            BASE_REF="master"
        else
            log_error "Could not determine base reference. Set BASE_REF environment variable."
            return 1
        fi
    fi
    log_debug "Using base reference: $BASE_REF"
}

###############################################################################
# Get list of changed files
###############################################################################
get_changed_files() {
    local base="$1"
    local head="$2"
    
    # Get list of changed files (A=added, M=modified, D=deleted, R=renamed)
    git diff --name-status "$base" "$head" 2>/dev/null || {
        log_error "Failed to get changed files between $base and $head"
        return 1
    }
}

###############################################################################
# Categorize files by type
###############################################################################
categorize_files() {
    local file_list="$1"
    
    declare -A categories
    categories[docs]=0
    categories[code]=0
    categories[tests]=0
    categories[config]=0
    categories[infra]=0
    categories[security]=0
    categories[other]=0
    
    while IFS=$'\t' read -r status file; do
        # Skip deleted files for detection (they don't impact lane selection)
        if [[ "$status" == "D" ]]; then
            continue
        fi
        
        # Categorize by file path and extension
        if [[ "$file" =~ \.(md|txt|rst)$ ]] || [[ "$file" == "README"* ]] || [[ "$file" == "CHANGELOG"* ]]; then
            ((categories[docs]++))
        elif [[ "$file" =~ ^docs/ ]] || [[ "$file" =~ ^\.github/.*\.md$ ]]; then
            ((categories[docs]++))
        elif [[ "$file" =~ \.(yml|yaml)$ ]] && [[ "$file" =~ \.github/workflows ]] || [[ "$file" =~ Makefile ]]; then
            ((categories[infra]++))
        elif [[ "$file" =~ \.(py|js|ts|jsx|tsx)$ ]]; then
            if [[ "$file" =~ ^tests/ ]] || [[ "$file" =~ \.test\.(py|js|ts)$ ]] || [[ "$file" =~ \.spec\.(py|js|ts)$ ]]; then
                ((categories[tests]++))
            else
                ((categories[code]++))
            fi
        elif [[ "$file" =~ ^(setup|requirements|pyproject|package\.json|tsconfig|\.eslintrc) ]]; then
            ((categories[config]++))
        elif [[ "$file" =~ (security|auth|crypto|vault|encrypt) ]]; then
            ((categories[security]++))
        elif [[ "$file" =~ \.(json|toml|ini|conf)$ ]]; then
            ((categories[config]++))
        else
            ((categories[other]++))
        fi
    done <<< "$file_list"
    
    # Export results
    for category in "${!categories[@]}"; do
        echo "${category}=${categories[$category]}"
    done
}

###############################################################################
# Analyze commit messages for patterns
###############################################################################
analyze_commit_messages() {
    local base="$1"
    local head="$2"
    
    local commit_messages
    commit_messages=$(git log --pretty="%B" "$base..$head" 2>/dev/null || echo "")
    
    declare -A patterns
    patterns[breaking]=0
    patterns[security]=0
    patterns[refactor]=0
    patterns[feat]=0
    patterns[fix]=0
    
    if [[ -n "$commit_messages" ]]; then
        # Check for breaking changes
        if echo "$commit_messages" | grep -qi "BREAKING\|breaking change\|^!\|^.*!:"; then
            patterns[breaking]=1
        fi
        
        # Check for security fixes
        if echo "$commit_messages" | grep -qi "security\|vulnerability\|cve\|security fix"; then
            patterns[security]=1
        fi
        
        # Check for refactoring
        if echo "$commit_messages" | grep -qi "^refactor\|refactor:"; then
            patterns[refactor]=1
        fi
        
        # Check for new features
        if echo "$commit_messages" | grep -qi "^feat\|feature:"; then
            patterns[feat]=1
        fi
        
        # Check for bug fixes
        if echo "$commit_messages" | grep -qi "^fix\|fix:"; then
            patterns[fix]=1
        fi
    fi
    
    # Export results
    for pattern in "${!patterns[@]}"; do
        echo "${pattern}=${patterns[$pattern]}"
    done
}

###############################################################################
# Detect file size impact
###############################################################################
detect_file_impact() {
    local base="$1"
    local head="$2"
    
    local stats
    stats=$(git diff --stat "$base" "$head" 2>/dev/null || echo "")
    
    # Count total lines added/removed
    local total_adds=0
    local total_dels=0
    
    while read -r line; do
        # Parse: "file.py | 100 ++++++++------"
        if [[ "$line" =~ \|\ ([0-9]+)\ (.+)$ ]]; then
            local changes="${BASH_REMATCH[2]}"
            # Count + and - characters
            local adds=$(echo "$changes" | tr -cd '+' | wc -c)
            local dels=$(echo "$changes" | tr -cd '-' | wc -c)
            ((total_adds += adds))
            ((total_dels += dels))
        fi
    done <<< "$stats"
    
    echo "adds=$total_adds"
    echo "dels=$total_dels"
}

###############################################################################
# Decision tree for lane selection
###############################################################################
decide_lane() {
    # Parse inputs
    local docs_count=0
    local code_count=0
    local tests_count=0
    local config_count=0
    local infra_count=0
    local security_count=0
    local other_count=0
    local breaking_change=0
    local security_fix=0
    local refactor=0
    local feat_count=0
    local fix_count=0
    local adds=0
    local dels=0
    
    while IFS='=' read -r key value; do
        case "$key" in
            docs) docs_count=$value ;;
            code) code_count=$value ;;
            tests) tests_count=$value ;;
            config) config_count=$value ;;
            infra) infra_count=$value ;;
            security) security_count=$value ;;
            other) other_count=$value ;;
            breaking) breaking_change=$value ;;
            security) security_fix=$value ;;
            refactor) refactor=$value ;;
            feat) feat_count=$value ;;
            fix) fix_count=$value ;;
            adds) adds=$value ;;
            dels) dels=$value ;;
        esac
    done
    
    local total_code=$((code_count + tests_count))
    local total_changes=$((docs_count + code_count + tests_count + config_count + infra_count + other_count))
    
    log_debug "File counts: docs=$docs_count code=$code_count tests=$tests_count config=$config_count infra=$infra_count other=$other_count"
    log_debug "Patterns: breaking=$breaking_change security=$security_fix refactor=$refactor"
    log_debug "Impact: adds=$adds dels=$dels total_changes=$total_changes"
    
    # Decision Logic
    
    # HEAVY LANE: Critical changes requiring full validation
    if [[ $breaking_change -eq 1 ]] || [[ $security_fix -eq 1 ]]; then
        echo "heavy"
        return 0
    fi
    
    if [[ $refactor -eq 1 ]] && [[ $total_code -gt 10 ]]; then
        echo "heavy"
        return 0
    fi
    
    if [[ $infra_count -gt 0 ]] && [[ $total_code -gt 5 ]]; then
        echo "heavy"
        return 0
    fi
    
    # Large changes warrant heavy lane
    if [[ $total_changes -gt 20 ]] || [[ $adds -gt 500 ]]; then
        echo "heavy"
        return 0
    fi
    
    # DOCS LANE: Only documentation changes
    if [[ $code_count -eq 0 ]] && [[ $tests_count -eq 0 ]] && \
       [[ $config_count -eq 0 ]] && [[ $infra_count -eq 0 ]] && \
       [[ $security_count -eq 0 ]] && [[ $total_changes -gt 0 ]]; then
        echo "docs"
        return 0
    fi
    
    # STANDARD LANE: Mixed or moderate changes
    # Default to standard for all other cases
    echo "standard"
    return 0
}

###############################################################################
# Validate lane detection
###############################################################################
validate_lane() {
    local lane="$1"
    
    case "$lane" in
        docs|standard|heavy)
            return 0
            ;;
        *)
            log_error "Invalid lane detected: $lane"
            return 1
            ;;
    esac
}

###############################################################################
# Output detection result
###############################################################################
output_result() {
    local lane="$1"
    local json_format="${2:-false}"
    
    if [[ "$json_format" == "true" ]]; then
        # JSON output format
        cat <<EOF
{
  "lane": "$lane",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "confidence": "high",
  "method": "automatic_detection"
}
EOF
    else
        # Simple text output
        echo "$lane"
    fi
}

###############################################################################
# Main function
###############################################################################
main() {
    log_info "Starting lane detection..."
    
    # Determine base reference
    if ! determine_base_ref; then
        return 1
    fi
    
    # Verify git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository"
        return 1
    fi
    
    # Get changed files
    log_debug "Analyzing changes from $BASE_REF to $HEAD_REF..."
    local changed_files
    if ! changed_files=$(get_changed_files "$BASE_REF" "$HEAD_REF"); then
        return 1
    fi
    
    if [[ -z "$changed_files" ]]; then
        log_warning "No changes detected between $BASE_REF and $HEAD_REF"
        echo "standard"  # Default to standard when no changes
        return 2
    fi
    
    log_debug "Changed files count: $(echo "$changed_files" | wc -l)"
    
    # Categorize files
    log_debug "Categorizing files..."
    local categories
    categories=$(categorize_files "$changed_files")
    
    # Analyze commit messages
    log_debug "Analyzing commit messages..."
    local patterns
    patterns=$(analyze_commit_messages "$BASE_REF" "$HEAD_REF")
    
    # Detect file impact
    log_debug "Detecting file impact..."
    local impact
    impact=$(detect_file_impact "$BASE_REF" "$HEAD_REF")
    
    # Combine all inputs for decision
    local all_data="$categories"$'\n'"$patterns"$'\n'"$impact"
    
    # Decide lane
    local lane
    lane=$(decide_lane <<< "$all_data")
    
    # Validate
    if ! validate_lane "$lane"; then
        return 1
    fi
    
    log_success "Lane detected: $lane"
    
    # Output result
    output_result "$lane" "false"
    
    return 0
}

# Run main function
main "$@"
