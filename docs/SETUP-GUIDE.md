# Setup & Configuration Guide

Complete guide for installing, configuring, and fine-tuning the sticker creator.

---

## 📦 Installation

### Prerequisites

- Python 3.8+ installed
- pip package manager
- Git (optional, for cloning)

### Steps

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**:

   ```bash
   python test_setup.py
   ```

   This validates that all dependencies are installed and the environment is configured correctly.

---

## 🔑 Configuration

### Environment Variables

The project uses a `.env` file for API keys and sensitive configuration.

### Setup Steps

1. **Copy the example file**:

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API keys**:

   ```bash
   # Required: Gemini LLM for agent reasoning and Imagen 4.0 for image generation
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Getting API Keys

**Google API Key (Gemini & Imagen 4)**:

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create or select a project
3. Generate API key
4. Add to `.env` as `GOOGLE_API_KEY`

---

## 📁 Directory Structure

The application automatically creates necessary directories on first run:

- **`data/input/`**: Generated images are saved here
- **`data/output/`**: Processed stickers (background removed, resized) are saved here

You can manually create them if needed:

```bash
mkdir -p data/input data/output
```

---

## 🚀 Running the Application

### Standard Mode (Recommended)

```bash
python main.py
```

Features:

- Interactive command-line interface
- Clean output showing only final results
- Best for production use

Example usage:

```
You: Create a sticker of a cool robot
Agent: I'll generate that image for you...
Agent: Your sticker is ready at: data/output/robot_resized.png
```

### Streaming Mode (Debugging)

```bash
python main_streaming.py
```

Features:

- Real-time display of agent reasoning
- Shows each tool call as it happens
- See thinking process and intermediate steps
- Best for debugging and understanding agent behavior

Example output:

```
You: Create a cat sticker

[Agent]: I need to generate an image first
[Tool Call]: generate_image("cat", "cat.jpg")
[Result]: Image saved at cat.jpg
[Agent]: Now I'll check the background
[Tool Call]: check_background("cat.jpg")
[Result]: has_background
[Agent]: Removing background...
...
```

---

## ⚙️ Parameter Tuning

### Background Removal Settings

The background removal process uses AI (RMBG-1.4 model) with post-processing to clean edges and artifacts.

#### Available Parameters

| Parameter      | Default | Range    | Description                                                  |
| -------------- | ------- | -------- | ------------------------------------------------------------ |
| `erosion_size` | 1       | 0 - 3    | Removes edge halos. Increase if background color bleeds      |
| `island_size`  | 100     | 50 - 200 | Removes background specks. Increase to remove more artifacts |

#### When to Adjust

**`erosion_size`** (Edge Cleanup):

- **Increase (2-3)**: If you see background colors bleeding into character edges
- **Decrease (0)**: If character details are being removed
- **Default (1)**: Works for most images

**`island_size`** (Artifact Removal):

- **Increase (150-200)**: If background has many small floating pixels/specks
- **Decrease (50-75)**: If small character details (like whiskers, antennae) disappear
- **Default (100)**: Balances cleanup vs detail preservation

#### How to Modify

Edit `app/services/processor.py`:

```python
def remove_background(self, input_path, output_path,
                     erosion_size=1,    # Adjust this
                     island_size=100):  # Adjust this
    # ... implementation
```

Then invoke via tools with custom parameters (requires modifying tool signatures).

---

### Image Resizing Settings

Final stickers are resized to fit standard dimensions with aspect ratio preservation.

#### Current Settings

| Parameter         | Default     | Description                       |
| ----------------- | ----------- | --------------------------------- |
| `target_width`    | 370         | Final canvas width                |
| `target_height`   | 320         | Final canvas height               |
| `maintain_aspect` | True        | Preserve original aspect ratio    |
| `padding_color`   | Transparent | Background color for letterboxing |
| `resampling`      | LANCZOS     | High-quality resampling algorithm |

#### Resizing Behavior

The resizer:

1. Calculates aspect ratio
2. Scales image to fit within target dimensions
3. Centers image on canvas
4. Adds transparent padding (letterboxing) if needed

#### How to Modify

Edit `app/services/processor.py`:

```python
def resize_image(self, input_path, output_path,
                target_width=370,   # Adjust width
                target_height=320): # Adjust height
    # ... implementation
