# Project Structure & File Organization

> ⚠️ **Note on Folder Name**: The project folder may be named `sticker-remove` but this is a **Sticker Creator/Generator** tool. The name refers to the background removal feature, not the main purpose.

## 📁 Complete Directory Structure

```
sticker-creator/                 # Project root (may be named 'sticker-remove')
│
├── main.py                      # CLI entry point (standard mode)
├── main_streaming.py            # CLI entry point (streaming mode with real-time updates)
├── test_setup.py                # Environment validation script (checks installation)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .env                         # Your API keys (gitignored)
├── README.md                    # Project overview
├── CHANGELOG.md                 # Version history and updates
│
├── app/                         # Main application package
│   ├── __init__.py              # Package initialization (empty)
│   │
│   ├── agent.py                 # LangGraph agent creator
│   │   └── create_sticker_agent()
│   │       - Initializes tools
│   │       - Configures Gemini model
│   │       - Creates ReAct agent graph
│   │       - Returns compiled graph
│   │
│   ├── model.py                 # LLM configuration
│   │   └── get_gemini_model()
│   │       - Loads GOOGLE_API_KEY
│   │       - Initializes ChatGoogleGenerativeAI
│   │       - Returns configured model
│   │
│   ├── services/                # Core business logic (LLM-agnostic)
│   │   ├── __init__.py          # Empty package initializer
│   │   └── processor.py         # Image processing service
│   │       # NOTE: Could be renamed to 'sticker_processor.py' to match class name
│   │       └── StickerProcessor class
│   │           ├── __init__()   - Load RMBG-1.4 model
│   │           ├── generate_image() - Gemini Imagen 4.0 API
│           ├── image_to_image() - Local image + Style prompt
│   │           ├── remove_background() - AI background removal
│   │           ├── resize_image() - Smart resizing with padding
│   │           └── has_transparency() - Check for alpha channel
│   │
│   └── tools/                   # LangChain tool wrappers (interfaces for LLM)
│       ├── __init__.py          # Empty package initializer
│       └── sticker_tool.py      # Tool definitions (4 tools)
│           # NOTE: Plural 'sticker_tools.py' would be more accurate
│           ├── GenerateImageInput - Pydantic schema
│           ├── CheckBackgroundInput - Pydantic schema
│           ├── RemoveBackgroundInput - Pydantic schema
│           ├── ResizeImageInput - Pydantic schema
│           ├── get_processor() - Singleton pattern
│           ├── generate_image_tool() - @tool decorator
│           ├── check_background_tool() - @tool decorator
│           ├── remove_background_tool() - @tool decorator
│           └── resize_image_tool() - @tool decorator
│
├── data/                        # File storage
│   ├── input/                   # Generated images (before processing)
│   │   └── *.jpg, *.png
│   └── output/                  # Processed stickers (after bg removal & resize)
│       └── *_nobg.png, *_resized.png
│
└── docs/                        # Documentation
    ├── README.md                # Documentation guide and learning paths
    ├── ARCHITECTURE.md          # Services vs Tools separation
    ├── LANGGRAPH-THEORY.md      # LangGraph concepts & visual diagrams
    ├── PROJECT-STRUCTURE.md     # This file - complete file organization
    ├── DEVELOPER-REFERENCE.md   # Quick reference for developers
    └── SETUP-GUIDE.md           # Setup, installation & parameter tuning
```

---

## 📝 Naming Conventions & Rationale

### Current File Names

| File                  | Current Name                   | Why This Name                             | Alternative (Better)                          |
| --------------------- | ------------------------------ | ----------------------------------------- | --------------------------------------------- |
| **Project folder**    | `sticker-remove`               | Historical (refers to background removal) | `sticker-creator` or `sticker-generator`      |
| **Tool definitions**  | `sticker_tool.py`              | Single module for all tools               | `sticker_tools.py` (plural - 4 tools inside)  |
| **Service class**     | `processor.py`                 | Generic processor name                    | `sticker_processor.py` (matches class name)   |
| **Validation script** | `test_setup.py`                | Tests the setup                           | `validate_setup.py` (avoids pytest confusion) |
| **Main files**        | `main.py`, `main_streaming.py` | ✅ Clear and standard                     | No change needed                              |
| **Agent/Model**       | `agent.py`, `model.py`         | ✅ Clear and standard                     | No change needed                              |

