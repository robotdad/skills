---
name: presentation
description: "Transform conversations, content, or ideas into visually striking HTML presentations. Use when tasks require: (1) Creating presentations from conversation history, (2) Building slide decks from notes or content, (3) Designing presentations with modern aesthetics (dark mode, glassmorphism, gradients), (4) Generating presentation narratives from unstructured content. Analyzes content to choose appropriate visual style and structure slides with narrative flow."
license: MIT
---

# Conversation to Presentation Builder

Transform conversations, notes, or content into visually striking HTML presentations with modern design aesthetics.

## Typical User Request Patterns

- "Turn this conversation into a presentation"
- "Create a slide deck from our discussion"
- "Make a presentation about what we just built"
- "Generate slides summarizing this feature"
- "Build a presentation from these notes"

## Workflow: From Conversation to Presentation

### Phase 1: Analyze Content

**Extract from the conversation:**
1. **Main topic/theme** - What is this about?
2. **Key narrative points** - What's the story arc?
3. **Important details** - Stats, comparisons, achievements, problems solved
4. **Tone and audience** - Technical? Business? Creative?

**Example analysis:**
```
Topic: "Feature launch - new caching system"
Key points:
  - Problem: API was slow (2s response time)
  - Solution: Redis caching layer
  - Result: 95% faster (100ms response time)
  - Technical details: LRU eviction, 1hr TTL
Tone: Technical (for engineering team)
Audience: Developers
```

### Phase 2: Choose Visual Style

Match style to topic and tone:

| Content Type | → Style Choice |
|--------------|----------------|
| Tech feature, dev topic | → **dark-mode** (electric blue, neon accents) |
| Design work, creative | → **glassmorphism** (frosted glass, elegant) |
| Bold announcement, launch | → **bold-gradient** (high energy, sunset/ocean) |
| Business results, reports | → **corporate** (professional blue, clean) |

**Decision criteria:**
- **Energy level:** High energy = bold-gradient, Low = corporate/minimalist
- **Formality:** Formal = corporate, Informal = dark-mode/creative
- **Audience:** Developers = dark-mode, Executives = corporate, Designers = glassmorphism

### Phase 3: Structure Slides

**Map content to slide types:**

1. **Title Slide** (always first)
   - Main topic as headline
   - Optional subtitle (date, event, context)

2. **Content Slides** (main narrative)
   - Section headers from key points
   - Bullets for details
   - 3-5 bullets max per slide

3. **Stats Slide** (if you have numbers)
   - Extract metrics: percentages, counts, timelines
   - Format: Big number + label
   - 2-4 stats per slide maximum

4. **Comparison Slides** (if before/after or vs scenarios)
   - Two-column layout
   - Before vs After
   - Old way vs New way

**Example structure from conversation:**
```
Slide 1: Title
  - "Caching Layer Implementation"
  - "Q4 2025 Performance Initiative"

Slide 2: The Problem
  - Slow API response times
  - Poor user experience
  - Scaling challenges

Slide 3: The Solution
  - Redis caching layer
  - LRU eviction strategy
  - 1-hour TTL configuration

Slide 4: The Results (Stats)
  - 95% → FASTER
  - 2s → 100ms → RESPONSE TIME
  - 100% → UPTIME MAINTAINED

Slide 5: Before vs After (Two Column)
  - Left: "2 second load times, frustrated users"
  - Right: "100ms responses, happy users"
```

### Phase 4: Generate HTML Programmatically

**Use the builder classes** - don't write HTML manually:

```python
from scripts.builder import DarkModeTech, BoldGradient, CorporateModern, Glassmorphism

# Choose builder based on your Phase 2 style decision
builder = DarkModeTech("Caching Layer Implementation")

# Add title slide
builder.add_title_slide(
    "CACHING LAYER\nIMPLEMENTATION",
    "Q4 2025 PERFORMANCE INITIATIVE"
)

# Add content slides
builder.add_content_slide("The Problem", [
    "Slow API response times (2s average)",
    "Poor user experience and complaints",
    "Scaling challenges under load"
])

builder.add_content_slide("The Solution", [
    "Redis caching layer with LRU eviction",
    "1-hour TTL for frequently accessed data",
    "Cache warming on deployment",
    "Monitoring and invalidation hooks"
])

# Add stats slide
builder.add_stats_slide("The Results", [
    {"number": "95%", "label": "FASTER"},
    {"number": "100ms", "label": "RESPONSE TIME"},
    {"number": "100%", "label": "UPTIME"}
])

# Add comparison slide
builder.add_two_column_slide(
    "Before vs After",
    "2 second load times, frustrated users, scaling problems",
    "100ms responses, happy users, handles 10x traffic"
)

# Build and save
html = builder.build()
with open('caching-presentation.html', 'w') as f:
    f.write(html)
```

