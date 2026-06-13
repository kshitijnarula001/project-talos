import ollama
import base64
import os

def analyze_image(image_path, question=None):
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        prompt = question if question else """
        Analyze this image and tell me:
        1. What you see in detail
        2. Any text visible in the image
        3. Key observations or insights
        4. Anything notable or interesting
        """

        response = ollama.chat(
            model="llava",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_data]
                }
            ]
        )
        return response["message"]["content"]

    except Exception as e:
        return f"Could not analyze image: {e}"