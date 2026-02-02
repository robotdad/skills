#!/bin/bash
# Auto-setup wrapper for HTML presentation creation
# Usage: ./create.sh --style <style> --output <file.html> [options]
# Example: ./create.sh --style dark-mode --title "Product Launch" --output presentation.html

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

# Check if venv exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "First-time setup: Creating virtual environment..." >&2
    cd "$SKILL_DIR"
    uv venv
    
    echo "✓ Setup complete!" >&2
    echo "" >&2
fi

# No dependencies needed - builder.py uses only standard library
# Just run with venv Python for consistency

# Run the builder with venv Python
exec "$VENV_DIR/bin/python" "$SKILL_DIR/scripts/builder.py" "$@"