### Phase 5: Save and Optionally Convert

1. Save HTML file with descriptive name
2. Inform user the HTML is ready
3. If user wants PowerPoint, use `html2ppt` skill to convert

## Builder Classes Reference

### Import and Initialize

```python
from scripts.builder import DarkModeTech, Glassmorphism, BoldGradient, CorporateModern

# Choose based on your style decision
builder = DarkModeTech("Presentation Title")
# or
builder = Glassmorphism("Presentation Title")  
# or
builder = BoldGradient("Presentation Title", gradient="sunset")  # sunset/ocean/forest
# or
builder = CorporateModern("Presentation Title")
```

### Available Methods

All builders support:

```python
# Title slide - use for opening slide
builder.add_title_slide(
    title="MAIN HEADLINE\nCAN BE MULTI-LINE",
    subtitle="Optional supporting text or date"
)

# Content slide - use for main narrative sections
builder.add_content_slide(
    title="Section Name",
    bullets=[
        "First key point",
        "Second key point", 
        "Third key point"
    ]
)

# Stats slide - use when you have numbers to showcase
builder.add_stats_slide(
    title="By The Numbers",  # Can be empty string for stats-only
    stats=[
        {"number": "350%", "label": "GROWTH"},
        {"number": "1M+", "label": "USERS"},
        {"number": "99.9%", "label": "UPTIME"}
    ]
)

# Two-column slide - use for comparisons, before/after
builder.add_two_column_slide(
    title="Comparison Title",
    left_content="Before: description of old state",
    right_content="After: description of new state"
)

# Build complete HTML
html = builder.build()
```

## Style Selection Guide

### 🌑 Dark Mode Tech
**Use when:** Tech features, developer topics, SaaS products, API launches, system architecture

**Characteristics:**
- Deep blue/purple backgrounds
- Electric blue and neon pink accents
- Impact font for bold statements
- Glowing effects and gradients
- Modern, energetic feel

**Conversation signals:**
- Technical terminology (API, cache, deployment, performance)
- Developer-focused discussion
- System architecture topics
- Performance metrics and benchmarks

---

### ✨ Glassmorphism
**Use when:** Design topics, creative work, luxury products, elegant solutions

**Characteristics:**
- Frosted glass effects with blur
- Gradient backgrounds
- Soft, sophisticated aesthetic
- Verdana typography
- Apple-style elegance

**Conversation signals:**
- Design-focused discussion
- UI/UX topics
- Creative or artistic content
- Premium/luxury context
- Aesthetic considerations

---

### 🔥 Bold Gradient
**Use when:** Major announcements, big wins, dramatic results, high-energy topics

**Characteristics:**
- Full-bleed eye-catching gradients
- Oversized typography (200px numbers)
- Minimal text, maximum impact
- High contrast, dramatic
- Choose variant: sunset (warm), ocean (cool), forest (natural)

**Conversation signals:**
- Celebration of major achievement
- Dramatic improvements or results
- Product launches or announcements
- High percentage gains (100%+, 10x)
- Exciting news or milestones

---

### 🏢 Corporate Modern
**Use when:** Business results, professional reports, formal presentations

**Characteristics:**
- Clean white backgrounds
- Professional blue color scheme
- Structured layouts
- Verdana/Arial typography
- Business-appropriate aesthetic

**Conversation signals:**
- Quarterly results or metrics
- Business stakeholder audience
- Professional/formal tone
- Charts and data visualization
- Process or methodology topics

## Extracting Stats from Conversations

