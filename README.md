# Sticker Creator Agent

> ⚠️ **Note on Project Name**: This folder may be named `sticker-remove` but this is a **Sticker Creator/Generator** tool. The name historically refers to the background removal feature, not the main purpose.

An AI-powered sticker creation tool that uses **LangGraph + Gemini** to generate, clean, and format professional stickers automatically.

## 🚀 Quick Outline

This project uses the **modern LangGraph architecture** (v2.0) with a ReAct agent pattern:

### 1. Core Features

- **AI Image Generation**: Create unique images from text prompts using Google Gemini Imagen 4 API
- **Background Removal**: Professional-grade segmentation using the `RMBG-1.4` AI model
- **Auto-Cleaning**: Intelligent noise removal, edge optimization, and halo removal
- **Standard Formatting**: Resizes to perfect sticker dimensions (370x320px) with transparency

### 2. Modern LangGraph Architecture

- ✅ **LangGraph `create_react_agent`** (replaces deprecated `AgentExecutor`)
- ✅ **Message-based invocation** for better state management
- ✅ **Streaming support** for real-time agent progress
- ✅ **Tool-calling with proper schemas** using Pydantic models
- ✅ **Configurable system prompts** via `prompt` parameter

### 3. Project Structure

```
app/                          # Main application package
├── agent.py                  # LangGraph ReAct agent (v2.0 pattern)
├── model.py                  # Gemini LLM configuration
├── services/                # Core business logic (LLM-agnostic)
│   └── processor.py         # StickerProcessor class (image processing)
└── tools/                   # LangChain tool wrappers
    └── sticker_tool.py      # 4 tools: generate, check, remove, resize

main.py                   # CLI entry point (standard mode)
main_streaming.py         # CLI entry point (streaming mode - real-time updates)
test_setup.py             # Environment validation (checks installation)

data/
├── input/                   # Generated images (before processing)
└── output/                  # Processed stickers (final results)

docs/                     # Comprehensive documentation (consolidated)
├── README.md                 # Documentation guide with learning paths
├── FILE-STRUCTURE-GUIDE.md  # File naming & structure clarification
├── SETUP-GUIDE.md           # Installation, configuration & parameter tuning
├── LANGGRAPH-THEORY.md      # LangGraph deep dive with visual diagrams
├── ARCHITECTURE.md          # Design patterns and rationale
├── PROJECT-STRUCTURE.md     # File reference guide
└── DEVELOPER-REFERENCE.md   # Quick reference for developers
```

**Key Points**:

- 📚 All tools in one module (`sticker_tool.py` contains 4 tools)
- 📦 Single processor class (`processor.py` contains `StickerProcessor`)
- 📁 Clear separation: `services/` (business logic) vs `tools/` (LLM interface)
- 📝 Extensive documentation in `docs/` folder (8 markdown files)

```

### 4. Workflow

1. **Generate** → Gemini Imagen creates image from prompt
2. **Check** → Verify if background removal is needed
3. **Remove** → AI-powered background removal (RMBG-1.4)
4. **Resize** → Format to standard sticker size (370x320px)

### 5. How LangGraph Works

**The ReAct Loop** (Reasoning + Acting):

```

User: "Create a cat sticker"
│
▼
┌─────────────────────────────────────────────┐
│ LangGraph automatically manages this cycle: │
│ │
│ 1. Agent (Gemini) THINKS: │
│ "I need to generate an image first" │
│ │
│ 2. Agent ACTS: │
│ Calls generate_image tool │
│ │
│ 3. Tool EXECUTES: │
│ Gemini Imagen API creates image │
│ │
│ 4. Agent OBSERVES: │
│ "Image saved at data/input/cat.jpg" │
│ │
│ ↓ (Loop continues...) │
│ │
│ 5. Agent: Check background │
│ 6. Agent: Remove background │
│ 7. Agent: Resize image │
│ 8. Agent: FINISH → Return result │
└─────────────────────────────────────────────┘

