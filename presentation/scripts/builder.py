#!/usr/bin/env python3
"""
HTML Presentation Builder - Generate modern styled HTML presentations.

Provides builder classes for different design templates:
- DarkModeTech: Dark theme with vibrant accents
- Glassmorphism: Frosted glass aesthetic
- BoldGradient: Eye-catching gradients
- CorporateModern: Professional with personality
- MinimalistMono: Black, white, one accent
- CreativeChaos: Playful and asymmetric

Usage:
    python builder.py --style dark-mode --output presentation.html
    python builder.py --style glassmorphism --title "Product Launch" --slides title,features,stats
"""

import argparse
from abc import ABC, abstractmethod
from pathlib import Path


class PresentationBuilder(ABC):
    """Base class for presentation builders."""

    def __init__(self, title: str = "Presentation"):
        self.title = title
        self.slides: list[str] = []

    @abstractmethod
    def get_style(self) -> str:
        """Return CSS styles for this template."""
        pass

    @abstractmethod
    def get_body_style(self) -> str:
        """Return body element inline styles."""
        pass

    def add_title_slide(self, title: str, subtitle: str = ""):
        """Add title slide."""
        self.slides.append(self._build_title_slide(title, subtitle))

    def add_content_slide(self, title: str, bullets: list[str]):
        """Add content slide with bullets."""
        self.slides.append(self._build_content_slide(title, bullets))

    def add_stats_slide(self, title: str, stats: list[dict]):
        """Add statistics slide. Stats format: [{"number": "350%", "label": "GROWTH"}, ...]"""
        self.slides.append(self._build_stats_slide(title, stats))

    def add_two_column_slide(self, title: str, left_content: str, right_content: str):
        """Add two-column layout slide."""
        self.slides.append(
            self._build_two_column_slide(title, left_content, right_content)
        )

    @abstractmethod
    def _build_title_slide(self, title: str, subtitle: str) -> str:
        """Build title slide HTML."""
        pass

    @abstractmethod
    def _build_content_slide(self, title: str, bullets: list[str]) -> str:
        """Build content slide HTML."""
        pass

    @abstractmethod
    def _build_stats_slide(self, title: str, stats: list[dict]) -> str:
        """Build stats slide HTML."""
        pass

    @abstractmethod
    def _build_two_column_slide(self, title: str, left: str, right: str) -> str:
        """Build two-column slide HTML."""
        pass

    def build(self) -> str:
        """Build complete HTML presentation with navigation."""
        # Add data-slide attributes and active class to first slide
        slides_with_attrs = []
        for i, slide_html in enumerate(self.slides):
            slide_num = i + 1
            active_class = " active" if i == 0 else ""
            # Insert data-slide and active class into opening div tag
            modified = slide_html.replace(
                '<div class="slide',
                f'<div class="slide{active_class}" data-slide="{slide_num}',
            )
            slides_with_attrs.append(modified)

        navigation_html = f"""
    <div class="nav-dots"></div>
    <div class="slide-counter"><span id="current-slide">1</span> / <span id="total-slides">{len(self.slides)}</span></div>
    
    <div class="clickable-area left" onclick="previousSlide()"></div>
    <div class="clickable-area right" onclick="nextSlide()"></div>

    <script>
        let currentSlide = 1;
        const totalSlides = {len(self.slides)};
        
        // Create navigation dots
        const navDotsContainer = document.querySelector('.nav-dots');
        for (let i = 1; i <= totalSlides; i++) {{
            const dot = document.createElement('div');
            dot.className = 'nav-dot' + (i === 1 ? ' active' : '');
            dot.onclick = () => goToSlide(i);
            navDotsContainer.appendChild(dot);
        }}
        
        function updateSlide() {{
            document.querySelectorAll('.slide').forEach(slide => {{
                slide.classList.remove('active');
            }});
            
            document.querySelectorAll('.nav-dot').forEach((dot, index) => {{
                dot.classList.toggle('active', index + 1 === currentSlide);
            }});
            
            const activeSlide = document.querySelector(`[data-slide="${{currentSlide}}"]`);
            if (activeSlide) {{
                activeSlide.classList.add('active');
            }}
            
            document.getElementById('current-slide').textContent = currentSlide;
        }}
        
        function nextSlide() {{
            if (currentSlide < totalSlides) {{
                currentSlide++;
                updateSlide();
            }}
        }}
        
        function previousSlide() {{
            if (currentSlide > 1) {{
                currentSlide--;
                updateSlide();
            }}
        }}
        
        function goToSlide(slideNumber) {{
            currentSlide = slideNumber;
            updateSlide();
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') {{
                e.preventDefault();
                nextSlide();
            }} else if (e.key === 'ArrowLeft') {{
                e.preventDefault();
                previousSlide();
            }}
        }});
        
        // Swipe support for mobile
        let touchStartX = 0;
        let touchEndX = 0;
        
        document.addEventListener('touchstart', e => {{
            touchStartX = e.changedTouches[0].screenX;
        }});
        
        document.addEventListener('touchend', e => {{
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }});
        
        function handleSwipe() {{
            if (touchEndX < touchStartX - 50) nextSlide();
            if (touchEndX > touchStartX + 50) previousSlide();
        }}
    </script>"""

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{self.title}</title>
<style>
{self.get_style()}
</style>
</head>
<body style="{self.get_body_style()}">
{chr(10).join(slides_with_attrs)}
{navigation_html}
</body>
</html>"""
        return html


class DarkModeTech(PresentationBuilder):
    """Dark mode tech theme with vibrant accents."""

    def get_style(self) -> str:
        return """* { margin: 0; padding: 0; box-sizing: border-box; }

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  min-height: 100vh;
  padding: 80px;
  display: flex;
  flex-direction: column;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}

