# Architectural Documentation: Services vs. Tools

This document outlines the architectural separation between the **Service Layer** and the **Tool Layer** within the Sticker Creator project. This structure follows software engineering best practices for building scalable, AI-powered applications using **LangGraph** and **LangChain**.

> **📚 Related Documentation:**
>
> - [LangGraph Theory & Model Triggering](./LANGGRAPH-THEORY.md) - How the agent loop works
> - [Project Structure](./PROJECT-STRUCTURE.md) - Complete file organization and data flow
> - [Getting Started](./SETUP-GUIDE.md) - Installation and setup guide

---

## 1. The Service Layer (The "Worker")

**Location:** `app/services/processor.py`

The Service Layer contains the **core business logic** of the application. It is responsible for the actual execution of tasks such as image processing, background removal, and API communication.

- **Role:** Implementation of features.
- **Characteristics:**
  - **LLM-Agnostic:** It has no knowledge of LangChain or Large Language Models.
  - **Heavy Lifting:** Handles OpenCV operations, loading AI models into memory, and file system I/O.
  - **Unit Testable:** Can be tested independently of the AI agent.
- **Example:** The `StickerProcessor` class. It doesn't care _why_ a background is being removed; it only cares about the pixels and the algorithm.

---

## 2. The Tool Layer (The "Interface")

**Location:** `app/tools/sticker_tool.py`

The Tool Layer acts as a **bridge** between the LLM Agent and the Service Layer. It translates the capabilities of the services into a format that an AI can understand and invoke.

- **Role:** Communication and metadata.
- **Characteristics:**
  - **Semantic Descriptions:** Uses natural language to explain to the Agent _when_ and _why_ to use a specific function.
  - **Schema Validation:** Uses Pydantic to strictly define what inputs the Agent must provide.
  - **Error Handling:** Catches service-level exceptions and returns readable strings to the Agent so it can "reason" about what went wrong.
- **Example:** The `@tool` decorated functions. These provide the "manual" for the Agent to operate the Services.

---

## 3. Key Differences at a Glance

| Feature               | **Service Layer**                    | **Tool Layer**                         |
| :-------------------- | :----------------------------------- | :------------------------------------- |
| **Primary Goal**      | Executing logic.                     | Facilitating Agent interaction.        |
| **Analogy**           | The car's engine.                    | The car's steering wheel and pedals.   |
| **Input**             | Raw data (file paths, pixel arrays). | Pydantic objects/JSON from the LLM.    |
| **Output**            | Processed files or data objects.     | Strings or observations for the LLM.   |
| **Primary Libraries** | `opencv`, `PIL`, `torch`.            | `langchain`, `pydantic`.               |
| **Visibility**        | Hidden from the LLM.                 | Directly visible to the LLM's context. |

---

## 4. The Request Lifecycle

To understand how they interact, consider a request to **"Make a 370x320 sticker of a cat"**:

1.  **Agent (Model)**: Reads the user prompt and looks at the **Tool** descriptions.
2.  **Tool**: The Agent decides to call the `generate_image` tool with specific arguments.
3.  **Service**: The Tool invokes the `StickerProcessor.generate_image` method. The service talks to the Google Imagen API (v4.0 via REST or official SDK) and saves the file.
4.  **Tool**: Returns "Image saved at data/input/cat.jpg" to the Agent.
5.  **Agent**: Sees the image is saved. It now calls the `remove_background` tool.
6.  **Service**: The Service runs the `RMBG-1.4` model on the cat image.
7.  **Tool**: Reports success back to the Agent.

---

## 5. Why This Separation Matters

1.  **Reusability**: You can build a Web UI or a Telegram bot using the same **Services** without needing the **Tools** or the **Agent**.
2.  **Maintainability**: If you decide to swap the background removal AI (e.g., from `RMBG-1.4` to `Rembg`), you only change the **Service**. The **Tool** and the **Agent** remain exactly the same.
3.  **Security**: The Agent never has direct access to your file system or raw API keys; it only has access to the specific "actions" you expose through the Tools.

---

## 6. LangGraph Integration (v2.0 Update)

### Modern Agent Architecture

This project now uses **LangGraph's `create_react_agent()`** instead of the deprecated `AgentExecutor`:

```python
# app/agent.py
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,          # Gemini LLM
    tools=tools,        # Our 4 tools
    prompt=...          # System prompt
)
```

