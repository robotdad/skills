---
name: image-vision
description: "Analyze images using LLM vision APIs (Anthropic Claude, OpenAI GPT-4, Google Gemini, Azure OpenAI). Use when tasks require: (1) Understanding image content, (2) Describing visual elements, (3) Answering questions about images, (4) Comparing images, (5) Extracting text from images (OCR). Provides ready-to-use scripts - no custom code needed for simple cases."
license: MIT
---

# Image Vision Analysis

## Overview

Analyze images using state-of-the-art LLM vision models. **Use the provided scripts** for most tasks - custom code only needed for advanced scenarios.

## Workflow Decision Tree

### First time using this skill?
→ Read [`setup.md`](setup.md) for one-time environment and API key setup

### Simple image analysis (most common)
→ Use "Quick Start" canned scripts below

### Batch processing or multi-turn conversations
→ Read [`patterns.md`](patterns.md) for advanced patterns

### Something failing?
→ Check setup.md for troubleshooting

## Quick Start (Use Canned Scripts)

**Most common case - use the provided scripts directly:**

```bash
# Anthropic Claude (recommended for most tasks)
python examples/anthropic-vision.py <image_path> <prompt>

# OpenAI GPT-4 (good for detailed analysis)
python examples/openai-vision.py <image_path> <prompt>

# Google Gemini (fast, handles large images well)
python examples/gemini-vision.py <image_path> <prompt>

# Azure OpenAI (enterprise deployments)
python examples/azure-vision.py <image_path> <prompt>
```

**Example usage:**

```bash
# Analyze a UI screenshot
python examples/anthropic-vision.py screenshot.png "Describe any UI bugs or issues you see"

# Extract text from an image
python examples/gemini-vision.py document.jpg "Extract all text from this image"

# Describe an image
python examples/openai-vision.py photo.png "Describe this image in detail"
```

## Provider Comparison

| Provider | Model | Best For | Speed | Cost |
|----------|-------|----------|-------|------|
| **Anthropic** | claude-sonnet-4-5 | Latest, balanced quality/speed | Fast | $$ |
| **Anthropic** | claude-3-opus | Highest quality (older) | Slow | $$$ |
| **Anthropic** | claude-3-haiku | Fastest, simple tasks | Very Fast | $ |
| **OpenAI** | gpt-5 | Latest flagship model | Fast | $$$ |
| **OpenAI** | gpt-4.1 | High-volume production | Fast | $$ |
| **Gemini** | gemini-2.5-flash | Latest, excellent balance | Very Fast | $ |
| **Gemini** | gemini-2.5-pro | Large images, best quality | Medium | $$ |
| **Azure** | (deployment-based) | Enterprise, compliance | Varies | Varies |

## Supported Image Formats

- **JPEG/JPG** - Most common
- **PNG** - With transparency
- **GIF** - Static or animated
- **WEBP** - Modern format

**Max sizes:**
- Anthropic: 5MB per image
- OpenAI: 20MB (auto-resizes)
- Gemini: Varies by model (1.5 pro handles very large)

## Common Use Cases

```bash
# UI/UX Analysis
python examples/anthropic-vision.py app-screenshot.png \
  "Analyze this UI for accessibility issues and suggest improvements"

# Bug Identification
python examples/anthropic-vision.py error-state.png \
  "What's wrong with this interface? Describe any visual bugs."

# Content Moderation
python examples/openai-vision.py user-upload.jpg \
  "Does this image contain inappropriate content? Yes or no, and explain."

# Document Understanding
python examples/gemini-vision.py invoice.png \
  "Extract the total amount, date, and vendor name from this invoice"

# Design Review
python examples/anthropic-vision.py mockup.png \
  "Provide design feedback on this mockup. Consider layout, typography, and color."
```

## Output Format

All scripts output to stdout as plain text. The LLM's analysis is printed directly:

```bash
$ python examples/anthropic-vision.py screenshot.png "What's in this image?"

This image shows a web application dashboard with a navigation bar at the top,
a sidebar on the left with menu items, and a main content area displaying...
```

**For structured output**, modify your prompt:

```bash
python examples/openai-vision.py data.png \
  "Extract data as JSON with keys: title, date, amount"
```

## When to Write Custom Scripts

**Use the canned scripts for:**
- ✅ Single image + single prompt analysis
- ✅ Quick one-off tasks
- ✅ Simple Q&A about images

**Write custom scripts when you need:**
- ❌ Batch processing (analyze 100 images)
- ❌ Multi-turn conversations (follow-up questions on same image)
- ❌ Custom output formatting (generate markdown reports)
- ❌ Image preprocessing (resize, crop, filter)
- ❌ Provider fallback logic (try Gemini, then Claude)

→ See [`patterns.md`](patterns.md) for custom script examples

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Write custom script for simple analysis | Use canned scripts |
| Use low-quality compressed images | Use clear, high-res images |
| Ask vague questions | Be specific in prompts |
| Forget to set API keys | Set keys in environment variables |
| Mix up provider-specific model names | Check provider comparison table |

## Quick Reference

| Task | Command |
|------|---------|
| Analyze image (Claude) | `python examples/anthropic-vision.py img.png "prompt"` |
| Analyze image (GPT-4) | `python examples/openai-vision.py img.png "prompt"` |
| Analyze image (Gemini) | `python examples/gemini-vision.py img.png "prompt"` |
| Extract text (OCR) | Any script + "Extract all text from this image" |
| Compare images | See patterns.md for custom script |
| Batch process | See patterns.md for custom script |

## Environment Setup Reminder

**Before first use:**
1. Create venv: `cd image-vision && uv venv`
2. Install SDKs: `uv pip install anthropic openai google-generativeai`
3. Set API keys: Export `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`

→ See [`setup.md`](setup.md) for complete instructions

## See Also

- [`setup.md`](setup.md) — One-time environment setup, API keys, troubleshooting
- [`patterns.md`](patterns.md) — Advanced patterns: batch processing, multi-turn, custom output