.slide.active {
  opacity: 1;
  visibility: visible;
  z-index: 1;
}

.nav-dots {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 100;
}

.nav-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-dot.active {
  background: #667eea;
  width: 24px;
  border-radius: 4px;
}

.slide-counter {
  position: fixed;
  bottom: 30px;
  right: 30px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  z-index: 100;
}

.clickable-area {
  position: fixed;
  top: 0;
  width: 50%;
  height: 100%;
  cursor: pointer;
  z-index: 50;
}

.clickable-area.left { left: 0; }
.clickable-area.right { right: 0; }

.slide.title {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  align-items: center;
  justify-content: center;
  text-align: center;
}

.label {
  font-size: 14px;
  color: #f093fb;
  text-transform: uppercase;
  letter-spacing: 4px;
  margin-bottom: 20px;
  font-weight: bold;
}

h1 {
  font-size: 96px;
  color: white;
  font-family: Impact, Arial Black, sans-serif;
  line-height: 1.1;
  text-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

h2 {
  font-size: 56px;
  color: #667eea;
  font-family: Impact, Arial Black, sans-serif;
  margin-bottom: 60px;
  border-bottom: 4px solid #f093fb;
  padding-bottom: 20px;
}

ul {
  list-style: none;
  font-size: 28px;
  line-height: 2;
}

li {
  padding-left: 40px;
  position: relative;
}

li:before {
  content: "▸";
  position: absolute;
  left: 0;
  color: #f093fb;
  font-size: 32px;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  gap: 60px;
  align-items: center;
  flex: 1;
}

.stat {
  text-align: center;
  flex: 1;
}

.stat-number {
  font-size: 96px;
  color: #f093fb;
  font-family: Impact, Arial Black, sans-serif;
  text-shadow: 0 0 20px rgba(240, 147, 251, 0.5);
  line-height: 1;
  margin-bottom: 20px;
}

.stat-label {
  font-size: 24px;
  color: #667eea;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.columns {
  display: flex;
  gap: 60px;
  flex: 1;
}

.column {
  flex: 1;
  background: #1a1f3a;
  padding: 40px;
  border-radius: 16px;
  border: 2px solid #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.column h3 {
  font-size: 32px;
  color: #f093fb;
  margin-bottom: 20px;
  font-family: Impact, Arial Black, sans-serif;
}

.column p {
  font-size: 20px;
  line-height: 1.6;
  color: #e4e7ff;
}"""

    def get_body_style(self) -> str:
        return "background: #0a0e27; font-family: Arial, sans-serif; color: #e4e7ff;"

    def _build_title_slide(self, title: str, subtitle: str) -> str:
        subtitle_html = f'<div class="label">{subtitle}</div>' if subtitle else ""
        return f"""
<div class="slide title">
  {subtitle_html}
  <h1>{title}</h1>
</div>"""

    def _build_content_slide(self, title: str, bullets: list[str]) -> str:
        bullets_html = "\n".join([f"  <li>{bullet}</li>" for bullet in bullets])
        return f"""
<div class="slide">
  <h2>{title}</h2>
  <ul>
{bullets_html}
  </ul>
</div>"""

    def _build_stats_slide(self, title: str, stats: list[dict]) -> str:
        stats_html = "\n".join(
            [
                f'    <div class="stat">\n      <div class="stat-number">{s["number"]}</div>\n      <div class="stat-label">{s["label"]}</div>\n    </div>'
                for s in stats
            ]
        )
        title_html = f"<h2>{title}</h2>" if title else ""
        return f"""
<div class="slide">
  {title_html}
  <div class="stats-grid">
{stats_html}
  </div>
</div>"""

    def _build_two_column_slide(self, title: str, left: str, right: str) -> str:
        return f"""
<div class="slide">
  <h2>{title}</h2>
  <div class="columns">
    <div class="column">
      <h3>Option A</h3>
      <p>{left}</p>
    </div>
    <div class="column">
      <h3>Option B</h3>
      <p>{right}</p>
    </div>
  </div>
</div>"""


class Glassmorphism(PresentationBuilder):
    """Glassmorphism theme with frosted glass effects."""

    def get_style(self) -> str:
        return """* { margin: 0; padding: 0; box-sizing: border-box; }

.slide {
  width: 1280px;
  height: 720px;
  padding: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  page-break-after: always;
}

.glass-card {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 32px;
  padding: 80px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 1000px;
  width: 100%;
}

h1 {
  font-size: 72px;
  color: white;
  font-family: Verdana, sans-serif;
  margin-bottom: 40px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
  text-align: center;
}

h2 {
  font-size: 48px;
  color: white;
  font-family: Verdana, sans-serif;
  margin-bottom: 30px;
}

ul {
  list-style: none;
  font-size: 28px;
  color: white;
  line-height: 2;
}

li {
  padding-left: 40px;
  position: relative;
}

li:before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #ec4899;
  font-size: 28px;
  font-weight: bold;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  gap: 40px;
}

