import cv2
import numpy as np
from PIL import Image
from transformers import pipeline
import os
import requests
import base64
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class StickerProcessor:
    """
    Sticker Processor Service.
    Handles image generation, background removal, and resizing as separate operations.
    """
    
    def __init__(self, model_name="briaai/RMBG-1.4"):
        print(f"Loading model {model_name}...")
        self.pipe = pipeline("image-segmentation", model=model_name, trust_remote_code=True)
        
        # Initialize API keys from environment
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.banana_api_key = os.getenv("BANANA_API_KEY")
        self.banana_model_key = os.getenv("BANANA_MODEL_KEY")

    def remove_background(self, input_path, output_path, erosion_size=1, island_size=50):
        """
        Removes background and cleans up edges/noise.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        print(f"Removing background: {input_path}")
        image = Image.open(input_path).convert("RGB")
        img_np = np.array(image)
        
        # Background Removal
        result_rgba = self.pipe(image)
        result_np = np.array(result_rgba)
        r, g, b, a = cv2.split(result_np)
        
        # Island Removal (Denoising mask)
        _, thresh = cv2.threshold(a, 10, 255, cv2.THRESH_BINARY)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)
        new_mask = np.zeros_like(a)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] > island_size:
                new_mask[labels == i] = 255
        a_cleaned = cv2.bitwise_and(a, new_mask)
        
        # Erosion (Halo removal)
        if erosion_size > 0:
            kernel = np.ones((erosion_size + 1, erosion_size + 1), np.uint8)
            a_cleaned = cv2.erode(a_cleaned, kernel, iterations=1)
        
        # Smoothing edges
        a_cleaned = cv2.GaussianBlur(a_cleaned, (3, 3), 0)

        # Content Denoising
        clean_rgb = cv2.fastNlMeansDenoisingColored(img_np, None, 5, 5, 7, 21)
        r_c, g_c, b_c = cv2.split(clean_rgb)

        final_rgba = cv2.merge([r_c, g_c, b_c, a_cleaned])
        result_img = Image.fromarray(final_rgba)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        result_img.save(output_path)
        return output_path

    def resize_image(self, input_path, output_path, target_size=(370, 320)):
        """
        Resizes an image (usually a PNG with transparency) to target size,
        maintaining aspect ratio and centering.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        print(f"Resizing image: {input_path} to {target_size}")
        img = Image.open(input_path)
        target_w, target_h = target_size
        
        # High quality resize maintaining aspect ratio
        img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Create canvas
        new_canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        offset = ((target_w - img.width) // 2, (target_h - img.height) // 2)
        new_canvas.paste(img, offset)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        new_canvas.save(output_path)
        return output_path

    def generate_image(self, prompt, output_path):
        """
        Generates an image using Google Gemini Imagen API or Banana.dev API.
        Falls back to test image if API keys are not configured.
        """
        print(f"Generating image for prompt: '{prompt}'")
        
        # Try Gemini Imagen API first
        if self.google_api_key:
            try:
                return self._generate_with_gemini_imagen(prompt, output_path)
            except Exception as e:
                print(f"Gemini Imagen API Error: {e}")
                print("Falling back to Banana API or test image...")
        
        # Try Banana.dev API
        if self.banana_api_key and self.banana_model_key:
            try:
                return self._generate_with_banana(prompt, output_path)
            except Exception as e:
                print(f"Banana API Error: {e}")
                print("Falling back to test image...")
        
        # Fallback to test image
        print("Warning: No API keys configured. Using fallback image.")
        if os.path.exists("data/input/1.jpg"):
            import shutil
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy("data/input/1.jpg", output_path)
            return output_path
        else:
            raise ValueError("No API keys configured and no fallback image (data/input/1.jpg) found.")

    def _generate_with_gemini_imagen(self, prompt, output_path):
        """
        Generate image using Google Gemini Imagen 3 API.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={self.google_api_key}"
        
        payload = {
            "instances": [{
                "prompt": prompt
            }],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1",
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_adult"
            }
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # Extract base64 image from response
            if 'predictions' in result and len(result['predictions']) > 0:
                image_data = result['predictions'][0]['bytesBase64Encoded']
                image_bytes = base64.b64decode(image_data)
                
                # Save image
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"Image generated successfully with Gemini Imagen")
                return output_path
            else:
                raise ValueError("No image data in Gemini response")
        else:
            raise ValueError(f"Gemini API returned status {response.status_code}: {response.text}")
    
    def _generate_with_banana(self, prompt, output_path):
        """
        Generate image using Banana.dev API.
        Implement based on your specific Banana model.
        """
        try:
            import banana_dev as banana
            model_inputs = {"prompt": prompt}
            out = banana.run(self.banana_api_key, self.banana_model_key, model_inputs)
            
            # Extract and save image from banana response
            # This depends on your specific model output format
            if 'modelOutputs' in out and len(out['modelOutputs']) > 0:
                image_data = out['modelOutputs'][0].get('image_base64')
                if image_data:
                    image_bytes = base64.b64decode(image_data)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(image_bytes)
                    return output_path
            
            raise ValueError("No image data in Banana response")
        except ImportError:
            raise ImportError("banana_dev package not installed. Run: pip install banana-dev")

    def has_transparency(self, input_path):
        """
        Checks if an image already has a transparent background.
        """
        img = Image.open(input_path)
        if img.mode == 'RGBA':
            # Check if any pixel has an alpha value < 255
            extrema = img.getextrema()
            if extrema[3][0] < 255:
                return True
        return False

    