### How It Works

**LangGraph creates a graph with these nodes:**

- `__start__`: Entry point
- `agent`: Model reasoning node (calls Gemini)
- `tools`: Tool execution node (calls our Python functions)
- `__end__`: Exit point

**The execution flow:**

```
User Input → [agent node] → Decision:
                              ├─→ Tool Call → [tools node] → [back to agent]
                              └─→ Final Response → [end]
```

### Message-Based State

Instead of simple input/output, LangGraph uses **messages**:

```python
state = {
    "messages": [
        HumanMessage(content="Create a cat sticker"),
        AIMessage(content="...", tool_calls=[...]),
        ToolMessage(content="Image saved..."),
        AIMessage(content="...", tool_calls=[...]),
        ToolMessage(content="Background removed..."),
        # ... continues until done
    ]
}
```

This allows the agent to:

- See full conversation history
- Make multi-step decisions
- Retry on failures
- Maintain context across tool calls

### Benefits Over Old AgentExecutor

| Feature          | Old AgentExecutor       | New LangGraph                |
| ---------------- | ----------------------- | ---------------------------- |
| State Management | Limited                 | Full message history         |
| Customization    | Hard to modify          | Easy to customize nodes      |
| Streaming        | Limited support         | Full streaming support       |
| Debugging        | Opaque                  | Transparent state inspection |
| Prompt Control   | External hub dependency | Built-in `prompt` parameter  |
| Error Handling   | Basic                   | Advanced with retries        |

---

## 7. Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                "Create a cat sticker"                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │        main.py / main_streaming.py │
        │   Creates HumanMessage & invokes   │
        └───────────────┬───────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│                   LANGGRAPH GRAPH                          │
│   ┌─────────────────────────────────────────────────────┐ │
│   │  __start__  →  [agent]  ⇄  [tools]  →  __end__    │ │
│   └─────────────────────────────────────────────────────┘ │
│                                                             │
│   [agent] = Gemini Model (Decision Making)                │
│   [tools] = Python Tool Execution                         │
└───────┬────────────────────────────────┬──────────────────┘
        │                                │
        ▼                                ▼
┌──────────────────┐          ┌──────────────────────┐
│  app/model.py    │          │  app/tools/          │
│                  │          │  sticker_tool.py     │
│  Gemini Config   │          │                      │
│  - API Key       │          │  4 Tool Wrappers:    │
│  - Temperature   │          │  1. generate_image   │
│  - Model Name    │          │  2. check_background │
└──────────────────┘          │  3. remove_bg        │
                               │  4. resize           │
                               └──────────┬───────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │ app/services/       │
                               │ processor.py        │
                               │                     │
                               │ StickerProcessor    │
                               │ - RMBG-1.4 Model    │
                               │ - Gemini Imagen API │
                               │ - OpenCV/PIL        │
                               └──────┬──────────────┘
                                      │
                   ┌──────────────────┼──────────────────┐
                   ▼                  ▼                  ▼
            ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
            │   Gemini    │   │   RMBG-1.4  │   │  PIL/OpenCV │
            │ Imagen API  │   │   AI Model  │   │  Processing │
            └─────────────┘   └─────────────┘   └─────────────┘
                   │                  │                  │
                   └──────────┬───────┴──────────────────┘
                              ▼
                   ┌─────────────────────┐
                   │   data/input/       │
                   │  (Generated images) │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  data/output/       │
                   │ (Processed stickers)│
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │    USER RECEIVES    │
                   │   Final sticker!    │
                   └─────────────────────┘
```

---

## 8. Detailed Component Interaction

### Scenario: User requests "Create a dog sticker"

#### Phase 1: Initialization

```python
# main.py
agent = create_sticker_agent()  # From app/agent.py
```

This:

1. Loads Gemini model (`app/model.py`)
2. Imports tool definitions (`app/tools/sticker_tool.py`)
3. Creates LangGraph with ReAct pattern
4. Returns compiled graph

#### Phase 2: Invocation

```python
# main.py
response = agent.invoke({
    "messages": [HumanMessage(content="Create a dog sticker")]
})
```

LangGraph takes over and starts the loop.

#### Phase 3: Agent Loop (automatic)

**Iteration 1:**

```
[agent node] Gemini thinks:
  Input: "Create a dog sticker"
  Decision: Need to generate image first

  Action: TOOL_CALL
    name: "generate_image"
    args: {prompt: "cute dog", output_filename: "dog.jpg"}