```

For different sticker sizes:

- **Telegram stickers**: 512x512 recommended
- **WhatsApp stickers**: 512x512 max
- **Discord emoji**: 128x128
- **iMessage stickers**: 300x300, 408x408, or 618x618

---

## 🔍 Technical Details

### Image Processing Pipeline

1. **Generation**: Gemini Imagen API or Nano Banana (google-genai SDK) creates image from text
2. **Background Check**: Analyzes alpha channel to detect background
3. **AI Removal**: RMBG-1.4 transformer model segments foreground/background
4. **Edge Erosion**: OpenCV's `erode()` function shrinks transparency mask
5. **Island Removal**: Connected Components analysis removes isolated pixels
6. **Resizing**: Pillow's LANCZOS resampling maintains sharpness

### Quality Settings

All operations use high-quality algorithms:

- **Resampling**: LANCZOS (highest quality)
- **Image format**: PNG with alpha channel
- **Color depth**: Full RGBA (32-bit)
- **Compression**: PNG optimal (lossless)

---

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**:

```bash
pip install -r requirements.txt --upgrade
```

**"API key not found"**:

- Verify `.env` file exists in project root
- Check key names match exactly: `GOOGLE_API_KEY`
- Restart application after editing `.env`

**"RMBG model download failed"**:

- First run downloads ~1.7GB model from Hugging Face
- Ensure stable internet connection
- Model caches to `~/.cache/huggingface/`

**Images have rough edges**:

```python
# Increase erosion_size in processor.py
erosion_size=2  # or 3 for aggressive cleanup
```

**Small character details removed**:

```python
# Decrease erosion_size and island_size
erosion_size=0
island_size=50
```

**Agent doesn't call tools**:

- Check tool descriptions in `app/tools/sticker_tool.py`
- Try streaming mode to see agent reasoning: `python main_streaming.py`
- Verify GOOGLE_API_KEY is valid

---

## 🔄 Updating

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Clear Model Cache (if needed)

```bash
rm -rf ~/.cache/huggingface/hub/models--briaai--RMBG-1.4
```

The model will re-download on next run.

---

## 📚 Next Steps

After setup:

1. Try creating your first sticker: `python main.py`
2. Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand design
3. Read [LANGGRAPH-THEORY.md](./LANGGRAPH-THEORY.md) to understand agent flow
4. Read [DEVELOPER-REFERENCE.md](./DEVELOPER-REFERENCE.md) for customization

---

## 💬 Example Prompts

You can use prompts in two ways:

1. **Type directly** — paste a text prompt into the agent
2. **Use a JSON file** — save a structured JSON file in `data/prompts/` and tell the agent to read it

---

### Using JSON Prompt Files

Instead of typing a long prompt, create a `.json` file in `data/prompts/` and tell the agent:

```
read prompt from silent.json
```

or simply:

```
use silent.json
```

The agent will read the JSON, build the prompt automatically, detect whether it's text-to-image or image-to-image (based on `base_image`), and run the full pipeline.

#### Available Example Files

| File                         | Type           | Description                                 |
| ---------------------------- | -------------- | ------------------------------------------- |
| `data/prompts/silent.json`   | image-to-image | Character with finger on lips (shh gesture) |
| `data/prompts/waving.json`   | image-to-image | Character waving hello                      |
| `data/prompts/thumbsup.json` | image-to-image | Character giving thumbs up                  |
| `data/prompts/crying.json`   | image-to-image | Character crying with tear drops            |
| `data/prompts/cool_cat.json` | text-to-image  | Cool cartoon cat with sunglasses            |

#### Creating Your Own JSON Prompt File

Create a new `.json` file in `data/prompts/` with this structure:

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing straight, one finger held up to lips",
  "expression": "calm, secretive",
  "action": "making a 'shh' silent gesture",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": null
}
```

For text-to-image (no base image), set `"type": "text-to-image"` and `"base_image": null`.

---

### Prompt Schema

Every prompt follows this structure:

```json
{
  "type": "text-to-image | image-to-image",
  "base_image": "filename or null",
  "subject": "what the character is",
  "pose": "body position and gesture",
  "expression": "facial emotion",
  "action": "what the character is doing",
  "art_style": "visual style to use",
  "framing": "full body | upper body | close-up",
  "background": "background description",
  "extras": "additional details (props, effects, text)"
}
```

> **Note**: Not all fields are required. Use only what's relevant to your prompt. The `base_image` field is only for image-to-image.

---

### Text-to-Image Examples

#### 1. Simple Character

```json
{
  "type": "text-to-image",
  "base_image": null,
  "subject": "cartoon cat",
  "pose": "standing upright",
  "expression": "cool, confident",
  "action": "wearing sunglasses",
  "art_style": "cartoon sticker style, flat colors, clean lines",
  "framing": "full body",
  "background": "white background",
  "extras": null
}
```

