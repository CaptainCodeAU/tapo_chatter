# Cursor Rules for Tapo Chatter Project

This directory contains Cursor rules to help maintain code quality and automate common tasks for the Tapo Chatter project.

## Available Rules

### 1. Test Coverage Check (`check_coverage.mdc`)

-   **Purpose**: Ensures test coverage stays above 95% after code changes
-   **Triggers**: After saving files in `src/tapo_chatter/`
-   **Action**: Runs `python tests/check_coverage.py` and reports if coverage drops below 95%

### 2. Code Formatting (`format_code.mdc`)

-   **Purpose**: Automatically formats Python code using ruff
-   **Triggers**: After saving any Python file
-   **Action**: Runs `ruff format` on the saved file

### 3. Code Linting (`lint_code.mdc`)

-   **Purpose**: Lints Python code using ruff and reports issues
-   **Triggers**: After saving any Python file
-   **Action**: Runs `ruff check` on the saved file and reports linting issues

### 4. Run Tests (`run_tests.mdc`)

-   **Purpose**: Runs pytest when test files are modified
-   **Triggers**: After saving files in `tests/`
-   **Action**: Runs `pytest` on the modified test file

### 5. Environment Variable Check (`check_env_vars.mdc`)

-   **Purpose**: Reminds to set required environment variables
-   **Triggers**: Before running `main.py`
-   **Action**: Shows a prompt reminding about required environment variables

### 6. Docstring Reminder (`docstring_reminder.mdc`)

-   **Purpose**: Suggests adding docstrings to undocumented functions or classes
-   **Triggers**: After editing files in `src/tapo_chatter/`
-   **Action**: Checks for missing docstrings and suggests adding them

### 7. Dependency Check (`dependency_check.mdc`)

-   **Purpose**: Verifies that all required dependencies are installed
-   **Triggers**: Before running any Python file
-   **Action**: Checks for key dependencies and warns if any are missing

## Usage

Cursor will automatically apply these rules based on the triggers defined in each rule. No manual action is required.

## Customization

You can modify these rules or add new ones by editing the .mdc files in this directory. See [Cursor Rules Documentation](https://cursor.sh/docs/rules) for more details.