[tools node] Execution:
  1. Validates args against GenerateImageInput schema
  2. Calls generate_image_tool("cute dog", "dog.jpg")
  3. Tool calls processor.generate_image()
  4. Service calls Gemini Imagen API
  5. Returns: "Image saved at data/input/dog.jpg"

State updated with ToolMessage
Loop continues...
```

**Iteration 2:**

```
[agent node] Gemini thinks:
  Sees: "Image saved at data/input/dog.jpg"
  Decision: Need to check background

  Action: TOOL_CALL
    name: "check_image_background"
    args: {input_path: "dog.jpg"}

[tools node] Execution:
  1. Calls check_background_tool("dog.jpg")
  2. Tool calls processor.has_transparency()
  3. Service checks alpha channel
  4. Returns: "has_background"

State updated with ToolMessage
Loop continues...
```

**Iterations 3-4:** (remove_background, resize_for_sticker)

**Iteration 5:**

```
[agent node] Gemini thinks:
  Sees: All tasks completed successfully
  Decision: Time to respond to user

  Action: RESPOND (no tool call)
    content: "Your dog sticker is ready at data/output/dog_resized.png!"

[graph] Routes to __end__
```

#### Phase 4: Return

```python
# main.py receives response
final_message = response['messages'][-1].content
print(final_message)
# Output: "Your dog sticker is ready at data/output/dog_resized.png!"
```

---

## 9. Key Architectural Decisions

### Decision 1: Service/Tool Separation

**Rationale:** Services can be reused in non-AI contexts (web API, CLI, batch processing)

### Decision 2: Message-Based State

**Rationale:** Full conversation history enables better decision-making and debugging

### Decision 3: LangGraph over AgentExecutor

**Rationale:** Better control, streaming support, modern patterns, active maintenance

### Decision 4: Gemini for Both LLM and Image Generation

**Rationale:** Single API key, integrated ecosystem, high quality results

### Decision 5: String Tool Returns

**Rationale:** LLMs reason better about text than structured objects

### Decision 6: Pydantic Schemas

**Rationale:** Type safety, automatic validation, clear contracts

---

## 10. Extension Patterns

### Adding a New Tool

1. **Add Service Method** (`app/services/processor.py`):

```python
def apply_filter(self, input_path, filter_name):
    # Implementation
    return output_path
```

2. **Create Tool Wrapper** (`app/tools/sticker_tool.py`):

```python
class ApplyFilterInput(BaseModel):
    input_path: str = Field(...)
    filter_name: str = Field(...)

@tool("apply_filter", args_schema=ApplyFilterInput)
def apply_filter_tool(input_path, filter_name) -> str:
    """Apply artistic filter to image."""
    processor = get_processor()
    result = processor.apply_filter(input_path, filter_name)
    return f"Filter applied: {result}"
```

3. **Register Tool** (`app/agent.py`):

```python
from app.tools.sticker_tool import apply_filter_tool

tools = [
    generate_image_tool,
    check_background_tool,
    remove_background_tool,
    resize_image_tool,
    apply_filter_tool,  # New!
]
```

The agent automatically learns to use the new tool based on its description!

### Customizing the Agent Prompt

Edit `app/agent.py`:

```python
agent_graph = create_react_agent(
    model=llm,
    tools=tools,
    prompt="""You are a sticker creator.
    Special requirements:
    - Always make images cute and colorful
    - Prefer cartoon style
    - Resize to 512x512 instead of 370x320
    """
)
```

---

## Summary

This architecture provides:

- ✅ Clear separation of concerns
- ✅ Testable components
- ✅ Modern LangGraph patterns
- ✅ Extensible design
- ✅ Type-safe tool calling
- ✅ Full transparency and debugging

**The three layers:**

1. **Services**: Do the work (image processing)
2. **Tools**: Provide the interface (LLM → Python)
3. **Agent**: Make decisions (reasoning loop)

Each layer can be modified independently without affecting the others.

---

**Next Steps:**

- Read [LANGGRAPH-THEORY.md](./LANGGRAPH-THEORY.md) for deep dive into model triggering
- Read [PROJECT-STRUCTURE.md](./PROJECT-STRUCTURE.md) for file organization
- Start coding with [SETUP-GUIDE.md](./SETUP-GUIDE.md)
