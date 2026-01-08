---
name: image-search
description: Find and download images from Wikipedia, Archive.org, and the web using search-first, never-guess approach. Use when users need images for presentations, documents, websites, or any visual content. Specializes in reliable sources with proven download methods, MediaWiki API expertise for Wikipedia images, and batch download support with progress reporting.
---

# Image Search

Find and download images from Wikipedia, Archive.org, and web sources using proven techniques.

## When to Use This Skill

Use when users request images for:
- Presentations and slide decks
- Documents and reports
- Website and app designs
- Research and reference material
- Any visual content needs

## Core Workflow

The skill follows a **search-first, never-guess** approach:

1. **Search** for the topic using web_search
2. **Find** Wikipedia or Archive.org pages in results
3. **Extract** actual image URLs/filenames from those pages
4. **Download** using proper APIs or direct URLs
5. **Never guess** filenames or construct URLs manually

## Primary Sources (Preferred)

### Wikipedia Images via MediaWiki API

**CRITICAL**: Wikipedia requires MediaWiki API - never construct URLs manually.

Wikipedia uses MD5-based directory hashing, making manual URL construction impossible:
```
❌ WRONG: https://upload.wikimedia.org/wikipedia/commons/f/fe/Image.jpg
✓ RIGHT: Use API to get actual URL with correct hash directory
```

#### Quick Pattern

**Step 1: Search and find Wikipedia page**
```python
results = web_search("Dawn of the Dead 1978 film")
# Look for wikipedia.org URLs in results
```

**Step 2: Extract actual filename from Wikipedia page**
```bash
curl -s "https://en.wikipedia.org/wiki/Dawn_of_the_Dead_(1978_film)" | \
  grep -o 'File:[^"]*\.jpg' | head -1
# Output: File:Dawn_of_the_dead.jpg
```

**Step 3: Use MediaWiki API to get actual image URL**

```python
import urllib.request, urllib.parse, json

def get_wikipedia_image_url(filename, site='en.wikipedia.org'):
    """Get actual Wikipedia/Commons image URL using MediaWiki API"""
    api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode({
        'action': 'query',
        'titles': f'File:{filename}',
        'prop': 'imageinfo',
        'iiprop': 'url',
        'format': 'json'
    })
    
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(api_url, headers=headers)
    
    data = json.loads(urllib.request.urlopen(req).read())
    pages = data['query']['pages']
    page_id = list(pages.keys())[0]
    
    if page_id != '-1' and 'imageinfo' in pages[page_id]:
        return pages[page_id]['imageinfo'][0]['url']
    
    return None

# Usage
url = get_wikipedia_image_url("Dawn_of_the_dead.jpg")
# Returns: https://upload.wikimedia.org/wikipedia/en/6/63/Dawn_of_the_dead.jpg
```

**Step 4: Download the image**
```python
def download_image(url, output_filename):
    """Download image with proper headers"""
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        data = response.read()
        with open(output_filename, 'wb') as f:
            f.write(data)
    
    print(f"✓ Downloaded: {len(data)/1024:.1f} KB")
```

#### Wikipedia vs Commons

**en.wikipedia.org:**
- Movie posters, album covers, book covers, fair use images
- Use: `get_wikipedia_image_url("file.jpg", "en.wikipedia.org")`

**commons.wikimedia.org:**
- Free-licensed photos, historical images, public domain
- Use: `get_wikipedia_image_url("file.jpg", "commons.wikimedia.org")`

#### Detailed Documentation

**→ For complete API details, advanced patterns, error handling, and batch processing:**
See [MediaWiki API Reference](references/mediawiki-api.md)

#### Production Scripts

**Batch download images** (✅ zero dependencies - runs immediately):
```bash
# Download specific files
python scripts/download_wikipedia_images.py --filenames poster1.jpg poster2.jpg

# Download from list file
python scripts/download_wikipedia_images.py --from-list filenames.txt

# Download from Commons
python scripts/download_wikipedia_images.py --site commons.wikimedia.org --filenames Image.jpg
```

**Verify image quality** (⚠️ requires Pillow: `pip install Pillow`):
```bash
# Check downloaded images
python scripts/check_image_quality.py --dir ./downloaded-images

# Check specific files with minimum dimensions
python scripts/check_image_quality.py --files *.jpg --min-width 800 --min-height 600
```

**Dependencies Summary:**
- `download_wikipedia_images.py`: Uses only standard library (urllib, json, argparse) - ready to use immediately
- `check_image_quality.py`: Requires Pillow (`pip install Pillow`) - script provides clear error if missing

### Archive.org Direct Downloads

Archive.org is excellent for public domain content with straightforward URLs.

#### Pattern for Archive.org

```
https://archive.org/download/[COLLECTION_NAME]/[FILE_NAME]
```

#### Finding Archive.org Images

**Step 1: Search for collection**
```python
results = web_search("archive.org zombie movie posters")
# Look for archive.org/details/[COLLECTION_NAME] URLs
```

**Step 2: Download directly**
```python
# Direct download URLs work without authentication
url = "https://archive.org/download/night-of-the-living-dead_1968/night-of-the-living-dead-1968.jpg"

download_image(url, "night-of-the-living-dead-1968.jpg")
```

**Alternative: Use internetarchive library**
```python
import internetarchive as ia

# Search for items
results = ia.search_items('zombie horror movie posters')

for result in results:
    print(f"Collection: {result['identifier']}")
    
    # Get item and download
    item = ia.get_item(result['identifier'])
    item.download()
```

## Secondary Sources (Web Search)

When Wikipedia/Archive.org don't have the image, use web search.

### Finding Images from Web Search

**Step 1: Search with specific terms**
```python
results = web_search("golden retriever puppy high quality photo")
```