### Why These Names Make Sense

**Despite some historical naming, the current structure is functional because:**

1. **`processor.py`**: Contains a single `StickerProcessor` class, so it's clear from the class name
2. **`sticker_tool.py`**: All tools are related to stickers, contained in one module
3. **`test_setup.py`**: Developers understand it validates setup (not a pytest test)
4. **Folder name**: Context makes it clear this creates stickers, not removes them

### Following Python Conventions

✅ **Good patterns used:**

- Snake_case for all Python files
- Package structure with `__init__.py` files
- Clear separation: `services/` and `tools/` directories
- Documentation in `docs/` directory
- Data storage in `data/` directory

✅ **Standard Python naming:**

- Modules: lowercase with underscores (`processor.py`, `sticker_tool.py`)
- Classes: PascalCase (`StickerProcessor`, `GenerateImageInput`)
- Functions: lowercase with underscores (`get_gemini_model()`, `generate_image_tool()`)
- Constants: UPPERCASE (`GOOGLE_API_KEY`)

---

## 📄 File Responsibilities

### Entry Points

#### `main.py`

**Purpose**: Standard command-line interface

**Flow**:

```python
1. Load environment variables (.env)
2. Create directories (data/input, data/output)
3. Initialize agent via create_sticker_agent()
4. Start interactive loop
5. For each user input:
   - Create HumanMessage
   - Invoke agent with messages
   - Extract and display final response
```

**When to use**: Normal operation, production use

#### `main_streaming.py`

**Purpose**: Real-time streaming interface

**Flow**:

```python
1-4. Same as main.py
5. For each user input:
   - Create HumanMessage
   - Stream agent execution
   - Display each step as it happens
   - Show tool calls and results in real-time
```

**When to use**: Debugging, development, demos

#### `test_setup.py`

**Purpose**: Validate project configuration

**Tests**:

- Package imports
- Environment variables
- Directory structure
- Agent creation
- Processor methods
- LangGraph pattern compliance

**When to use**: After installation, before first run

---

### Core Application (`app/`)

#### `agent.py`

**Role**: Agent orchestrator

**Key Function**: `create_sticker_agent()`

```python
Returns: CompiledGraph (LangGraph agent)

Process:
1. Import tools from tools/sticker_tool.py
2. Get Gemini model from model.py
3. Define prompt (system prompt)
4. Call create_react_agent(model, tools, prompt)
5. Return compiled graph

Graph Structure:
  __start__ → agent → tools → agent → ... → __end__
                ↑_____________↓
```

**Dependencies**:

- `langgraph.prebuilt.create_react_agent`
- `app.model.get_gemini_model`
- `app.tools.sticker_tool.*`

---

#### `model.py`

**Role**: LLM configuration

**Key Function**: `get_gemini_model()`

```python
Parameters:
  model_name: str = "gemini-2.5-flash"

Returns: ChatGoogleGenerativeAI

Configuration:
  - Loads GOOGLE_API_KEY from environment
  - Sets temperature=0 (deterministic)
  - Enables convert_system_message_to_human
```

**Why separate file?**

- Easy to swap models (Gemini → Claude → GPT-4)
- Centralized configuration
- Reusable across different agents

---

### Services Layer (`app/services/`)

#### `processor.py`

**Role**: Core image processing logic

**Class**: `StickerProcessor`

**Initialization**:

```python
__init__(model_name="briaai/RMBG-1.4")
  - Loads transformers pipeline for background removal
  - Loads API key (GOOGLE_API_KEY)
  - Heavy: Downloads 1.7GB model on first run
```