.stat {
  text-align: center;
}

.stat-number {
  font-size: 72px;
  color: white;
  font-family: Verdana, sans-serif;
  font-weight: bold;
  text-shadow: 0 2px 8px rgba(0,0,0,0.2);
  margin-bottom: 10px;
}

.stat-label {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.columns {
  display: flex;
  gap: 40px;
}

.column {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  padding: 30px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.column h3 {
  font-size: 28px;
  color: #ec4899;
  margin-bottom: 15px;
}

.column p {
  font-size: 18px;
  line-height: 1.6;
  color: white;
}"""

    def get_body_style(self) -> str:
        return "font-family: Arial, sans-serif; color: white;"

    def _build_title_slide(self, title: str, subtitle: str) -> str:
        return f"""
<div class="slide">
  <div class="glass-card">
    <h1>{title}</h1>
  </div>
</div>"""

    def _build_content_slide(self, title: str, bullets: list[str]) -> str:
        bullets_html = "\n".join([f"      <li>{bullet}</li>" for bullet in bullets])
        return f"""
<div class="slide">
  <div class="glass-card">
    <h2>{title}</h2>
    <ul>
{bullets_html}
    </ul>
  </div>
</div>"""

    def _build_stats_slide(self, title: str, stats: list[dict]) -> str:
        stats_html = "\n".join(
            [
                f'      <div class="stat">\n        <div class="stat-number">{s["number"]}</div>\n        <div class="stat-label">{s["label"]}</div>\n      </div>'
                for s in stats
            ]
        )
        title_html = f"<h2>{title}</h2>" if title else ""
        return f"""
<div class="slide">
  <div class="glass-card">
    {title_html}
    <div class="stats-grid">
{stats_html}
    </div>
  </div>
</div>"""

    def _build_two_column_slide(self, title: str, left: str, right: str) -> str:
        return f"""
<div class="slide">
  <div class="glass-card">
    <h2>{title}</h2>
    <div class="columns">
      <div class="column">
        <h3>Left</h3>
        <p>{left}</p>
      </div>
      <div class="column">
        <h3>Right</h3>
        <p>{right}</p>
      </div>
    </div>
  </div>
</div>"""


class BoldGradient(PresentationBuilder):
    """Bold gradient theme with high impact."""

    def __init__(self, title: str = "Presentation", gradient: str = "sunset"):
        super().__init__(title)
        self.gradient = gradient

        self.gradients = {
            "sunset": "linear-gradient(45deg, #f093fb 0%, #f5576c 50%, #ffd140 100%)",
            "ocean": "linear-gradient(45deg, #667eea 0%, #764ba2 50%, #f093fb 100%)",
            "forest": "linear-gradient(45deg, #00bf8f 0%, #004d40 50%, #001510 100%)",
        }

    def get_style(self) -> str:
        return """* { margin: 0; padding: 0; box-sizing: border-box; }

.slide {
  width: 1280px;
  height: 720px;
  padding: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  page-break-after: always;
}

h1 {
  font-size: 120px;
  color: white;
  font-family: Impact, Arial Black, sans-serif;
  line-height: 1;
  text-shadow: 0 8px 16px rgba(0,0,0,0.3);
  margin-bottom: 40px;
}

.subtitle {
  font-size: 48px;
  color: white;
  font-weight: bold;
  letter-spacing: 4px;
  text-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.stat-huge {
  font-size: 200px;
  color: white;
  font-family: Impact, Arial Black, sans-serif;
  text-shadow: 0 8px 16px rgba(0,0,0,0.3);
  line-height: 1;
  margin-bottom: 40px;
}

.stat-label {
  font-size: 48px;
  color: white;
  font-weight: bold;
  letter-spacing: 4px;
}

ul {
  list-style: none;
  font-size: 36px;
  color: white;
  line-height: 2;
  text-align: left;
  max-width: 800px;
}

li {
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}"""

    def get_body_style(self) -> str:
        gradient = self.gradients.get(self.gradient, self.gradients["sunset"])
        return f"background: {gradient}; font-family: Arial, sans-serif;"

    def _build_title_slide(self, title: str, subtitle: str) -> str:
        subtitle_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
        return f"""
<div class="slide">
  <div>
    <h1>{title}</h1>
    {subtitle_html}
  </div>
</div>"""

    def _build_content_slide(self, title: str, bullets: list[str]) -> str:
        bullets_html = "\n".join([f"    <li>{bullet}</li>" for bullet in bullets])
        return f"""
<div class="slide">
  <div>
    <h1 style="font-size: 72px; margin-bottom: 60px;">{title}</h1>
    <ul>
{bullets_html}
    </ul>
  </div>
</div>"""

    def _build_stats_slide(self, title: str, stats: list[dict]) -> str:
        # For bold gradient, usually just one big stat per slide
        if stats:
            stat = stats[0]
            return f"""
<div class="slide">
  <div>
    <div class="stat-huge">{stat["number"]}</div>
    <div class="stat-label">{stat["label"]}</div>
  </div>
</div>"""
        return ""

    def _build_two_column_slide(self, title: str, left: str, right: str) -> str:
        return f"""
<div class="slide">
  <div style="max-width: 1000px;">
    <h1 style="font-size: 64px; margin-bottom: 60px;">{title}</h1>
    <div style="display: flex; gap: 80px; text-align: left;">
      <div style="flex: 1; font-size: 28px; color: white; line-height: 1.8;">{left}</div>
      <div style="flex: 1; font-size: 28px; color: white; line-height: 1.8;">{right}</div>
    </div>
  </div>
</div>"""


class CorporateModern(PresentationBuilder):
    """Corporate modern theme - professional with personality."""

    def get_style(self) -> str:
        return """* { margin: 0; padding: 0; box-sizing: border-box; }

.slide {
  width: 1280px;
  height: 720px;
  padding: 80px;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  page-break-after: always;
}

h1 {
  font-size: 72px;
  color: #2563eb;
  font-family: Verdana, sans-serif;
  margin-bottom: 30px;
}

h2 {
  font-size: 48px;
  color: #2563eb;
  font-family: Verdana, sans-serif;
  margin-bottom: 40px;
  border-bottom: 3px solid #f59e0b;
  padding-bottom: 15px;
}

ul {
  list-style: none;
  font-size: 24px;
  color: #0f172a;
  line-height: 2;
}

li {
  padding-left: 30px;
  position: relative;
}

li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #0ea5e9;
  font-size: 28px;
  font-weight: bold;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  gap: 60px;
  flex: 1;
  align-items: center;
}

.stat {
  text-align: center;
}

.stat-number {
  font-size: 72px;
  color: #2563eb;
  font-family: Verdana, sans-serif;
  font-weight: bold;
  margin-bottom: 15px;
}

.stat-label {
  font-size: 18px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 2px;
}"""

    def get_body_style(self) -> str:
        return "font-family: Arial, sans-serif; color: #0f172a;"

    def _build_title_slide(self, title: str, subtitle: str) -> str:
        subtitle_html = (
            f'<p style="font-size: 32px; color: #64748b; margin-top: 20px;">{subtitle}</p>'
            if subtitle
            else ""
        )
        return f"""
<div class="slide" style="justify-content: center; align-items: center; text-align: center;">
  <div>
    <h1>{title}</h1>
    {subtitle_html}
  </div>
</div>"""

    def _build_content_slide(self, title: str, bullets: list[str]) -> str:
        bullets_html = "\n".join([f"    <li>{bullet}</li>" for bullet in bullets])
        return f"""
<div class="slide">
  <h2>{title}</h2>
  <ul>
{bullets_html}
  </ul>
</div>"""

    def _build_stats_slide(self, title: str, stats: list[dict]) -> str:
        stats_html = "\n".join(
            [
                f'    <div class="stat">\n      <div class="stat-number">{s["number"]}</div>\n      <div class="stat-label">{s["label"]}</div>\n    </div>'
                for s in stats
            ]
        )
        title_html = f"<h2>{title}</h2>" if title else ""
        return f"""
<div class="slide">
  {title_html}
  <div class="stats-grid">
{stats_html}
  </div>
</div>"""

    def _build_two_column_slide(self, title: str, left: str, right: str) -> str:
        return f"""
<div class="slide">
  <h2>{title}</h2>
  <div style="display: flex; gap: 60px; flex: 1;">
    <div style="flex: 1; background: #f8fafc; padding: 40px; border-radius: 12px; border: 1px solid #e2e8f0;">
      <p style="font-size: 20px; line-height: 1.6;">{left}</p>
    </div>
    <div style="flex: 1; background: #f8fafc; padding: 40px; border-radius: 12px; border: 1px solid #e2e8f0;">
      <p style="font-size: 20px; line-height: 1.6;">{right}</p>
    </div>
  </div>
</div>"""


BUILDERS = {
    "dark-mode": DarkModeTech,
    "glassmorphism": Glassmorphism,
    "bold-gradient": BoldGradient,
    "corporate": CorporateModern,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate modern styled HTML presentations"
    )
    parser.add_argument(
        "--style",
        required=True,
        choices=list(BUILDERS.keys()),
        help="Presentation style template",
    )
    parser.add_argument("--title", default="Presentation", help="Presentation title")
    parser.add_argument("--output", required=True, help="Output HTML file")
    parser.add_argument(
        "--gradient",
        default="sunset",
        choices=["sunset", "ocean", "forest"],
        help="Gradient variant (for bold-gradient style)",
    )

    args = parser.parse_args()

    # Create builder
    builder_class = BUILDERS[args.style]
    if args.style == "bold-gradient":
        builder = builder_class(args.title, gradient=args.gradient)
    else:
        builder = builder_class(args.title)

    # Example: Add some default slides for demonstration
    # LLM would customize this based on user content
    builder.add_title_slide(args.title, "Generated Presentation")
    builder.add_content_slide(
        "Key Points",
        ["First important point", "Second important point", "Third important point"],
    )
    builder.add_stats_slide(
        "By The Numbers",
        [
            {"number": "100%", "label": "COMPLETE"},
            {"number": "0", "label": "ERRORS"},
            {"number": "∞", "label": "POSSIBILITIES"},
        ],
    )

    # Build and save
    html = builder.build()
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")

    print(f"✓ Created {output_path}")
    print(f"  Style: {args.style}")
    print(f"  Slides: {len(builder.slides)}")
    print("  Open in browser to preview!")


if __name__ == "__main__":
    main()
