# LangGraph Theory & Model Triggering Explained

## 📚 Table of Contents

1. [What is LangGraph?](#what-is-langgraph)
2. [ReAct Pattern](#react-pattern)
3. [How LangGraph Triggers the Model](#how-langgraph-triggers-the-model)
4. [Message-Based Architecture](#message-based-architecture)
5. [Tool Calling Flow](#tool-calling-flow)
6. [State Management](#state-management)

---

## What is LangGraph?

**LangGraph** is a library for building stateful, multi-actor applications with LLMs. It extends LangChain with:

- **Graph-based execution**: Define workflows as nodes and edges
- **State persistence**: Maintain conversation context across turns
- **Cyclic flows**: Allow agents to loop and retry actions
- **Better control**: Fine-grained control over agent execution

### Key Concept: Graphs vs Chains

```
Traditional Chain (Linear):
Input → Agent → Tool → Output

LangGraph (Cyclic Graph):
Input → Agent → Tool → Agent → Tool → Agent → Output
         ↑____________↓
```

LangGraph allows **cyclic execution**, meaning the agent can:

1. Think about a problem
2. Use a tool
3. Think about the result
4. Use another tool
5. Repeat until complete

---

## ReAct Pattern

**ReAct** = **Reasoning** + **Acting**

This is the core pattern used by `create_react_agent()`:

```
1. REASON: "I need to generate an image first"
2. ACT: Call generate_image tool
3. OBSERVE: "Image saved at data/input/cat.jpg"
4. REASON: "Now I need to check if it has a background"
5. ACT: Call check_image_background tool
6. OBSERVE: "has_background"
7. REASON: "I should remove the background"
8. ACT: Call remove_background tool
9. OBSERVE: "Background removed successfully"
10. REASON: "Finally, resize it"
11. ACT: Call resize_for_sticker tool
12. OBSERVE: "Image resized successfully"
13. FINISH: "Your sticker is ready!"
```

Each cycle has three phases:

- **Thought**: Model decides what to do
- **Action**: Tool is executed
- **Observation**: Result is fed back to model

---

## How LangGraph Triggers the Model

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER INPUT                            │
│         "Create a cute cat sticker"                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 LANGGRAPH AGENT                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              STATE (Messages)                     │  │
│  │  [HumanMessage("Create a cute cat sticker")]     │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│                      ▼                                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │           MODEL NODE (Gemini)                     │  │
│  │  - Reads all messages in state                    │  │
│  │  - Reads tool descriptions                        │  │
│  │  - Decides: respond OR call tool                  │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│         ┌────────────┴────────────┐                     │
│         │                         │                     │
│         ▼                         ▼                     │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   RESPOND    │         │  TOOL CALL   │             │
│  │   (Finish)   │         │   (Action)   │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                     │
│                                   ▼                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │              TOOL NODE                            │  │
│  │  - Executes the requested tool                    │  │
│  │  - Adds result to state                           │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│                      │ (Loop back to Model Node)        │
│                      └──────────────┐                    │
│                                     │                    │
└─────────────────────────────────────┼────────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  FINAL RESPONSE  │
                            └──────────────────┘
```

### Step-by-Step Execution

#### 1. **Initialization**

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,          # Gemini model
    tools=tools,        # List of available tools
    state_modifier=...  # System prompt
)
```

This creates a **compiled graph** with pre-built nodes:

- `__start__`: Entry point
- `agent`: Model reasoning node
- `tools`: Tool execution node
- `__end__`: Exit point

#### 2. **Invocation**

```python
response = agent.invoke({
    "messages": [HumanMessage(content="Create a cat sticker")]
})
```

When you call `invoke()`:

1. Input is added to the state
2. Graph execution begins at `__start__`
3. Flows to `agent` node

#### 3. **Model Node Execution**

The model node does this **automatically**:

```python
# Pseudo-code of what happens inside
def agent_node(state):
    messages = state["messages"]

    # Model reads:
    # 1. All previous messages
    # 2. Tool descriptions/schemas
    # 3. System prompt (state_modifier)

    response = model.invoke(messages)

    if response.tool_calls:
        # Model decided to use a tool
        return {"next": "tools", "messages": [response]}
    else:
        # Model decided to respond
        return {"next": "end", "messages": [response]}
```

#### 4. **Tool Node Execution**

If model requests a tool:

```python
def tools_node(state):
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    results = []
    for tool_call in tool_calls:
        tool = find_tool(tool_call.name)
        result = tool.invoke(tool_call.args)
        results.append(ToolMessage(content=result))

    # Add results to state and go back to agent
    return {"next": "agent", "messages": results}
```

#### 5. **Loop Continues**

The cycle repeats until the model decides to **respond** instead of calling a tool.

---

## Message-Based Architecture

### Why Messages?

LangGraph uses a **message list** as the primary state:

```python
state = {
    "messages": [
        HumanMessage(content="Create a cat sticker"),
        AIMessage(
            content="I'll generate the image first",
            tool_calls=[{
                "name": "generate_image",
                "args": {"prompt": "cute cat", "filename": "cat.jpg"}
            }]
        ),
        ToolMessage(
            content="Image saved at data/input/cat.jpg",
            tool_call_id="123"
        ),
        AIMessage(
            content="Now checking background...",
            tool_calls=[{
                "name": "check_image_background",
                "args": {"input_path": "cat.jpg"}
            }]
        ),
        ToolMessage(
            content="has_background",
            tool_call_id="124"
        ),
        # ... more messages ...
        AIMessage(content="Your sticker is ready at data/output/cat_resized.png")
    ]
}
```

### Message Types

1. **HumanMessage**: User input
2. **AIMessage**: Model's response (may include tool calls)
3. **ToolMessage**: Tool execution result
4. **SystemMessage**: System instructions

### Benefits

- **Full context**: Model sees entire conversation history
- **Transparency**: You can inspect every step
- **Resumability**: Can save and resume from any point
- **Debugging**: Easy to see where things went wrong

---

## Tool Calling Flow

### How Model Triggers Tools

Gemini (and other modern LLMs) support **native tool calling**:

#### 1. **Tool Schema Registration**

When you pass tools to `create_react_agent`, they're converted to this format:

```json
{
  "name": "generate_image",
  "description": "Generates an image from a text prompt using Google Gemini Imagen API...",
  "parameters": {
    "type": "object",
    "properties": {
      "prompt": {
        "type": "string",
        "description": "Detailed description of the image to generate"
      },
      "output_filename": {
        "type": "string",
        "description": "Name for the saved file (e.g., 'cat_sticker.jpg')"
      }
    },
    "required": ["prompt", "output_filename"]
  }
}
```

#### 2. **Model Decision Making**

On each turn, Gemini receives:

```
System: You are an expert sticker creation assistant...

Tools available:
- generate_image(prompt, output_filename)
- check_image_background(input_path)
- remove_background(input_path, ...)
- resize_for_sticker(input_path, ...)

Conversation:
Human: Create a cute cat sticker

What do you do next?
```

#### 3. **Model Response**

Gemini can respond in two ways:

**Option A: Call a tool**

```json
{
  "content": "I'll generate the cat image first.",
  "tool_calls": [
    {
      "id": "call_123",
      "name": "generate_image",
      "arguments": {
        "prompt": "cute cartoon cat with big eyes",
        "output_filename": "cat.jpg"
      }
    }
  ]
}
```

**Option B: Final response**

```json
{
  "content": "Your sticker is ready at data/output/cat_resized.png",
  "tool_calls": []
}
```

#### 4. **Automatic Execution**

LangGraph automatically:

1. Parses the tool call
2. Validates arguments against schema
3. Executes the Python function
4. Captures the result
5. Adds it back to messages
6. Triggers the model again

---

## State Management

### Thread-Based Conversations

```python
agent.invoke(
    {"messages": [HumanMessage(content="Create a cat sticker")]},
    config={"configurable": {"thread_id": "user_123"}}
)
```

The `thread_id` allows:

- **Multiple conversations**: Different users, different contexts
- **Persistence**: Save/load conversation state
- **Isolation**: Each thread has independent state

### State Schema

```python
class AgentState(TypedDict):
    messages: list[AnyMessage]  # The conversation history
    # Can add custom fields:
    # user_id: str
    # generated_files: list[str]
    # error_count: int
```

### State Updates

Each node can **update** the state:

```python
# Append to messages
return {"messages": [new_message]}

# Replace messages (rarely used)
return {"messages": [new_message], "replace": True}
```

---

## Complete Example Flow

Let's trace a complete execution:

### Input

```python
agent.invoke({"messages": [HumanMessage(content="Create a dog sticker")]})
```

### Execution Trace

```
┌─────────────────────────────────────────────────────────────┐
│ TURN 1: Initial Request                                     │
├─────────────────────────────────────────────────────────────┤
│ State: [HumanMessage("Create a dog sticker")]              │
│                                                              │
│ Model thinks: "I need to generate an image first"          │
│ Model action: TOOL CALL generate_image                      │
│   - prompt: "cute dog"                                      │
│   - output_filename: "dog.jpg"                              │
│                                                              │
│ State: + AIMessage(tool_calls=[...])                        │
│                                                              │
│ Tool executes: Calls Gemini Imagen API                      │
│ Tool result: "Image saved at data/input/dog.jpg"            │
│                                                              │
│ State: + ToolMessage("Image saved at data/input/dog.jpg")   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TURN 2: Check Background                                    │
├─────────────────────────────────────────────────────────────┤
│ Model sees: "Image saved at data/input/dog.jpg"            │
│ Model thinks: "Now I should check if it needs bg removal"  │
│ Model action: TOOL CALL check_image_background             │
│   - input_path: "dog.jpg"                                   │
│                                                              │
│ State: + AIMessage(tool_calls=[...])                        │
│                                                              │
│ Tool executes: Checks image transparency                    │
│ Tool result: "has_background"                               │
│                                                              │
│ State: + ToolMessage("has_background")                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TURN 3: Remove Background                                   │
├─────────────────────────────────────────────────────────────┤
│ Model sees: "has_background"                               │
│ Model thinks: "I need to remove the background"            │
│ Model action: TOOL CALL remove_background                   │
│   - input_path: "dog.jpg"                                   │
│                                                              │
│ State: + AIMessage(tool_calls=[...])                        │
│                                                              │
│ Tool executes: Runs RMBG-1.4 AI model                       │
│ Tool result: "Background removed. Saved at .../dog_nobg.png"│
│                                                              │
│ State: + ToolMessage("Background removed...")                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TURN 4: Resize                                              │
├─────────────────────────────────────────────────────────────┤
│ Model sees: "Background removed at dog_nobg.png"           │
│ Model thinks: "Final step is to resize"                    │
│ Model action: TOOL CALL resize_for_sticker                  │
│   - input_path: "dog_nobg.png"                              │
│                                                              │
│ State: + AIMessage(tool_calls=[...])                        │
│                                                              │
│ Tool executes: Resizes to 370x320                           │
│ Tool result: "Image resized. Saved at .../dog_resized.png" │
│                                                              │
│ State: + ToolMessage("Image resized...")                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TURN 5: Final Response                                      │
├─────────────────────────────────────────────────────────────┤
│ Model sees: All tools executed successfully                │
│ Model thinks: "Task complete, I should respond to user"    │
│ Model action: RESPOND (no tool call)                        │
│                                                              │
│ State: + AIMessage("Your dog sticker is ready at           │
│                     data/output/dog_resized.png!")          │
│                                                              │
│ Graph: Routes to __end__                                    │
└─────────────────────────────────────────────────────────────┘

Final state returned to user with all messages.
```

---

## Key Differences from Old AgentExecutor

### Old Way (Deprecated)

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

prompt = hub.pull("hwchase17/react")  # External dependency
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "Create a sticker"})
print(result["output"])
```

**Problems:**

- ❌ Less control over execution flow
- ❌ Harder to customize prompts
- ❌ Limited state management
- ❌ No streaming support
- ❌ External prompt dependency

### New Way (LangGraph)

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=tools,
    state_modifier="Custom system prompt..."
)

result = agent.invoke({"messages": [HumanMessage(content="Create a sticker")]})
print(result["messages"][-1].content)
```

**Benefits:**

- ✅ Full control over graph structure
- ✅ Custom prompts built-in
- ✅ Advanced state management
- ✅ Streaming support
- ✅ Better debugging
- ✅ Can customize every node
- ✅ Persistent conversation history

---

## Summary

### How LangGraph Triggers the Model:

1. **Graph Invocation**: You call `agent.invoke()`
2. **State Initialization**: Messages added to state
3. **Agent Node**: Model reads state + tools
4. **Decision**: Model chooses tool call OR final response
5. **Tool Node**: If tool called, execute and add result to state
6. **Loop**: Return to Agent Node with updated state
7. **Terminate**: When model responds without tool call

### Key Components:

- **Model**: Gemini (decision maker)
- **Tools**: Python functions with schemas
- **State**: Message history
- **Graph**: Nodes and edges defining flow
- **ReAct**: Reasoning + Acting pattern

### The Magic:

LangGraph **automatically**:

- Manages the reasoning loop
- Routes between nodes
- Validates tool calls
- Handles errors
- Maintains state
- Supports streaming

You just define:

- The model to use
- The tools to provide
- The system prompt (optional)

Everything else is handled by the graph!

---

_For implementation details, see [ARCHITECTURE.md](./ARCHITECTURE.md) and [SETUP-GUIDE.md](./SETUP-GUIDE.md)_