**Methods**:

##### `generate_image(prompt, output_path)`

```
Purpose: Create image from text
API Priority:
  1. Try Gemini Imagen 4 (REST API)
  2. Fallback to test image (data/input/1.jpg)

Returns: Path to saved image
```

##### `remove_background(input_path, output_path, erosion_size, island_size)`

```
Purpose: AI-powered background removal
Algorithm:
  1. Load image
  2. Run RMBG-1.4 segmentation model
  3. Clean mask (remove islands/noise)
  4. Erode edges (remove halos)
  5. Gaussian blur for smooth edges
  6. Denoise RGB content
  7. Merge RGBA and save

Returns: Path to processed image
```

##### `resize_image(input_path, output_path, target_size)`

```
Purpose: Standard sticker formatting
Algorithm:
  1. Load image (with transparency)
  2. Thumbnail resize (maintains aspect ratio)
  3. Create transparent canvas (target size)
  4. Center paste image on canvas
  5. Save as PNG

Returns: Path to resized image
```

##### `has_transparency(input_path)`

```
Purpose: Check if background removal needed
Logic:
  - Check if image mode is RGBA
  - Check if any pixel has alpha < 255

Returns: Boolean
```

**No LangChain dependencies** - Pure image processing

---

### Tools Layer (`app/tools/`)

#### `sticker_tool.py`

**Role**: Bridge between LLM and Services

**Pattern**: Each tool follows this structure:

```python
1. Define Pydantic Input Schema
   class XxxInput(BaseModel):
       field1: type = Field(description="...")
       field2: type = Field(default=..., description="...")

2. Define Tool Function
   @tool("tool_name", args_schema=XxxInput, return_direct=False)
   def xxx_tool(field1, field2) -> str:
       '''
       Detailed description for the LLM.
       Explains WHEN and WHY to use this tool.
       '''
       try:
           processor = get_processor()
           result = processor.xxx_method(...)
           return f"Success: {result}"
       except Exception as e:
           return f"Error: {str(e)}"
```

**Key Design Decisions**:

- **String returns**: LLMs work best with text observations
- **Error handling**: Catch exceptions, return descriptive strings
- **Path normalization**: Handle relative/absolute paths consistently
- **Singleton processor**: `get_processor()` reuses the same instance
- **Detailed docstrings**: Help model understand tool purpose

**Four Tools**:

1. **generate_image_tool**: Creates image from prompt (first step)
2. **check_background_tool**: Determines if bg removal needed
3. **remove_background_tool**: Performs AI segmentation
4. **resize_image_tool**: Final formatting (last step)

**Tool Flow Guidance**:

```
generate_image → check_background → remove_background → resize_for_sticker
     (1)              (2)                 (3)                  (4)
```

---

### Data Storage (`data/`)

#### `data/input/`

**Purpose**: Store generated images (before processing)

**Contents**:

- Images from Gemini Imagen API
- Images from Nano Banana (google-genai)
- Fallback test images
- Format: JPG, PNG

**Naming**: User-defined via `output_filename` parameter

#### `data/output/`

**Purpose**: Store processed stickers

**Contents**:

- Background-removed images: `*_nobg.png`
- Resized stickers: `*_resized.png`
- Always PNG format (transparency support)

**Auto-generated names**: Derived from input filename

---

### Documentation (`docs/`)

#### `ARCHITECTURE.md`

**Content**:

- Services vs Tools separation
- Request lifecycle
- Why this design matters
- Comparison table

**Audience**: Developers extending the project

#### `LANGGRAPH-THEORY.md` (NEW)

**Content**:

- What is LangGraph?
- ReAct pattern explained
- How model triggering works
- Message-based architecture
- Tool calling flow
- State management
- Complete execution trace

**Audience**: Developers learning LangGraph

#### `SETUP-GUIDE.md`

**Content**:

