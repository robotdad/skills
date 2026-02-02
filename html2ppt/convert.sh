#!/bin/bash
# Auto-setup wrapper for HTML to PowerPoint conversion
# Usage: ./convert.sh <input.html> <output.pptx> [--primary-color HEX] [--accent-color HEX]
# Example: ./convert.sh deck.html presentation.pptx --primary-color 667eea

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

# Validate arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: convert.sh <input.html> <output.pptx> [options]" >&2
    echo "" >&2
    echo "Options:" >&2
    echo "  --primary-color HEX   Primary color for Amplifier Stories elements (no # prefix)" >&2
    echo "  --accent-color HEX    Accent color for highlights and stats (no # prefix)" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  ./convert.sh deck.html output.pptx" >&2
    echo "  ./convert.sh deck.html branded.pptx --primary-color 0066cc --accent-color ff6600" >&2
    exit 1
fi

# Check if venv exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "First-time setup: Creating virtual environment..." >&2
    cd "$SKILL_DIR"
    uv venv
    
    echo "Installing dependencies (python-pptx, beautifulsoup4, lxml)..." >&2
    uv pip install python-pptx beautifulsoup4 lxml --quiet
    
    echo "✓ Setup complete!" >&2
    echo "" >&2
fi

# Verify dependencies are installed
if ! "$VENV_DIR/bin/python" -c "import pptx" 2>/dev/null; then
    echo "Installing python-pptx..." >&2
    cd "$SKILL_DIR" && uv pip install python-pptx --quiet
fi

if ! "$VENV_DIR/bin/python" -c "import bs4" 2>/dev/null; then
    echo "Installing beautifulsoup4..." >&2
    cd "$SKILL_DIR" && uv pip install beautifulsoup4 lxml --quiet
fi

# Run the converter with venv Python
exec "$VENV_DIR/bin/python" "$SKILL_DIR/scripts/convert.py" "$@"