```

**Key concepts:**

- **Messages**: Every interaction (human, AI, tool) is a message in state
- **State**: Full conversation history maintained across all steps
- **Graph**: Nodes (agent, tools) connected by edges (routing logic)
- **Automatic**: LangGraph handles the loop, you just define tools

See [� Documentation](./docs/README.md) for complete guides.

---

## 📚 Documentation

> 📝 **New to the project?** Start with **[FILE-STRUCTURE-GUIDE.md](./docs/FILE-STRUCTURE-GUIDE.md)** to understand file structure and naming conventions.
> 🗺️ **Want guided tour?** See **[docs/README.md](./docs/README.md)** - Complete documentation guide with learning paths.

Comprehensive documentation is available in the `docs/` directory:

### Core Documentation

- **[⚠️ File Structure Guide](./docs/FILE-STRUCTURE-GUIDE.md)**
  File naming conventions, clarifications, structure verification, and risk assessment.

- **[🚀 Setup Guide](./docs/SETUP-GUIDE.md)**
  Installation, API key setup, configuration, parameter tuning, and troubleshooting.

- **[🧠 LangGraph Theory](./docs/LANGGRAPH-THEORY.md)** ⭐ NEW
  **Deep dive into how LangGraph triggers the model**, ReAct pattern, message-based architecture, and tool calling flow. **Read this to understand how everything works under the hood.**

- **[🏗️ Architecture Overview](./docs/ARCHITECTURE.md)**
  Understanding the separation between Services and Tools, and how LangGraph integrates.

- **[📁 Project Structure](./docs/PROJECT-STRUCTURE.md)** ⭐ NEW
  Complete file organization, responsibilities, data flow, and dependency graph.



- **[👨‍💻 Developer Reference](./docs/DEVELOPER-REFERENCE.md)** ⭐ NEW
  Quick reference for common tasks, adding tools, debugging, and code patterns.



- **[📝 Changelog](./CHANGELOG.md)**
  Details about the LangGraph v2.0 migration and new features.

### Quick Links

```

⚠️ Confused about file names? → docs/FILE-STRUCTURE-GUIDE.md
🚀 Need to install & setup? → docs/SETUP-GUIDE.md
📖 How does LangGraph work? → docs/LANGGRAPH-THEORY.md
🔧 Why this architecture? → docs/ARCHITECTURE.md
📂 What files do what? → docs/PROJECT-STRUCTURE.md
💻 How to extend/customize? → docs/DEVELOPER-REFERENCE.md
🗺️ Documentation overview? → docs/README.md

````

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
````

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 3. Validate Setup

```bash
python test_setup.py
```

### 4. Run the Agent

```bash
# Standard mode
python main.py

# Streaming mode (real-time progress)
python main_streaming.py
```

### Example Usage

```
✨ Describe your sticker: a cute cartoon cat with big eyes

🤖 Agent is working...

💭 Agent: I'll create that sticker for you. Let me generate the image first...
🔧 Tool: generate_image
💭 Agent: Now checking if background removal is needed...
🔧 Tool: check_image_background
💭 Agent: Removing the background...
🔧 Tool: remove_background
💭 Agent: Resizing to standard sticker format...
🔧 Tool: resize_for_sticker

✅ Your sticker is ready at: data/output/cat_resized.png
```

---

## 🔧 Key Updates (v2.0)

- **Modern LangGraph**: Migrated from deprecated `AgentExecutor` to `create_react_agent`
- **Gemini Imagen**: Native integration with Google's image generation API
- **Better Tools**: Enhanced descriptions and proper workflow guidance
- **Streaming Support**: Watch the agent work in real-time
- **Fixed Bugs**: Resolved critical indentation issues in processor

See [CHANGELOG.md](./CHANGELOG.md) for full details.

---

_Powered by LangGraph + Gemini_