**Look for quantifiable results:**
- Percentages: "95% faster" → `{"number": "95%", "label": "FASTER"}`
- Improvements: "10x performance" → `{"number": "10x", "label": "PERFORMANCE"}`
- Counts: "1 million users" → `{"number": "1M+", "label": "USERS"}`
- Time metrics: "100ms response" → `{"number": "100ms", "label": "RESPONSE TIME"}`
- Success rates: "99.9% uptime" → `{"number": "99.9%", "label": "UPTIME"}`

**Formatting rules:**
- Keep labels short (1-2 words, all caps)
- Round numbers for impact (99.87% → 99.9%)
- Use suffixes: 1,000,000 → 1M+, 1,000 → 1K+

## Structuring Narrative Flow

**Classic presentation arc:**

1. **Title** - What is this about?
2. **Context/Problem** - Why does this matter? What was the challenge?
3. **Solution/Approach** - What did we do?
4. **Results** - What happened? (Stats slide if you have numbers)
5. **Details** - How did we do it? (Can be multiple slides)
6. **Comparison** - Before vs After (if applicable)
7. **Conclusion/Next Steps** - Where do we go from here?

**Not every presentation needs all sections** - adapt to your content.

## Example: Complete Workflow

**User says:** "Turn our caching discussion into a presentation for the team"

**Your process:**

```python
# 1. ANALYZE CONVERSATION
# Topic: Redis caching implementation
# Key points: Problem (slow API), Solution (Redis), Results (95% faster)
# Tone: Technical
# Audience: Engineering team
# → Choice: DarkModeTech (tech topic, developer audience)

# 2. STRUCTURE SLIDES
# Title: Caching Layer Implementation
# Problem slide: Slow responses
# Solution slide: Redis approach
# Stats slide: Performance improvements
# Details slide: Technical implementation

# 3. IMPORT BUILDER
from scripts.builder import DarkModeTech

# 4. BUILD PRESENTATION
builder = DarkModeTech("Caching Layer Implementation")

builder.add_title_slide(
    "CACHING LAYER\nIMPLEMENTATION",
    "PERFORMANCE INITIATIVE Q4 2025"
)

builder.add_content_slide("The Challenge", [
    "API response times averaging 2 seconds",
    "User complaints about slow interface",
    "Database queries becoming bottleneck",
    "Scaling concerns for growing user base"
])

builder.add_content_slide("Our Solution", [
    "Redis caching layer with LRU eviction",
    "1-hour TTL for frequently accessed data",
    "Cache warming strategy on deployment",
    "Real-time monitoring and alerts"
])

builder.add_stats_slide("The Results", [
    {"number": "95%", "label": "FASTER"},
    {"number": "100ms", "label": "AVG RESPONSE"},
    {"number": "10x", "label": "CAPACITY"},
    {"number": "99.9%", "label": "CACHE HIT RATE"}
])

builder.add_content_slide("Technical Implementation", [
    "Redis cluster with 3 nodes for redundancy",
    "Cache key strategy: resource_type:id",
    "Background invalidation on data updates",
    "Fallback to database on cache miss"
])

builder.add_two_column_slide(
    "Before vs After",
    "2 second API responses\nDatabase overload\nScaling issues\nUser frustration",
    "100ms API responses\nDatabase relief\n10x capacity\nHappy users"
)

# 5. SAVE HTML
html = builder.build()
output_path = 'caching-implementation-presentation.html'
with open(output_path, 'w') as f:
    f.write(html)

print(f"✓ Created {output_path}")
print(f"  Style: Dark Mode Tech")
print(f"  Slides: {len(builder.slides)}")
print(f"  Open in browser to preview, or use html2ppt skill to convert to PowerPoint")
```

## Quick CLI Usage (For Simple Cases)

If user just wants a quick starter template (not from conversation):

```bash
./create.sh --style dark-mode --title "Presentation Title" --output deck.html
```

This generates a basic 3-slide deck that can be manually edited. **But for conversation-to-presentation, use the programmatic approach above.**

## Design Templates Summary

| Style | Colors | Fonts | Best For |
|-------|--------|-------|----------|
| **dark-mode** | Deep blue bg, electric blue/neon pink | Impact + Arial | Tech launches, dev presentations |
| **glassmorphism** | Gradient bg, frosted glass cards | Verdana + Arial | Design portfolios, luxury brands |
| **bold-gradient** | Full-bleed sunset/ocean/forest gradients | Impact + Arial | Product launches, bold announcements |
| **corporate** | White bg, professional blue/amber | Verdana + Arial | Business reports, formal presentations |