- Installation steps
- API key setup
- First run guide
- Troubleshooting

**Audience**: New users

#### `SETUP-GUIDE.md`

**Content**:

- Background removal tuning
- Erosion size effects
- Island size effects
- Quality optimization

**Audience**: Users fine-tuning results

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│              "Create a cute cat sticker"                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ main.py  │
                    └─────┬────┘
                          │ creates
                          ▼
              ┌──────────────────────┐
              │   app/agent.py       │
              │ create_sticker_agent()│
              └──────────┬────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐    ┌──────────┐   ┌────────────┐
   │app/     │    │app/      │   │app/tools/  │
   │model.py │    │tools/    │   │(4 tools)   │
   │         │    │sticker_  │   │            │
   │Gemini   │    │tool.py   │   │Schemas     │
   └─────────┘    └─────┬────┘   └────────────┘
                        │
                        │ uses
                        ▼
              ┌──────────────────┐
              │app/services/     │
              │processor.py      │
              │StickerProcessor  │
              └──────┬───────────┘
                     │
            ┌────────┼────────┐
            │        │        │
            ▼        ▼        ▼
      ┌─────────┬─────────┬─────────┐
      │ Gemini  │ RMBG    │ PIL/    │
      │ Imagen  │ Model   │ OpenCV  │
      │ API     │         │         │
      └────┬────┴────┬────┴────┬────┘
           │         │         │
           ▼         ▼         ▼
      ┌──────────────────────────────┐
      │       data/input/            │
      │    generated images          │
      └─────────────┬────────────────┘
                    │
                    ▼
              [Processing]
                    │
                    ▼
      ┌──────────────────────────────┐
      │       data/output/           │
      │    processed stickers        │
      └─────────────┬────────────────┘
                    │
                    ▼
      ┌──────────────────────────────┐
      │      USER RECEIVES           │
      │  "Sticker ready at ..."      │
      └──────────────────────────────┘
```

---

## 🎯 Agent Execution Flow

```
INVOCATION:
agent.invoke({"messages": [HumanMessage("Create a cat sticker")]})

↓

LANGGRAPH INTERNAL LOOP:

┌─────────────────────────────────────────────────────────────┐
│ CYCLE 1: Generate Image                                     │
├─────────────────────────────────────────────────────────────┤
│ [Agent Node] Gemini reads:                                  │
│   - User message: "Create a cat sticker"                    │
│   - System: "You are an expert sticker creator..."          │
│   - Tools: generate_image, check_background, ...            │
│                                                              │
│ [Agent Node] Gemini decides:                                │
│   TOOL_CALL: generate_image(                                │
│     prompt="cute cat",                                      │
│     output_filename="cat.jpg"                               │
│   )                                                          │
│                                                              │
│ [Tools Node] Executes:                                      │
│   processor.generate_image() → Gemini Imagen API            │
│   Result: "Image saved at data/input/cat.jpg"               │
│                                                              │
│ [State Updated] Messages now include tool result            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CYCLE 2: Check Background                                   │
├─────────────────────────────────────────────────────────────┤
│ [Agent Node] Gemini reads:                                  │
│   - Previous: "Image saved at data/input/cat.jpg"           │
│                                                              │
│ [Agent Node] Gemini decides:                                │
│   TOOL_CALL: check_image_background(                        │
│     input_path="cat.jpg"                                    │
│   )                                                          │
│                                                              │
│ [Tools Node] Executes:                                      │
│   processor.has_transparency() → checks alpha channel       │
│   Result: "has_background"                                  │
│                                                              │
│ [State Updated] Messages now include check result           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CYCLE 3: Remove Background                                  │
├─────────────────────────────────────────────────────────────┤
│ [Agent Node] Gemini reads:                                  │
│   - Previous: "has_background"                              │
│                                                              │
│ [Agent Node] Gemini decides:                                │
│   TOOL_CALL: remove_background(                             │
│     input_path="cat.jpg"                                    │
│   )                                                          │
│                                                              │
│ [Tools Node] Executes:                                      │
│   processor.remove_background() → RMBG-1.4 model            │
│   Result: "Background removed. Saved at .../cat_nobg.png"   │
│                                                              │
│ [State Updated] Messages now include removal result         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CYCLE 4: Resize                                             │
├─────────────────────────────────────────────────────────────┤
│ [Agent Node] Gemini reads:                                  │
│   - Previous: "Background removed at cat_nobg.png"          │
│                                                              │
│ [Agent Node] Gemini decides:                                │
│   TOOL_CALL: resize_for_sticker(                            │
│     input_path="cat_nobg.png"                               │
│   )                                                          │
│                                                              │
│ [Tools Node] Executes:                                      │
│   processor.resize_image() → 370x320 with padding           │
│   Result: "Image resized. Saved at .../cat_resized.png"     │
│                                                              │
│ [State Updated] Messages now include resize result          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CYCLE 5: Final Response                                     │
├─────────────────────────────────────────────────────────────┤
│ [Agent Node] Gemini reads:                                  │
│   - All tools executed successfully                         │
│                                                              │
│ [Agent Node] Gemini decides:                                │
│   RESPOND: "Your cat sticker is ready at                    │
│            data/output/cat_resized.png!"                    │
│   (NO tool call)                                            │
│                                                              │
│ [Graph concludes] Routes to __end__                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    RETURN TO CALLER

