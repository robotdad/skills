#!/usr/bin/env python3
"""Analyze images using OpenAI GPT-4 vision models.

Usage:
    python openai-vision.py <image_path> <prompt>

Example:
    python openai-vision.py screenshot.png "Describe this UI"
    python openai-vision.py photo.jpg "What's in this image?"

Requires:
    - openai SDK: pip install openai
    - OPENAI_API_KEY environment variable
"""

import openai
import base64
import sys
import os


def analyze_image(image_path: str, prompt: str) -> str:
    """Analyze an image using GPT-4's vision capabilities.
    
    Args:
        image_path: Path to image file (JPEG, PNG, GIF, WEBP)
        prompt: Question or instruction about the image
        
    Returns:
        GPT-4's text analysis of the image
    """
    # Initialize client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Read and encode image
    try:
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Image not found: {image_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to read image: {e}")
    
    # Detect media type from extension
    ext = image_path.lower().split('.')[-1]
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp"
    }
    media_type = media_types.get(ext, "image/jpeg")
    
    # Call GPT-5 with vision
    try:
        response = client.chat.completions.create(
            model="gpt-5",  # Latest flagship model (2025)
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}"
                        }
                    }
                ]
            }],
            max_completion_tokens=1024  # GPT-5 uses max_completion_tokens
        )
        
        return response.choices[0].message.content
    
    except openai.APIError as e:
        raise RuntimeError(f"API error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python openai-vision.py <image_path> <prompt>")
        print()
        print("Example:")
        print('  python openai-vision.py screenshot.png "Describe this UI"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = " ".join(sys.argv[2:])  # Join remaining args as prompt
    
    try:
        result = analyze_image(image_path, prompt)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