## Color Palettes Reference

### Dark Mode Tech
- Background: `#0a0e27`, Surface: `#1a1f3a`
- Primary: `#667eea` (electric blue)
- Accent: `#f093fb` (neon pink)
- Text: `#e4e7ff` (off-white)

### Glassmorphism
- Background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Glass: `rgba(255, 255, 255, 0.2)` + blur
- Primary: `#6366f1` (indigo)
- Accent: `#ec4899` (hot pink)

### Bold Gradient
- **Sunset:** `#f093fb` → `#f5576c` → `#ffd140`
- **Ocean:** `#667eea` → `#764ba2` → `#f093fb`
- **Forest:** `#00bf8f` → `#004d40` → `#001510`

### Corporate Modern
- Background: `#ffffff`, Surface: `#f8fafc`
- Primary: `#2563eb`, Secondary: `#0ea5e9`
- Accent: `#f59e0b`, Text: `#0f172a`

## Content Extraction Tips

### From Technical Discussions

**Look for:**
- Problem statements → "The Challenge" slide
- Solution descriptions → "Our Approach" slide
- Performance metrics → Stats slide
- Architecture details → Technical implementation slide
- Comparisons → Before/After slide

### From Feature Announcements

**Look for:**
- Feature name → Title slide
- Key capabilities → Content slides with bullets
- User benefits → "Why This Matters" slide
- Adoption metrics → Stats slide

### From Project Retrospectives

**Look for:**
- Goals → "Our Mission" slide
- Achievements → Content slides
- Metrics → Stats slide
- Lessons learned → Bullets on final slide

## Typography Hierarchy Guide

```python
# When building slides, use these size guidelines:

# Title slide main headline
h1: 96px-120px (Impact font)

# Section headers  
h2: 56px-72px (Impact font)

# Stats numbers
stats: 96px-200px (Impact font, depending on style)

# Bullets/body text
bullets: 28px-36px (Arial)
body: 20px-28px (Arial)

# Labels/captions
labels: 14px-18px (Arial, uppercase, letter-spacing: 4px)
```

## Anti-Patterns to Avoid

### ❌ Don't
- Write HTML manually - use builder classes
- Put more than 5 bullets on a slide
- Use tiny text (< 20px)
- Mix more than 2 font families
- Fill every pixel - white space is important
- Guess at content - analyze the actual conversation
- Use custom fonts (Roboto, SF Pro, etc.)

### ✓ Do
- Import builder classes and use programmatically
- Keep slides focused (one idea per slide)
- Use large, readable text
- Stick to web-safe fonts (Impact, Verdana, Arial)
- Leave generous spacing and padding
- Extract real content from conversation
- Choose style that matches topic/tone

## After Building

**Tell the user:**
1. Where you saved the HTML file
2. What style you chose and why
3. How many slides were created
4. Suggest opening in browser to preview
5. Offer to convert to PowerPoint using `html2ppt` skill

**Example:**
```
✓ Created presentation: caching-implementation.html

Style: Dark Mode Tech (technical topic, developer audience)
Slides: 5
  1. Title: "CACHING LAYER IMPLEMENTATION"
  2. The Challenge (4 bullets)
  3. Our Solution (4 bullets)
  4. The Results (stats: 95% faster, 100ms response, 10x capacity)
  5. Before vs After (comparison)

Open in browser to preview, or I can convert to PowerPoint using the html2ppt skill.
```

## Converting to PowerPoint

After creating HTML presentation, use the `html2ppt` skill:

```bash
# From html2ppt skill:
./convert.sh caching-implementation.html presentation.pptx
```

The html2ppt skill handles the conversion to .pptx format for easy sharing.

## Quick Reference

| User Request | Your Action |
|--------------|-------------|
| "Turn conversation into presentation" | Analyze → Choose style → Structure slides → Build with classes |
| "Create deck from notes" | Extract key points → Map to slide types → Build HTML |
| "Make presentation about X" | Analyze topic → Choose style → Generate narrative → Build |
| Just want a starter template | Use `./create.sh --style <style>` for basic 3-slide deck |
