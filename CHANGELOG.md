# Changelog

## [2.2.0] - 2026-02-12

### 🚀 Major Changes

#### Image-to-Image Support
- **Added `image_to_image` capability** to `StickerProcessor` using Imagen 4's editing features.
- **New `image_to_image_tool`** allowing the agent to use local images as a base for stylization.
- **Updated Agent Persona** to understand and handle local image base files.

## [2.1.0] - 2026-02-12

### 🚀 Major Changes

#### Model Upgrades
- **Upgraded Gemini LLM** to `gemini-2.5-flash` for faster and more accurate reasoning.
- **Upgraded Imagen API** to version `4.0` (`imagen-4.0-generate-001`) for superior sticker image generation.

#### Tool Enhancements
- **Fixed and completed tool implementations** in `app/tools/sticker_tool.py`:
  - `check_background_tool`: Now correctly returns background status.
  - `remove_background_tool`: fully implemented with proper path handling and processor call.
  - `resize_for_sticker`: Improved path resolution to check both `input` and `output` directories.
- **Updated tool docstrings** for better agent understanding.

#### LangGraph Refinement
- **Updated `create_react_agent`** to use the `prompt` parameter instead of the deprecated/renamed `state_modifier`.
- **Improved path handling** across all tools to ensure consistent behavior in different environments.

### 📝 Documentation Updates
- Updated all core documentation files (`README.md`, `GEMINI.md`, `docs/*`) to reflect model and API version changes.

## [2.0.0] - Updated to Latest LangGraph Patterns

### 🚀 Major Changes

#### LangGraph Migration

- **Updated from deprecated `AgentExecutor`** to modern `langgraph.prebuilt.create_react_agent`
- **Removed LangChain Hub dependency** - no longer need to pull prompts externally
- **New invocation pattern** - uses message-based API: `{"messages": [HumanMessage(content=...)]}`
- **Added state management** with configurable thread IDs for conversation tracking

#### Image Generation Implementation

- **Implemented Gemini Imagen 3 API integration** for native Google AI image generation
- **Added Banana.dev support** as alternative image generation backend
- **Intelligent fallback system** - tries Gemini first, then Banana, then test image
- **Fixed critical indentation bugs** in processor.py that prevented methods from being callable

#### Modern LangGraph Features

- **Added streaming support** via `main_streaming.py` for real-time agent progress
- **Enhanced tool descriptions** with detailed docstrings and workflow guidance
- **Added `state_modifier`** with custom system prompt for better agent behavior
- **Proper error handling** and user-friendly error messages

### 🔧 Technical Improvements

#### Code Quality

- Fixed nested method definitions in `StickerProcessor` class
- Proper class structure with all methods at correct indentation level
- Added type hints and comprehensive docstrings
- Better separation of concerns (Gemini vs Banana implementations)

#### Dependencies

- Added `langgraph` package
- Added `requests` for API calls
- Organized requirements.txt with clear sections
- Added optional `banana-dev` dependency

#### Configuration

- Created `.env.example` for easier setup
- Better environment variable handling
- API key validation and fallback logic

### 📝 Files Changed

- `app/agent.py` - Migrated to LangGraph create_react_agent
- `app/services/processor.py` - Fixed indentation, implemented image generation
- `app/tools/sticker_tool.py` - Enhanced tool descriptions and parameters
- `main.py` - Updated to use new LangGraph invocation pattern
- `main_streaming.py` - New streaming interface
- `requirements.txt` - Added missing dependencies
- `.env.example` - New configuration template

### 🎯 Workflow

The agent now follows a clear, documented workflow:

1. **Generate** - Create image from prompt using Gemini Imagen API
2. **Check** - Verify if background removal is needed
3. **Remove** - Apply AI-powered background removal (RMBG-1.4)
4. **Resize** - Format to standard sticker dimensions (370x320px)

### ⚡ Breaking Changes

- **Invocation method changed**: Old `agent.invoke({"input": text})` → New `agent.invoke({"messages": [HumanMessage(content=text)]})`
- **Response format changed**: Old `response['output']` → New `response['messages'][-1].content`
- **LangChain Hub no longer used**: Removed `hub.pull("hwchase17/react")`

### 🔄 Migration Guide

If you have existing code using the old pattern:

**Old:**

```python
agent = create_sticker_agent()
response = agent.invoke({"input": "Create a cat sticker"})
print(response['output'])
```

**New:**

```python
agent = create_sticker_agent()
response = agent.invoke({"messages": [HumanMessage(content="Create a cat sticker")]})
print(response['messages'][-1].content)
```

### 📦 Installation

```bash
# Install updated dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run the agent
python main.py

# Or use streaming mode
python main_streaming.py
```
