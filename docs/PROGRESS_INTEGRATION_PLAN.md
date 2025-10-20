# Progress Indicator Integration Plan

## Steps Completed
- ✅ Step 0: Spinner for "Creating todo.md from template"
- ✅ Step 2: Spinner for "Creating proposal.md" + "Validating proposal.md"
- ✅ Step 6: StatusTracker for test.py and implement.py generation
- ✅ Step 10: Spinner for issue fetching + ProgressBar for syncing

## Steps Remaining (9 steps)

### Step 1: Version Bump
**Operations**: Read version, increment, write back
**Progress**: Spinner "Updating version file"

### Step 3: Capability Spec  
**Operations**: Generate spec.md with multiple sections
**Progress**: StatusTracker for sections (Overview, Requirements, Implementation, Testing)

### Step 4: Task Breakdown
**Operations**: Extract tasks from documents
**Progress**: Spinner "Analyzing documents" + ProgressBar for task extraction

### Step 5: Implementation Checklist
**Operations**: Generate checklist.md
**Progress**: Spinner "Generating implementation checklist"

### Step 7: Document Review
**Operations**: Iterate through multiple documents
**Progress**: ProgressBar showing "Reviewing X of N documents"

### Step 8: Test Execution
**Operations**: Run test scripts
**Progress**: Spinner "Executing tests"

### Step 9: Review Changes
**Operations**: Validate all documents
**Progress**: StatusTracker for each document (proposal, spec, tasks, tests, checklist)

### Step 11: Commit Changes
**Operations**: Git add/commit
**Progress**: Spinner "Committing changes to git"

### Step 12: Cross-Validation
**Operations**: 5-way validation check
**Progress**: StatusTracker for 5 validation stages

## Implementation Strategy

For each step:
1. Add progress import at top of file
2. Identify main operations in invoke_stepN() function
3. Wrap with appropriate indicator:
   - **Spinner**: Single indeterminate operation
   - **ProgressBar**: Loop with known count
   - **StatusTracker**: Multiple concurrent/sequential operations

4. Preserve existing error handling
5. Add graceful fallback if progress module unavailable

## Estimated Time
- ~10 minutes per step
- ~90 minutes total for 9 steps
- Can be done in batches of 3 steps

## Priority Order
1. High-value: Steps 3, 4, 9, 12 (complex operations, clear progress)
2. Medium-value: Steps 1, 5, 7, 8 (simpler operations)
3. Low-value: Step 11 (very quick operation)