**Step 2: Extract image URLs from results**

Look for:
- Direct image URLs (.jpg, .png, .webp in the URL)
- Image-heavy sites (Pinterest, Flickr, museum sites)
- Specific image pages

**Step 3: Fetch page and extract images**
```python
import requests
from bs4 import BeautifulSoup

def find_images_on_page(url):
    """Extract all image URLs from a webpage"""
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    
    images = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if src:
            # Convert relative URLs to absolute
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                from urllib.parse import urljoin
                src = urljoin(url, src)
            images.append(src)
    
    return images

# Usage
images = find_images_on_page("https://example.com/article")
for img_url in images:
    print(img_url)
```

## Handling Download Issues

Many websites block direct image downloads. Here are proven techniques:

### Technique 1: User-Agent Header

Always include a User-Agent header:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
response = requests.get(image_url, headers=headers)
```

### Technique 2: Referer Header

Some sites check where the request came from:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Referer': 'https://example.com/page'  # The page where you found the image
}
response = requests.get(image_url, headers=headers)
```

### Technique 3: Timeout and Retries

Add timeouts and retry logic:
```python
import time

def download_with_retry(url, output_file, max_retries=3):
    """Download with retry logic"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded: {len(response.content)/1024:.1f} KB")
            return True
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
    
    return False
```

### Technique 4: Handle Redirects

Some sites redirect to CDN URLs:
```python
response = requests.get(url, headers=headers, allow_redirects=True)
final_url = response.url  # The actual image URL after redirects
```

## Script Organization

When generating helper scripts, **always create them in a dedicated subfolder** to keep the workspace organized.

### Creating the Scripts Folder

```python
import os

# Create image-search-scripts subfolder
scripts_dir = "image-search-scripts"
os.makedirs(scripts_dir, exist_ok=True)

# Write helper scripts there
script_path = os.path.join(scripts_dir, "download_images.py")
```

### Script Template Structure

When creating helper scripts, follow this pattern:

```python
#!/usr/bin/env python3
"""
[Script Purpose]

Generated by: image-search skill
Date: [current date]
Purpose: [what this script does]

Usage:
    python [script_name] [arguments]
"""

# Standard library imports only (no external dependencies if possible)
import urllib.request
import json
import os

# Your functions here
def main():
    # Main script logic
    pass

if __name__ == "__main__":
    main()
```

**Key points:**
- Clear header explaining the script's origin
- Usage instructions
- Prefer standard library over external dependencies
- Make scripts self-contained and readable

## Best Practices Summary

### ✓ DO

1. **Search first**: Use web_search to find Wikipedia/Archive.org pages
2. **Extract actual filenames**: Parse the source page to get exact filename
3. **Use APIs**: MediaWiki API for Wikipedia, direct URLs for Archive.org
4. **Add headers**: Always include User-Agent, add Referer if needed
5. **Organize scripts**: Put generated scripts in `image-search-scripts/` folder
6. **Test downloads**: Verify images downloaded correctly before proceeding
7. **Be respectful**: Add small delays between downloads

### ✗ DON'T

1. **Don't guess URLs**: Never construct Wikipedia URLs manually
2. **Don't guess filenames**: Always extract from source page
3. **Don't skip API**: MediaWiki API is required for Wikipedia
4. **Don't ignore errors**: Handle 403/404 errors gracefully
5. **Don't clutter workspace**: Always use subfolder for helper scripts

## Workflow Examples

### Example 1: Finding a Specific Movie Poster

```
User: "Get me the Night of the Living Dead movie poster"

Step 1: Search for Wikipedia page
→ web_search("Night of the Living Dead 1968 film wikipedia")
→ Find: https://en.wikipedia.org/wiki/Night_of_the_Living_Dead

Step 2: Extract image filename from page
→ curl and grep to find: "File:Night_of_the_Living_Dead_poster.jpg"

Step 3: Use MediaWiki API to get URL
→ get_wikipedia_image_url("Night_of_the_Living_Dead_poster.jpg")
→ Returns actual URL with correct MD5 directory

Step 4: Download
→ download_image(url, "night-of-the-living-dead-1968.jpg")
→ ✓ Success
```

### Example 2: Finding Historical Images from Archive.org

```
User: "Find vintage zombie movie posters from the 1940s"

Step 1: Search Archive.org
→ web_search("archive.org 1940s zombie movie posters")
→ Find collection: archive.org/details/Horror-Movie-Posters

Step 2: Browse collection
→ Visit the collection page
→ Extract file list

Step 3: Download directly
→ https://archive.org/download/Horror-Movie-Posters/king-of-zombies-1941.jpg
→ No API needed, direct download works
→ ✓ Success
```

### Example 3: Batch Download with Script Generation

```
User: "Download posters for 10 classic horror films"

Step 1: Search Wikipedia for each film
Step 2: Extract all filenames into a list
Step 3: Generate helper script in image-search-scripts/
Step 4: Run the script to download all posters
Step 5: Report results with file sizes
```

## Dependencies

Standard library preferred. Optional external libraries:

```bash
# For web scraping (if needed)
pip install requests beautifulsoup4 lxml

# For Archive.org (optional)
pip install internetarchive

# For image quality checking
pip install Pillow
```

Most tasks work with just standard library (urllib, json).

## Additional Resources

- **[MediaWiki API Reference](references/mediawiki-api.md)** - Complete API documentation, advanced patterns, error handling
- **[download_wikipedia_images.py](scripts/download_wikipedia_images.py)** - Production-ready batch download script
- **[check_image_quality.py](scripts/check_image_quality.py)** - Image verification and quality checking utility

## Keywords

image search, wikipedia images, archive.org, download images, movie posters, mediawiki api, web images, photo download, image scraping, public domain images
