# Developer Quick Reference

Quick reference for developers working with this LangGraph-based sticker creator.

> 📝 **File Naming Note**: Some file names are historical. See [PROJECT-STRUCTURE.md](./PROJECT-STRUCTURE.md#naming-conventions--rationale) for details about naming conventions.

---

## 🎯 Common Tasks

### Run the Agent

```bash
# Standard mode
python main.py

# Streaming mode (see real-time progress)
python main_streaming.py

# Test configuration
python test_setup.py
```

### Check Errors

```python
# All errors appear in terminal
# For detailed debugging:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🛠️ Adding a New Tool

### 1. Add Method to Service

Edit `app/services/processor.py`:

```python
class StickerProcessor:
    # ... existing methods ...

    def apply_watermark(self, input_path, watermark_text, output_path):
        """Add a watermark to the image."""
        from PIL import ImageDraw, ImageFont

        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)
        # ... watermarking logic ...
        img.save(output_path)
        return output_path
```

### 2. Create Tool Wrapper

Edit `app/tools/sticker_tool.py`:

```python
# Add schema
class WatermarkInput(BaseModel):
    input_path: str = Field(description="Path to image")
    watermark_text: str = Field(description="Text to add as watermark")

# Add tool
@tool("add_watermark", args_schema=WatermarkInput, return_direct=False)
def watermark_tool(input_path: str, watermark_text: str) -> str:
    """
    Adds a watermark to an image.
    Use this when user wants to add text or branding to the sticker.
    """
    try:
        processor = get_processor()
        output_path = input_path.replace('.png', '_watermark.png')
        result = processor.apply_watermark(input_path, watermark_text, output_path)
        return f"Watermark added successfully. Saved at: {result}"
    except Exception as e:
        return f"Error adding watermark: {str(e)}"
```

### 3. Register Tool

Edit `app/agent.py`:

```python
from app.tools.sticker_tool import (
    generate_image_tool,
    check_background_tool,
    remove_background_tool,
    resize_image_tool,
    watermark_tool  # Add this
)

def create_sticker_agent():
    tools = [
        generate_image_tool,
        check_background_tool,
        remove_background_tool,
        resize_image_tool,
        watermark_tool  # Add this
    ]
    # ... rest of function
```

**That's it!** The agent will automatically learn to use the new tool.

---

## 🔧 Modifying the Agent

### Change System Prompt

Edit `app/agent.py`:

```python
agent_graph = create_react_agent(
    model=llm,
    tools=tools,
    state_modifier="""Your custom instructions here.

    You are a sticker creator that:
    - Always makes images cute
    - Prefers bright colors
    - Adds funny captions
    """
)
```

### Change Model

Edit `app/model.py`:

```python
def get_gemini_model(model_name="gemini-1.5-pro"):  # Change model
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.7,  # Increase for more creativity
        # ... other settings
    )
```

### Add Custom State

Edit `app/agent.py`:

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langchain_core.messages import AnyMessage

class CustomState(TypedDict):
    messages: Annotated[list[AnyMessage], "conversation history"]
    user_id: str  # Custom field
    sticker_count: int  # Custom field

# Then create custom graph instead of using create_react_agent
# See LangGraph docs for details
```

---

## 🐛 Debugging

### View All Messages

```python
response = agent.invoke({"messages": [HumanMessage(content="...")]})

for i, msg in enumerate(response["messages"]):
    print(f"\n[{i}] {msg.__class__.__name__}")
    print(f"Content: {msg.content[:100]}")
    if hasattr(msg, "tool_calls"):
        print(f"Tool calls: {msg.tool_calls}")
```

### Test Individual Tools

```python
from app.tools.sticker_tool import generate_image_tool

result = generate_image_tool.invoke({
    "prompt": "test image",
    "output_filename": "test.jpg"
})
print(result)
```

### Test Service Directly

```python
from app.services.processor import StickerProcessor

processor = StickerProcessor()
result = processor.generate_image("cute cat", "data/input/test.jpg")
print(result)
```

### Check State at Each Step

```python
for event in agent.stream({"messages": [...]}, stream_mode="values"):
    print("=" * 50)
    print(f"Messages: {len(event['messages'])}")
    print(f"Last: {event['messages'][-1]}")
```

---

## 📝 Code Patterns

### Tool Function Template