**Prompt:**

```
Create a cute cartoon cat standing upright, wearing sunglasses, looking cool and confident. Full body visible, cartoon sticker style, flat colors, clean lines, white background.
```

#### 2. Detailed Character

```json
{
  "type": "text-to-image",
  "base_image": null,
  "subject": "chibi astronaut dog",
  "pose": "floating in zero gravity",
  "expression": "happy, wonder",
  "action": "holding a small planet",
  "art_style": "kawaii, chibi proportions, clean lines",
  "framing": "full body",
  "background": "white background",
  "extras": "small stars around the character"
}
```

**Prompt:**

```
A chibi-style astronaut dog floating in zero gravity, holding a small planet, looking happy with wonder. Kawaii art style, chibi proportions, clean lines, full body visible, white background, small stars around the character.
```

#### 3. Expressive Emotion

```json
{
  "type": "text-to-image",
  "base_image": null,
  "subject": "round chubby penguin",
  "pose": "standing, leaning back slightly",
  "expression": "laughing hard, tears of joy",
  "action": "holding belly while laughing",
  "art_style": "cartoon sticker style, flat colors, bold outlines",
  "framing": "full body",
  "background": "white background",
  "extras": "tear drops flying off, laughter lines"
}
```

**Prompt:**

```
A round chubby penguin leaning back, laughing hard with tears of joy streaming down its face, holding its belly. Cartoon sticker style, flat colors, bold outlines, full body, white background.
```

#### 4. Action Pose

```json
{
  "type": "text-to-image",
  "base_image": null,
  "subject": "tiny dragon",
  "pose": "sitting on the ground",
  "expression": "focused, playful",
  "action": "breathing a small flame to roast a marshmallow on a stick",
  "art_style": "cute cartoon style, soft shading",
  "framing": "full body",
  "background": "white background",
  "extras": "marshmallow on a stick, small campfire"
}
```

**Prompt:**

```
A tiny dragon sitting on the ground, breathing a small flame to roast a marshmallow on a stick, looking focused and playful. Cute cartoon style, soft shading, full body, white background.
```

---

### Image-to-Image Examples

These use a local image as a reference. Place your base image in `data/input/` first.

#### Pose / Body Language Changes

##### 5. Silent Gesture

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing straight, one finger held up to lips",
  "expression": "calm, secretive",
  "action": "making a 'shh' silent gesture",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": null
}
```

**Prompt:**

```
Use 4.png as a base. The character should be standing straight with one finger held up to their lips in a "shh" silent gesture, looking calm and secretive. Full body visible, same character design and art style.
```

##### 6. Waving Hello

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing, one hand raised high waving",
  "expression": "smiling warmly, friendly",
  "action": "waving hello",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": null
}
```

**Prompt:**

```
Use 4.png as a base. The character should be waving hello with one hand raised high, smiling warmly. Full body, same character design and art style.
```

##### 7. Thumbs Up

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing, one arm extended with thumb up",
  "expression": "confident grin, proud",
  "action": "giving a big thumbs up",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": "small sparkle near thumb"
}
```

**Prompt:**

```
Use 4.png as a base. The character should be giving a big thumbs up with a confident grin. Full body, same character design and art style.
```

##### 8. Sitting Down

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "sitting on the ground, legs crossed",
  "expression": "relaxed, happy",
  "action": "sitting casually",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": null
}
```

**Prompt:**

```
Use 4.png as a base. The character should be sitting on the ground with legs crossed, looking relaxed and happy. Full body, same character design and art style.
```

##### 9. Jumping for Joy

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "mid-air, arms raised above head",
  "expression": "excited, overjoyed",
  "action": "jumping in celebration",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": "motion lines below feet"
}
```

**Prompt:**

```
Use 4.png as a base. The character should be jumping in the air with arms raised in celebration, looking overjoyed. Full body, same character design and art style.
```

#### Emotion / Expression Changes

##### 10. Crying

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing, shoulders slumped, fists near eyes",
  "expression": "sobbing, very sad",
  "action": "crying with big tear drops",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": "large exaggerated tear drops flying off"
}
```

**Prompt:**

```
Use 4.png as a base. The character should be sobbing with big tear drops flying off, mouth open wide, fists near eyes. Same character design and art style.
```

