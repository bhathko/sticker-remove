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
   # Required: Gemini LLM for agent reasoning and Imagen 3 / Nano Banana for image generation
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Getting API Keys

**Google API Key (Gemini & Nano Banana)**:

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

_Last updated: February 12, 2026_