Final state contains all messages including final AI response.
```

---

## 🧩 Dependency Graph

```
main.py
  └── app.agent.create_sticker_agent()
        ├── app.model.get_gemini_model()
        │     └── langchain_google_genai.ChatGoogleGenerativeAI
        │
        ├── app.tools.sticker_tool.generate_image_tool
        ├── app.tools.sticker_tool.check_background_tool
        ├── app.tools.sticker_tool.remove_background_tool
        └── app.tools.sticker_tool.resize_image_tool
              │
              └── app.services.processor.StickerProcessor
                    ├── transformers.pipeline (RMBG-1.4)
                    ├── PIL.Image
                    ├── cv2 (OpenCV)
                    ├── numpy
                    └── requests (for Gemini Imagen API)
```

---

## 📝 Key Design Principles

1. **Separation of Concerns**
   - Services: Pure logic (no LangChain)
   - Tools: LLM interface (no heavy computation)
   - Agent: Orchestration (no implementation details)

2. **Single Responsibility**
   - Each file has one clear purpose
   - Each function does one thing well

3. **Dependency Injection**
   - Tools receive processor via `get_processor()`
   - Agent receives model via `get_gemini_model()`
   - Easy to mock for testing

4. **Configuration Over Code**
   - Environment variables for API keys
   - Pydantic schemas for validation
   - Prompt parameter for system instructions

5. **User-Friendly Errors**
   - Tools catch exceptions
   - Return descriptive strings
   - LLM can reason about errors

---

## 🚀 Extension Points

Want to extend the project? Here's where to start:

### Add a New Tool

1. Define Pydantic schema in `app/tools/sticker_tool.py`
2. Add method to `StickerProcessor` class
3. Create `@tool` function wrapping the method
4. Import and add to tools list in `app/agent.py`

### Swap the LLM

1. Edit `app/model.py`
2. Replace `ChatGoogleGenerativeAI` with your model
3. Ensure it supports tool calling

### Add a New Service

1. Create new file in `app/services/`
2. Implement pure Python class (no LangChain)
3. Wrap methods with tools in `app/tools/`

### Customize the Agent

1. Edit `agent.py`
2. Modify `prompt` (system prompt)
3. Or replace `create_react_agent()` with custom graph

---

_For theoretical background, see [LANGGRAPH-THEORY.md](./LANGGRAPH-THEORY.md)_  
_For architecture rationale, see [ARCHITECTURE.md](./ARCHITECTURE.md)_
