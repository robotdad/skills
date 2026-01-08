# MediaWiki API Reference for Image Downloads

Comprehensive guide to downloading images from Wikipedia and Wikimedia Commons using the MediaWiki API.

## Why the API is Required

**CRITICAL**: Wikipedia uses MD5-based directory hashing for image storage. This makes manual URL construction impossible.

### The Problem with Manual URLs

```
❌ WRONG: https://upload.wikimedia.org/wikipedia/commons/f/fe/Image.jpg
✓ RIGHT: Use MediaWiki API to get the actual URL with correct hash directory
```

The actual URL might be:
```
https://upload.wikimedia.org/wikipedia/commons/6/63/Image.jpg
```

Notice the directory `/6/63/` is based on MD5 hash, not the filename. You cannot predict this.

## Core API Function

### Complete Implementation

```python
import urllib.request
import urllib.parse
import json

def get_wikipedia_image_url(filename, site='en.wikipedia.org'):
    """
    Get actual Wikipedia/Commons image URL using MediaWiki API.
    
    Args:
        filename: Image filename with or without 'File:' prefix
                 Examples: "Dawn_of_the_dead.jpg" or "File:Dawn_of_the_dead.jpg"
        site: Target site
              - 'en.wikipedia.org' for Wikipedia (fair use, posters, covers)
              - 'commons.wikimedia.org' for Commons (free-licensed, public domain)
    
    Returns:
        Direct download URL string, or None if image not found
    
    Raises:
        urllib.error.URLError: Network/connection errors
        json.JSONDecodeError: Invalid API response
        KeyError: Unexpected API response structure
    
    Example:
        >>> url = get_wikipedia_image_url("Dawn_of_the_dead.jpg")
        >>> print(url)
        https://upload.wikimedia.org/wikipedia/en/6/63/Dawn_of_the_dead.jpg
        
        >>> url = get_wikipedia_image_url("Golden_Gate_Bridge.jpg", "commons.wikimedia.org")
        >>> print(url)
        https://upload.wikimedia.org/wikipedia/commons/...
    """
    # Remove 'File:' prefix if present
    if filename.startswith('File:'):
        filename = filename[5:]
    
    # Build API request URL
    api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode({
        'action': 'query',
        'titles': f'File:{filename}',
        'prop': 'imageinfo',
        'iiprop': 'url',
        'format': 'json'
    })
    
    # Make request with User-Agent header (required by Wikipedia)
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(api_url, headers=headers)
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        
        # Extract image URL from response
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        
        # Check if image exists (page_id != '-1' means found)
        if page_id != '-1' and 'imageinfo' in pages[page_id]:
            return pages[page_id]['imageinfo'][0]['url']
        
        return None
        
    except urllib.error.URLError as e:
        print(f"Network error: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"API response error: {e}")
        return None
```

## API Parameters Explained

### Basic Parameters (Required)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `action` | `query` | Type of API operation |
| `titles` | `File:filename.jpg` | The file to query (must include `File:` prefix) |
| `prop` | `imageinfo` | Get image information |
| `format` | `json` | Response format |

### Image Info Properties (`iiprop`)

Request additional information about the image:

```python
# Basic - just URL
'iiprop': 'url'

# With size information
'iiprop': 'url|size'

# With metadata
'iiprop': 'url|size|metadata|mime'

# Everything
'iiprop': 'url|size|metadata|mime|timestamp|user|comment'
```

### Advanced: Image Quality Parameters

Get different image sizes/qualities:

```python
def get_wikipedia_image_url_with_size(filename, width=None, height=None, site='en.wikipedia.org'):
    """
    Get Wikipedia image URL with specific dimensions.
    
    Args:
        filename: Image filename
        width: Desired width in pixels (maintains aspect ratio)
        height: Desired height in pixels (maintains aspect ratio)
        site: 'en.wikipedia.org' or 'commons.wikimedia.org'
    
    Returns:
        Thumbnail URL if width/height specified, otherwise full-size URL
    """
    params = {
        'action': 'query',
        'titles': f'File:{filename}',
        'prop': 'imageinfo',
        'iiprop': 'url',
        'format': 'json'
    }
    
    # Add thumbnail parameters if requested
    if width:
        params['iiurlwidth'] = width
    elif height:
        params['iiurlheight'] = height
    
    api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode(params)
    
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(api_url, headers=headers)
    
    data = json.loads(urllib.request.urlopen(req).read())
    pages = data['query']['pages']
    page_id = list(pages.keys())[0]
    
    if page_id != '-1' and 'imageinfo' in pages[page_id]:
        info = pages[page_id]['imageinfo'][0]
        # Return thumbnail URL if available, otherwise full URL
        return info.get('thumburl', info['url'])
    
    return None

# Usage examples
full_size = get_wikipedia_image_url_with_size("Poster.jpg")
thumbnail = get_wikipedia_image_url_with_size("Poster.jpg", width=800)
```

