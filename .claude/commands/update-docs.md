# Update Documentation
---
description: Automatically update README.md and CLAUDE.md files based on current codebase
allowed-tools: Read,Write,Glob,Grep,Bash
---

You are tasked with updating the project's documentation files (README.md and CLAUDE.md) to reflect the current state of the codebase.

## Instructions:

1. **Analyze the current codebase structure** by examining:
   - All Python files in src/ directory
   - Test files in tests/ directory
   - Main entry point (main.py)
   - Dependencies (requirements.txt)

2. **Update README.md** to include:
   - Clear project description
   - Installation instructions
   - Usage instructions
   - Current game features and mechanics
   - Development setup information

3. **Update CLAUDE.md** to include:
   - Current code architecture and structure
   - All available commands and their usage
   - Testing information
   - Any new classes, functions, or modules added
   - Updated coding guidelines if needed

4. **Preserve existing important content** while updating outdated information

5. **Ensure consistency** between both documentation files

## Process:

- Read all source files to understand current functionality
- Identify any new features, classes, or modules since last update
- Update documentation to reflect current state
- Maintain the existing tone and structure where appropriate
- Add any missing critical information for developers

$ARGUMENTS