##### 11. Angry

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing, fists clenched at sides",
  "expression": "furious, red face",
  "action": "being angry",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": "steam coming out of ears, anger vein mark on forehead"
}
```

**Prompt:**

```
Use 4.png as a base. The character should look furious with clenched fists, red face, and steam coming out of ears. Same character design and art style.
```

##### 12. Sleeping

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "curled up or lying down",
  "expression": "peaceful, eyes closed",
  "action": "sleeping",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": "small 'Zzz' speech bubble, pillow optional"
}
```

**Prompt:**

```
Use 4.png as a base. The character should be sleeping peacefully, curled up with eyes closed and a small "Zzz" bubble. Same character design and art style.
```

##### 13. Surprised / Shocked

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "standing, leaning back slightly, hands up",
  "expression": "wide open eyes, open mouth, shocked",
  "action": "reacting in surprise",
  "art_style": "same as reference image",
  "framing": "full body",
  "background": "white background",
  "extras": "exclamation marks around character, sweat drop"
}
```

**Prompt:**

```
Use 4.png as a base. The character should have wide open eyes and mouth, leaning back with hands up, looking completely shocked. Exclamation marks around them. Same character design and art style.
```

#### Style Changes

##### 14. Pixel Art Version

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "same as reference",
  "expression": "same as reference",
  "action": "same as reference",
  "art_style": "pixel art, 16-bit retro game style",
  "framing": "full body",
  "background": "white background",
  "extras": "keep same colors, outfit, and features"
}
```

**Prompt:**

```
Use 4.png as a base. Redraw this exact character in pixel art style (16-bit retro game style). Keep the same colors, outfit, and features. Full body, white background.
```

##### 15. Watercolor Version

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "same as reference",
  "expression": "same as reference",
  "action": "same as reference",
  "art_style": "soft watercolor painting, paint bleeds, paper texture",
  "framing": "full body",
  "background": "white background",
  "extras": "keep same design but change rendering to watercolor"
}
```

**Prompt:**

```
Use 4.png as a base. Redraw this exact character in a soft watercolor painting style with paint bleeds and paper texture. Keep the same pose and design. Full body, white background.
```

##### 16. 3D Render Version

```json
{
  "type": "image-to-image",
  "base_image": "4.png",
  "subject": "same character from reference",
  "pose": "same as reference",
  "expression": "same as reference",
  "action": "same as reference",
  "art_style": "3D rendered, soft lighting, smooth shading, Pixar-like",
  "framing": "full body",
  "background": "white background",
  "extras": "same design and proportions, 3D depth"
}
```

**Prompt:**

```
Use 4.png as a base. Redraw this exact character as a 3D rendered figure with soft lighting and smooth shading, Pixar-like quality. Same design and proportions. Full body, white background.
```

---

### Schema Field Reference

| Field        | Required | Description                                                                     |
| ------------ | -------- | ------------------------------------------------------------------------------- |
| `type`       | Yes      | `text-to-image` (from scratch) or `image-to-image` (from base image)            |
| `base_image` | i2i only | Filename in `data/input/` (e.g. `"4.png"`)                                      |
| `subject`    | Yes      | What the character is (e.g. `"cartoon cat"`, `"same character from reference"`) |
| `pose`       | Yes      | Body position and limb placement                                                |
| `expression` | Yes      | Facial emotion (e.g. `"happy"`, `"furious"`, `"calm"`)                          |
| `action`     | No       | What the character is doing (e.g. `"waving"`, `"sleeping"`)                     |
| `art_style`  | Yes      | Visual style (e.g. `"cartoon"`, `"pixel art"`, `"same as reference"`)           |
| `framing`    | Yes      | `"full body"`, `"upper body"`, or `"close-up"`                                  |
| `background` | Yes      | Usually `"white background"` for stickers                                       |
| `extras`     | No       | Props, effects, text bubbles (e.g. `"Zzz bubble"`, `"sparkles"`)                |

### Tips for Better Results

| Tip                                                    | Why                                                     |
| ------------------------------------------------------ | ------------------------------------------------------- |
| Always set `framing` to `"full body"`                  | Prevents cropped/partial characters                     |
| Set `art_style` to `"same as reference image"` for i2i | Keeps consistency with base image                       |
| Be specific in `pose` — describe limb positions        | `"one finger on lips"` > `"silent gesture"`             |
| Set `background` to `"white background"`               | Produces cleaner sticker after bg removal               |
| Use `extras` for visual effects                        | Tear drops, sparkles, speech bubbles add expressiveness |
| Keep `expression` and `action` separate                | Avoids confusion between emotion and movement           |

---

_Last updated: February 12, 2026_