## Wikipedia vs Wikimedia Commons

### en.wikipedia.org

**Use for:**
- Movie posters
- Album covers
- Book covers
- Fair use images
- Non-free content specific to Wikipedia articles

**Example:**
```python
url = get_wikipedia_image_url("Dawn_of_the_dead.jpg", "en.wikipedia.org")
```

**Characteristics:**
- Fair use doctrine applies
- Images tied to specific articles
- May have usage restrictions
- Often higher quality for media posters/covers

### commons.wikimedia.org

**Use for:**
- Free-licensed photographs
- Historical images
- Public domain content
- Creative Commons licensed work
- Photos from Wikipedia articles

**Example:**
```python
url = get_wikipedia_image_url("Golden_Gate_Bridge.jpg", "commons.wikimedia.org")
```

**Characteristics:**
- All freely licensed
- Can be used across all Wikimedia projects
- Generally safe for reuse (check specific license)
- Broader collection of user-uploaded content

## Getting Comprehensive Image Information

```python
def get_image_full_info(filename, site='en.wikipedia.org'):
    """
    Get comprehensive information about an image.
    
    Returns dictionary with:
        - url: Direct download URL
        - size: File size in bytes
        - width: Image width in pixels
        - height: Image height in pixels
        - mime: MIME type (e.g., 'image/jpeg')
        - timestamp: Upload timestamp
    """
    api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode({
        'action': 'query',
        'titles': f'File:{filename}',
        'prop': 'imageinfo',
        'iiprop': 'url|size|dimensions|mime|timestamp',
        'format': 'json'
    })
    
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(api_url, headers=headers)
    
    data = json.loads(urllib.request.urlopen(req).read())
    pages = data['query']['pages']
    page_id = list(pages.keys())[0]
    
    if page_id != '-1' and 'imageinfo' in pages[page_id]:
        info = pages[page_id]['imageinfo'][0]
        return {
            'url': info['url'],
            'size': info['size'],
            'width': info['width'],
            'height': info['height'],
            'mime': info['mime'],
            'timestamp': info['timestamp']
        }
    
    return None

# Usage
info = get_image_full_info("Example.jpg")
print(f"Dimensions: {info['width']}x{info['height']}")
print(f"Size: {info['size']/1024:.1f} KB")
print(f"Type: {info['mime']}")
```

## Batch Processing Pattern

### Efficient Batch Downloads

```python
def batch_download_wikipedia_images(filenames, site='en.wikipedia.org', output_dir='downloads'):
    """
    Download multiple Wikipedia images efficiently.
    
    Args:
        filenames: List of image filenames
        site: Wikipedia site to use
        output_dir: Directory to save images
    
    Returns:
        Dictionary with success/failure counts and details
    """
    import os
    import time
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        'successful': [],
        'failed': [],
        'not_found': []
    }
    
    for idx, filename in enumerate(filenames, 1):
        print(f"[{idx}/{len(filenames)}] Processing: {filename}")
        
        # Get URL via API
        url = get_wikipedia_image_url(filename, site)
        
        if not url:
            print(f"  ✗ Not found")
            results['not_found'].append(filename)
            continue
        
        # Download
        output_path = os.path.join(output_dir, filename)
        try:
            headers = {'User-Agent': 'Research/1.0'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = response.read()
                with open(output_path, 'wb') as f:
                    f.write(data)
            
            print(f"  ✓ Downloaded: {len(data)/1024:.1f} KB")
            results['successful'].append(filename)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['failed'].append((filename, str(e)))
        
        # Be respectful to Wikipedia's servers
        if idx < len(filenames):
            time.sleep(1)
    
    return results
```

## Error Handling Strategies

### Common Errors and Solutions

```python
def robust_get_wikipedia_image_url(filename, site='en.wikipedia.org', max_retries=3):
    """
    Get Wikipedia image URL with robust error handling.
    
    Handles:
        - Network timeouts
        - Connection errors
        - Invalid responses
        - Missing images
    """
    import time
    
    for attempt in range(max_retries):
        try:
            # Remove 'File:' prefix if present
            if filename.startswith('File:'):
                filename = filename[5:]
            
            api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode({
                'action': 'query',
                'titles': f'File:{filename}',
                'prop': 'imageinfo',
                'iiprop': 'url',
                'format': 'json'
            })
            
            headers = {'User-Agent': 'Research/1.0'}
            req = urllib.request.Request(api_url, headers=headers)
            
            # Increased timeout for slow connections
            response = urllib.request.urlopen(req, timeout=15)
            data = json.loads(response.read())
            
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]
            
            if page_id == '-1':
                # Image doesn't exist, no point retrying
                return None, "Image not found"
            
            if 'imageinfo' not in pages[page_id]:
                return None, "No image info available"
            
            return pages[page_id]['imageinfo'][0]['url'], None
            
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt + 1} failed: {e}, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return None, f"Network error after {max_retries} attempts: {e}"
            
        except json.JSONDecodeError as e:
            return None, f"Invalid API response: {e}"
            
        except KeyError as e:
            return None, f"Unexpected API structure: {e}"
            
        except Exception as e:
            return None, f"Unexpected error: {e}"
    
    return None, "Max retries exceeded"

# Usage
url, error = robust_get_wikipedia_image_url("Example.jpg")
if url:
    print(f"Success: {url}")
else:
    print(f"Failed: {error}")
```

