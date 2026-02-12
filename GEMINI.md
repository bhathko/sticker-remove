# GEMINI.md - Sticker Creator Agent Context

This project is an AI-powered sticker creation tool that utilizes **LangGraph** and **Google Gemini** to generate, process, and format professional stickers.

## 🚀 Project Overview

- **Purpose**: Automate the creation of stickers from text prompts.
- **Core Stack**: 
  - **Orchestration**: LangGraph (v2.0 ReAct agent pattern).
  - **LLM/Image Gen**: Google Gemini (Imagen 3 API via REST and official google-genai SDK).
  - **Image Processing**: RMBG-1.4 (Background Removal), OpenCV, PIL, PyTorch.
  - **Architecture**: Separates **Services** (core business logic in `app/services/processor.py`) from **Tools** (LLM interface in `app/tools/sticker_tool.py`).
  ## 🛠️ Key Commands

- **Setup Dependencies**: `pip install -r requirements.txt`
- **Environment Setup**: `cp .env.example .env` (Requires `GOOGLE_API_KEY`)
- **Validate Setup**: `python test_setup.py`
- **Run Agent (Standard)**: `python main.py`
- **Run Agent (Streaming)**: `python main_streaming.py`

## 📂 Project Structure

- `app/agent.py`: LangGraph agent definition using `create_react_agent`.
- `app/model.py`: Gemini LLM configuration via LangChain.
- `app/services/processor.py`: `StickerProcessor` class for image generation, background removal (RMBG-1.4), and resizing.
- `app/tools/sticker_tool.py`: LangChain tools (`generate_image`, `check_image_background`, `remove_background`, `resize_for_sticker`).
- `data/`: `input/` for base images, `output/` for final stickers.
- `docs/`: Extensive documentation including `ARCHITECTURE.md`, `LANGGRAPH-THEORY.md`, and `DEVELOPER-REFERENCE.md`.

## 🏗️ Architecture & Flow

The agent follows a ReAct loop:
1. **Reason**: Decide which tool to call based on user prompt and current state.
2. **Act**: Execute tool (e.g., `generate_image`).
3. **Observe**: Process tool output and update state.

**Standard Workflow**:
`Prompt` → `Generate (Imagen 3)` → `Check BG` → `Remove BG (RMBG-1.4)` → `Resize (370x320px)`

## 📝 Development Conventions

- **Tool Creation**:
  - Define a Pydantic `BaseModel` for input schema in `app/tools/sticker_tool.py`.
  - Use the `@tool` decorator with `args_schema` and a descriptive docstring (the LLM uses this to decide when to call the tool).
  - Always return a clear string result for the LLM to interpret.
- **Service Layer**:
  - Implement core logic in `StickerProcessor`.
  - Avoid LLM-specific dependencies in the service layer.
  - Handle file path normalization (defaults to `data/input` or `data/output`).
- **State Management**:
  - Uses the message-based state of LangGraph.
  - The `state_modifier` in `app/agent.py` defines the system prompt and persona.
- **Error Handling**:
  - Tools should catch exceptions and return informative error messages to the agent so it can attempt recovery.

## 📚 Reference Documentation
For deep dives, refer to:
- `docs/README.md`: Documentation map.
- `docs/FILE-STRUCTURE-GUIDE.md`: Naming conventions and structure.
- `docs/LANGGRAPH-THEORY.md`: Details on the LangGraph implementation.
- `docs/DEVELOPER-REFERENCE.md`: Guide for adding new tools or modifying the agent.
