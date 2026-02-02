---
name: html2ppt
description: "Convert HTML presentations to PowerPoint (.pptx) format. Use when tasks require: (1) Converting Amplifier Stories HTML decks to PowerPoint, (2) Converting custom HTML presentations to PPTX, (3) Generating shareable PowerPoint files from web-based slides. Works with any HTML presentation - handles Amplifier Stories format automatically and supports custom HTML from the 'presentation' skill."
license: MIT
---

# HTML to PowerPoint Converter

Convert HTML presentations to PowerPoint format using python-pptx. Works with Amplifier Stories HTML and custom HTML presentations.

## When to Use This Skill

- Converting Amplifier Stories HTML decks to PowerPoint
- Converting custom HTML presentations (created with `presentation` skill or manually)
- Generating shareable .pptx files from any HTML slide deck

## Quick Start

**ALWAYS use the wrapper script** - it handles venv setup automatically:

```bash
# Convert any HTML presentation to PowerPoint
./convert.sh <input.html> <output.pptx>

# With custom brand colors (Amplifier Stories format only)
./convert.sh input.html output.pptx --primary-color 667eea --accent-color f093fb
```

The wrapper script automatically:
- Creates venv if it doesn't exist
- Installs required libraries (python-pptx, beautifulsoup4, lxml)
- Uses venv Python (no manual activation needed)
- Handles errors gracefully

## What Gets Converted

### Amplifier Stories Format (Auto-detected)

The converter recognizes Amplifier Stories HTML structure and handles:

**Slide elements:**
- `.slide` divs → PowerPoint slides
- `.section-label` → Uppercase blue labels
- `h1`, `.headline` → Large headlines (56pt for h1, 40pt for h2)
- `.subhead` → Gray subtitles (24pt)
- `.big-text` → Cyan gradient effect (accent color)

**Content components:**
- `.card` elements → Rounded rectangle cards with title/text
- `.stat-grid` → Statistics with large numbers + labels
- `.tenet` → Accent-bordered info boxes
- `.highlight-box` → Callout boxes
- Tables (`.data-table`) → Formatted tables
- `.feature-list` → Bullet lists

**Layout:**
- `.center` class → Centered alignment
- `.thirds`, `.halves`, `.fourths` → Card grids

### Custom HTML (Generic parser)

For non-Amplifier HTML, the converter extracts:
- Text from `<h1>` through `<h6>`, `<p>` tags
- Lists from `<ul>`, `<ol>` elements
- Basic structure and hierarchy
- Colors from inline styles

**Note:** Custom HTML gets basic conversion. For best results with custom presentations, structure them similarly to Amplifier Stories format.

## Color Customization

Override default Amplifier colors:

```bash
# Use your brand colors
./convert.sh deck.html output.pptx --primary-color 2563eb --accent-color f59e0b

# Colors are hex without # prefix
# Primary: Used for section labels, card titles, table headers
# Accent: Used for big numbers, highlighted text
```

## Usage Examples

### Convert Amplifier Stories Deck

```bash
# Basic conversion
./convert.sh amplifier-story-deck.html presentation.pptx

# With custom colors matching your brand
./convert.sh amplifier-story-deck.html branded.pptx \
  --primary-color 0066cc \
  --accent-color ff6600
```

### Convert Custom HTML Presentation

```bash
# From presentation skill or custom HTML
./convert.sh my-dark-mode-deck.html output.pptx

# Colors apply if HTML has Amplifier structure classes
./convert.sh custom-deck.html output.pptx --primary-color 667eea
```

### Batch Conversion

```bash
# Convert multiple presentations
for html in *.html; do
  ./convert.sh "$html" "${html%.html}.pptx"
done
```

## Output Format

- **Slide size:** 10" × 5.625" (16:9 aspect ratio)
- **Background:** Black (default) or from HTML structure
- **Fonts:** Matches HTML where possible, falls back to Arial
- **Colors:** Uses provided overrides or Amplifier defaults

## Troubleshooting

### First-time Setup Issues

The script automatically creates the venv and installs dependencies on first use. If you see errors:

```bash
# Check uv is installed
which uv

# Manually create venv if needed
cd ~/.amplifier/skills/html2ppt
uv venv
uv pip install python-pptx beautifulsoup4 lxml
```

### Common Errors

**"No module named 'pptx'"**
- The venv wasn't created properly
- Solution: Delete `.venv` folder and run script again

**"Input file not found"**
- Check the file path is correct
- Use absolute paths or verify you're in the right directory

**"Invalid color format"**
- Colors should be hex without # prefix
- Wrong: `--primary-color #667eea`
- Right: `--primary-color 667eea`

## Advanced: Direct Script Usage

If you need to call the Python script directly (not recommended - use wrapper):

```bash
# ✓ Correct - uses venv Python
./.venv/bin/python scripts/convert.py input.html output.pptx

# ✗ Wrong - uses system Python, will fail
python scripts/convert.py input.html output.pptx
```

## Library Details

**Why python-pptx over pptxgenjs:**

| Aspect | python-pptx (Our choice) | pptxgenjs (Anthropic's) |
|--------|-------------------------|------------------------|
| API clarity | Clear, well-documented | Confusing margin arrays |
| Positioning | Accurate with Inches() | 2% width adjustment hacks |
| Browser needed | No (direct HTML parsing) | Yes (Playwright overhead) |
| Validation | Reasonable | Aggressive (0.5" bottom margin) |
| Maturity | Very stable | Good but quirky |

## Dependencies

Installed automatically by wrapper script:
- **python-pptx** - PowerPoint generation
- **beautifulsoup4** - HTML parsing
- **lxml** - XML processing

## Companion Skills

- **presentation** - Create modern styled HTML presentations before converting

## Quick Reference

| Task | Command |
|------|---------|
| Convert HTML | `./convert.sh input.html output.pptx` |
| Custom colors | `./convert.sh in.html out.pptx --primary-color HEX --accent-color HEX` |
| Verify setup | `./convert.sh --help` |