## Advanced Patterns

### Finding Images by Category

```python
def get_images_from_category(category, site='commons.wikimedia.org', limit=10):
    """
    Get images from a specific Wikimedia Commons category.
    
    Args:
        category: Category name (e.g., "Golden_Gate_Bridge")
        site: Usually 'commons.wikimedia.org'
        limit: Maximum number of images to return
    
    Returns:
        List of image filenames
    """
    api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode({
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category}',
        'cmtype': 'file',
        'cmlimit': limit,
        'format': 'json'
    })
    
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(api_url, headers=headers)
    
    data = json.loads(urllib.request.urlopen(req).read())
    
    images = []
    for member in data['query']['categorymembers']:
        # Remove 'File:' prefix
        title = member['title']
        if title.startswith('File:'):
            images.append(title[5:])
    
    return images

# Usage
images = get_images_from_category("Golden_Gate_Bridge", limit=5)
for img in images:
    url = get_wikipedia_image_url(img, "commons.wikimedia.org")
    print(f"{img}: {url}")
```

### Search for Images

```python
def search_wikipedia_images(search_term, site='commons.wikimedia.org', limit=10):
    """
    Search for images on Wikipedia/Commons.
    
    Args:
        search_term: What to search for
        site: Target site
        limit: Maximum results
    
    Returns:
        List of (filename, url) tuples
    """
    api_url = f'https://{site}/w/api.php?' + urllib.parse.urlencode({
        'action': 'query',
        'list': 'search',
        'srsearch': f'filetype:bitmap {search_term}',
        'srnamespace': 6,  # File namespace
        'srlimit': limit,
        'format': 'json'
    })
    
    headers = {'User-Agent': 'Research/1.0'}
    req = urllib.request.Request(api_url, headers=headers)
    
    data = json.loads(urllib.request.urlopen(req).read())
    
    results = []
    for item in data['query']['search']:
        title = item['title']
        if title.startswith('File:'):
            filename = title[5:]
            url = get_wikipedia_image_url(filename, site)
            if url:
                results.append((filename, url))
    
    return results

# Usage
results = search_wikipedia_images("zombie movie poster")
for filename, url in results:
    print(f"{filename}")
    print(f"  {url}")
```

## Best Practices

### DO ✓

1. **Always use the API** - Never construct URLs manually
2. **Include User-Agent** - Wikipedia requires it
3. **Handle errors gracefully** - Network issues are common
4. **Add delays** - Be respectful (1 second between requests)
5. **Check for None** - API returns None if image not found
6. **Use timeouts** - Prevent hanging on slow connections

### DON'T ✗

1. **Don't guess URLs** - MD5 hashing makes it impossible
2. **Don't skip the API** - Direct URLs will always fail
3. **Don't hammer the API** - Add delays between requests
4. **Don't ignore errors** - Handle 404s, timeouts, etc.
5. **Don't assume filenames** - Always extract from source page

## Performance Tips

1. **Batch API calls when possible** - But respect rate limits
2. **Cache results** - Store URL mappings to avoid repeated API calls
3. **Use thumbnails for previews** - Add `iiurlwidth` parameter
4. **Parallelize downloads** - But keep API calls sequential
5. **Monitor network usage** - Be respectful of Wikipedia's resources

## Testing Your Implementation

```python
# Test basic functionality
test_cases = [
    ("Dawn_of_the_dead.jpg", "en.wikipedia.org"),
    ("Golden_Gate_Bridge.jpg", "commons.wikimedia.org"),
]

for filename, site in test_cases:
    print(f"Testing: {filename} on {site}")
    url = get_wikipedia_image_url(filename, site)
    if url:
        print(f"  ✓ Success: {url}")
    else:
        print(f"  ✗ Failed to get URL")
```

## Production Script Reference

For production use, see the complete implementation:
- `../scripts/download_wikipedia_images.py` - Full-featured batch downloader with CLI
