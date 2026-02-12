from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from app.services.processor import StickerProcessor
import os
import json

# --- Input Schemas ---

class RemoveBackgroundInput(BaseModel):
    input_path: str = Field(description="The full path or filename of the image to process.")
    output_path: Optional[str] = Field(default=None, description="The path where the background-removed image should be saved. If not provided, it will save to data/output/nobg_[input_filename].png")
    erosion_size: int = Field(default=1, description="Size for edge erosion to remove halos. 0-3 is typical.")
    island_size: int = Field(default=100, description="Minimum area for a connected component to be kept. Helps remove noise/specks.")

class ResizeImageInput(BaseModel):
    input_path: str = Field(description="The full path or filename of the image to resize.")
    output_path: Optional[str] = Field(default=None, description="The path where the resized image should be saved.")
    target_width: int = Field(default=370, description="Target width in pixels.")
    target_height: int = Field(default=320, description="Target height in pixels.")

class GenerateImageInput(BaseModel):
    prompt: str = Field(description="The text prompt to generate an image from.")
    output_filename: str = Field(description="The filename to save the generated image as (e.g., 'generated_char.jpg').")

class CheckBackgroundInput(BaseModel):
    input_path: str = Field(description="The path to the image to check for background/transparency.")

class ImageToImageInput(BaseModel):
    prompt: str = Field(description="The text prompt to style the base image.")
    base_image_path: str = Field(description="The path or filename of the local base image to use.")
    output_filename: str = Field(description="The filename to save the stylized image as.")

# --- Processor Singleton ---

_processor = None

def get_processor():
    global _processor
    if _processor is None:
        _processor = StickerProcessor()
    return _processor

# --- Tool Definitions ---

@tool("generate_image", args_schema=GenerateImageInput, return_direct=False)
def generate_image_tool(prompt: str, output_filename: str) -> str:
    """
    Generates an image from a text prompt using Google Gemini Imagen 4 API.
    
    Use this tool FIRST when creating a sticker to generate the base image.
    The prompt should describe the visual appearance of the sticker character or object.
    
    Args:
        prompt: Detailed description of the image to generate
        output_filename: Name for the saved file (e.g., 'cat_sticker.jpg')
    
    Returns:
        Success message with file path or error message
    """
    output_path = os.path.join("data", "input", output_filename)
    processor = get_processor()
    try:
        final_path = processor.generate_image(prompt, output_path)
        return f"Image generated successfully and saved at: {final_path}. NEXT: Call 'check_image_background' on this file, then 'remove_background' if needed, then 'resize_for_sticker'."
    except Exception as e:
        return f"Error generating image: {str(e)}"

@tool("check_image_background", args_schema=CheckBackgroundInput, return_direct=False)
def check_background_tool(input_path: str) -> str:
    """
    Checks if an image has a transparent background or needs background removal.
    
    Use this tool AFTER generating an image to determine if background removal is needed.
    Returns 'transparent' if the image already has transparency, or 'has_background' if it needs processing.
    
    Args:
        input_path: Path to the image file to check
    
    Returns:
        Either 'transparent' or 'has_background'
    """
    if not os.path.isabs(input_path) and not input_path.startswith("data/"):
        input_path = os.path.join("data", "input", input_path)
        
    processor = get_processor()
    try:
        if processor.has_transparency(input_path):
            return f"Image '{input_path}' already has a transparent background. NEXT: Call 'resize_for_sticker' on this file."
        else:
            return f"Image '{input_path}' has a background that needs removal. NEXT: Call 'remove_background' on this file."
    except Exception as e:
        return f"Error checking background: {str(e)}"

@tool("remove_background", args_schema=RemoveBackgroundInput, return_direct=False)
def remove_background_tool(
    input_path: str,
    output_path: Optional[str] = None,
    erosion_size: int = 1,
    island_size: int = 100
) -> str:
    """
    Removes the background from an image using AI segmentation, creating a transparent PNG.
    
    Use this tool when an image has a background that needs to be removed for sticker creation.
    This uses the RMBG-1.4 model for professional-grade background removal with edge cleaning.
    
    Args:
        input_path: Path to the image with background
        output_path: Optional output path (auto-generated if not provided)
        erosion_size: Edge erosion to remove halos (0-3 recommended, default 1)
        island_size: Minimum pixel area to keep (removes noise, default 100)
    
    Returns:
        Success message with output file path or error message
    """
    if not os.path.isabs(input_path) and not input_path.startswith("data/"):
        input_path = os.path.join("data", "input", input_path)
        
    if output_path is None:
        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join("data", "output", f"nobg_{name}.png")
        
    processor = get_processor()
    try:
        final_path = processor.remove_background(
            input_path=input_path,
            output_path=output_path,
            erosion_size=erosion_size,
            island_size=island_size
        )
        return f"Background removed successfully. File saved at: {final_path}. NEXT: Call 'resize_for_sticker' on this file."
    except Exception as e:
        return f"Error removing background: {str(e)}"