```python
class MyToolInput(BaseModel):
    """Input schema for my tool."""
    param1: str = Field(description="Description for LLM")
    param2: int = Field(default=10, description="Optional with default")

@tool("my_tool_name", args_schema=MyToolInput, return_direct=False)
def my_tool(param1: str, param2: int = 10) -> str:
    """
    Single-sentence description.

    More detailed explanation of WHEN and WHY to use this tool.
    The LLM reads this to decide when to call the tool.
    """
    try:
        processor = get_processor()
        result = processor.my_method(param1, param2)
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Service Method Template

```python
def my_method(self, input_path, param, output_path=None):
    """
    Pure Python implementation.
    No LangChain/LLM dependencies.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")

    # Do work
    # ...

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path)
    return output_path
```

---

## 🔍 Understanding the Flow

### Request Lifecycle

```
1. User types message
   ↓
2. main.py creates HumanMessage
   ↓
3. agent.invoke() starts LangGraph
   ↓
4. [agent node] Gemini reads state
   ↓
5. [agent node] Gemini decides action
   ↓
   ├─→ Tool call → [tools node] → Execute → Back to step 4
   └─→ Final response → [end]
   ↓
6. main.py extracts response
   ↓
7. User sees result
```

### Tool Execution Flow

```
LangGraph [tools node]
  ↓
Validates args with Pydantic schema
  ↓
Calls @tool decorated function (tool layer)
  ↓
Function calls processor method (service layer)
  ↓
Processor does actual work
  ↓
Returns result string
  ↓
LangGraph wraps in ToolMessage
  ↓
Adds to state.messages
  ↓
Routes back to [agent node]
```

---

## 📊 File Locations

| What                   | Where                       |
| ---------------------- | --------------------------- |
| Agent configuration    | `app/agent.py`              |
| LLM configuration      | `app/model.py`              |
| Tool definitions       | `app/tools/sticker_tool.py` |
| Service implementation | `app/services/processor.py` |
| Main entry point       | `main.py`                   |
| Streaming entry point  | `main_streaming.py`         |
| Environment variables  | `.env`                      |
| Generated images       | `data/input/`               |
| Processed stickers     | `data/output/`              |
| Documentation          | `docs/`                     |

---

## 🚀 Performance Tips

### Speed Up Model Loading

The RMBG-1.4 model is loaded only once on first `StickerProcessor()` instantiation. Keep the agent running for multiple requests:

```python
agent = create_sticker_agent()  # Loads model

# Process multiple requests without reloading
for prompt in prompts:
    response = agent.invoke(...)
```

### Reduce Token Usage

```python
# Use smaller model
get_gemini_model("gemini-1.5-flash")  # Faster, cheaper

# Reduce temperature (more deterministic, less tokens)
ChatGoogleGenerativeAI(temperature=0)
```

### Parallel Processing

For batch processing multiple stickers:

```python
from concurrent.futures import ThreadPoolExecutor

def process_sticker(prompt):
    # Each thread creates its own agent
    agent = create_sticker_agent()
    return agent.invoke({"messages": [HumanMessage(content=prompt)]})

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_sticker, prompts)
```

---

## 🔐 Security Notes

### API Keys

- **Never commit `.env`** to version control
- `.env` is in `.gitignore` by default
- Use `.env.example` as template

### Tool Access

- Tools only have access to what you explicitly give them
- Service layer doesn't see LLM prompts
- Agent can't access filesystem directly (only via tools)

### Input Validation

- Pydantic schemas validate all tool inputs
- Service methods should validate file paths
- Check for path traversal attacks:

```python
import os
def safe_path(path, base_dir="data"):
    # Prevent ../../../etc/passwd
    full_path = os.path.abspath(path)
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Invalid path")
    return full_path
```

---

## 📚 Further Reading

- **[LangGraph Theory](./docs/LANGGRAPH-THEORY.md)**: Deep dive into how it works
- **[Architecture](./docs/ARCHITECTURE.md)**: Design patterns and rationale
- **[Visual Flows](./docs/LANGGRAPH-THEORY.md)**: Diagrams and flow charts
- **[Project Structure](./docs/PROJECT-STRUCTURE.md)**: Complete file organization

---

## 🆘 Common Issues

### "GOOGLE_API_KEY not found"

```bash
# Make sure .env exists
cp .env.example .env

# Edit .env and add your key
nano .env  # or use any editor
```

### "ModuleNotFoundError: No module named 'langgraph'"

```bash
pip install -r requirements.txt
```

### "Model download takes forever"

First run downloads RMBG-1.4 (~1.7GB). Be patient. Subsequent runs are instant.

### "Agent keeps calling the same tool"

Check tool return string. Make sure it clearly indicates success/failure. The LLM uses this to decide next action.

### "Tool not being called"

- Check tool description (docstring) - make it clear WHEN to use
- Check Pydantic schema descriptions
- Test tool individually to ensure it works

---

## 💡 Tips and Tricks

### Make Agent More Verbose

```python
# In tool description
"""
Use this tool to generate images.

IMPORTANT: Always tell the user you're generating an image before calling this.
After calling, summarize what you generated.
"""
```

### Chain Multiple Tools

The agent automatically chains tools based on results. To encourage specific sequences:

```python
# In state_modifier
"""Always follow this workflow:
1. generate_image first
2. Then check_background
3. Then remove_background if needed
4. Finally resize_for_sticker
"""
```

### Handle Errors Gracefully

```python
@tool(...)
def my_tool(...) -> str:
    try:
        result = processor.method(...)
        return f"✓ Success: {result}"
    except FileNotFoundError as e:
        return f"✗ File not found: {e}. Please generate an image first."
    except Exception as e:
        return f"✗ Unexpected error: {e}. Please try again or use different parameters."
```

The agent will see the error and can retry or try a different approach!

---

_Happy coding! 🚀_
