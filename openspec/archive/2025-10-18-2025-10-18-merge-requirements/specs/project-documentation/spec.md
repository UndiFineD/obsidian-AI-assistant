# Delta: Requirements File Merge

## ADDED Requirements

### Requirement: Merge all requirements files into one
The project SHALL merge requirements.txt, requirements-dev.txt, and requirements-ml.txt into a single requirements.txt file.

#### Scenario: Successful merge
- **WHEN** the merge script is run
- **THEN** all packages from the three files are present in the new requirements.txt

### Requirement: Deduplicate and categorize packages
The project SHALL deduplicate all package entries and organize them by category with clear comments.

#### Scenario: Deduplication and categorization
- **WHEN** the merged requirements.txt is generated
- **THEN** no duplicate packages exist, all version pins are preserved, and packages are grouped by category

### Requirement: Remove obsolete requirements files
The project SHALL remove requirements-dev.txt and requirements-ml.txt after merging.

#### Scenario: Obsolete file removal
- **WHEN** the merge is complete
- **THEN** requirements-dev.txt and requirements-ml.txt no longer exist in the repository