@tool("resize_for_sticker", args_schema=ResizeImageInput, return_direct=False)
def resize_image_tool(
    input_path: str,
    output_path: Optional[str] = None,
    target_width: int = 370,
    target_height: int = 320
) -> str:
    """
    Resizes an image to standard sticker dimensions while maintaining aspect ratio and quality.
    
    Use this tool as the FINAL STEP to format the sticker to standard dimensions (370x320px).
    The image is centered on a transparent canvas with high-quality LANCZOS resampling.
    
    Args:
        input_path: Path to the image to resize (usually the background-removed version)
        output_path: Optional output path (auto-generated if not provided)
        target_width: Target width in pixels (default 370)
        target_height: Target height in pixels (default 320)
    
    Returns:
        Success message with final sticker path or error message
    """
    if not os.path.isabs(input_path) and not (input_path.startswith("data/input") or input_path.startswith("data/output")):
        # If it's just a filename, assume it's in data/output (where removed bg images go)
        # but also check data/input just in case.
        if os.path.exists(os.path.join("data", "output", input_path)):
            input_path = os.path.join("data", "output", input_path)
        else:
            input_path = os.path.join("data", "input", input_path)

    if output_path is None:
        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join("data", "output", f"{name}_resized.png")

    processor = get_processor()
    try:
        final_path = processor.resize_image(
            input_path=input_path,
            output_path=output_path,
            target_size=(target_width, target_height)
        )
        return f"Image resized successfully. File saved at: {final_path}"
    except Exception as e:
        return f"Error resizing image: {str(e)}"

@tool("image_to_image", args_schema=ImageToImageInput, return_direct=False)
def image_to_image_tool(prompt: str, base_image_path: str, output_filename: str) -> str:
    """
    Generates a new image based on a local base image and a text prompt.
    Use this when you have an existing image and want to apply a style or modification to it.
    
    Args:
        prompt: Description of the style or changes to apply
        base_image_path: Path to the local image to use as a base
        output_filename: Filename for the result (e.g., 'stylized_cat.png')
        
    Returns:
        Success message with path or error message
    """
    if not os.path.isabs(base_image_path) and not base_image_path.startswith("data/"):
        # Check both input and output directories
        if os.path.exists(os.path.join("data", "input", base_image_path)):
            base_image_path = os.path.join("data", "input", base_image_path)
        elif os.path.exists(os.path.join("data", "output", base_image_path)):
            base_image_path = os.path.join("data", "output", base_image_path)
        else:
            base_image_path = os.path.join("data", "input", base_image_path) # Default to input

    output_path = os.path.join("data", "output", output_filename)
    processor = get_processor()
    try:
        final_path = processor.image_to_image(prompt, base_image_path, output_path)
        return f"Image stylized successfully and saved at: {final_path}. NEXT: Call 'check_image_background' on this file, then 'remove_background' if needed, then 'resize_for_sticker'."
    except Exception as e:
        return f"Error in image-to-image generation: {str(e)}"


class ReadPromptFileInput(BaseModel):
    file_path: str = Field(description="The path or filename of the JSON prompt file (e.g., 'silent.json' or 'data/prompts/silent.json').")


@tool("read_prompt_file", args_schema=ReadPromptFileInput, return_direct=False)
def read_prompt_file_tool(file_path: str) -> str:
    """
    Reads a structured JSON prompt file and converts it into an actionable prompt.
    The JSON file contains fields like type, base_image, subject, pose, expression, action, art_style, framing, background, and extras.
    
    Use this tool when the user says to read a JSON file or use a prompt file.
    After reading, you MUST use the returned prompt to call the appropriate generation tool (generate_image or image_to_image).
    
    Args:
        file_path: Path to the JSON prompt file
        
    Returns:
        Parsed prompt details with instructions on which tool to call next
    """
    # Resolve the file path
    if not os.path.isabs(file_path) and not file_path.startswith("data/"):
        # Check data/prompts/ first, then data/input/
        if os.path.exists(os.path.join("data", "prompts", file_path)):
            file_path = os.path.join("data", "prompts", file_path)
        elif os.path.exists(os.path.join("data", "input", file_path)):
            file_path = os.path.join("data", "input", file_path)
        else:
            file_path = os.path.join("data", "prompts", file_path)

    if not os.path.exists(file_path):
        return f"Error: Prompt file not found: {file_path}"

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in {file_path}: {e}"

    # Extract fields
    prompt_type = data.get("type", "text-to-image")
    base_image = data.get("base_image")
    subject = data.get("subject", "")
    pose = data.get("pose", "")
    expression = data.get("expression", "")
    action = data.get("action", "")
    art_style = data.get("art_style", "")
    framing = data.get("framing", "full body")
    background = data.get("background", "white background")
    extras = data.get("extras")

    # Build the natural language prompt from JSON fields
    parts = []
    if subject:
        parts.append(subject)
    if pose:
        parts.append(f"in a pose: {pose}")
    if expression:
        parts.append(f"with expression: {expression}")
    if action:
        parts.append(f"doing: {action}")
    if art_style:
        parts.append(f"in {art_style}")
    if framing:
        parts.append(f"{framing} visible")
    if background:
        parts.append(background)
    if extras:
        parts.append(f"with {extras}")

    generated_prompt = ". ".join(parts) + "."

    # Derive output filename from the JSON filename
    json_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{json_name}_output.png"

    if prompt_type == "image-to-image" and base_image:
        return (
            f"PARSED FROM JSON ({file_path}):\n"
            f"Type: image-to-image\n"
            f"Base image: {base_image}\n"
            f"Generated prompt: {generated_prompt}\n"
            f"Output filename: {output_filename}\n\n"
            f"NEXT ACTION: Call 'image_to_image' with:\n"
            f"  - prompt: \"{generated_prompt}\"\n"
            f"  - base_image_path: \"{base_image}\"\n"
            f"  - output_filename: \"{output_filename}\""
        )
    else:
        return (
            f"PARSED FROM JSON ({file_path}):\n"
            f"Type: text-to-image\n"
            f"Generated prompt: {generated_prompt}\n"
            f"Output filename: {output_filename}\n\n"
            f"NEXT ACTION: Call 'generate_image' with:\n"
            f"  - prompt: \"{generated_prompt}\"\n"
            f"  - output_filename: \"{output_filename}\""
        )
