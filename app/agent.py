from langgraph.prebuilt import create_react_agent
from app.model import get_gemini_model
from app.tools.sticker_tool import (
    generate_image_tool, 
    check_background_tool, 
    remove_background_tool, 
    resize_image_tool,
    image_to_image_tool,
    read_prompt_file_tool
)

def create_sticker_agent():
    """
    Creates and returns a LangGraph agent specialized in sticker creation.
    Uses the new LangGraph method which returns a compiled graph directly.
    
    The agent follows this workflow:
    1. Generate image (from text OR base image + text)
    2. Check if background removal is needed
    3. Remove background if necessary
    4. Resize to standard sticker dimensions (370x320)
    """
    # Initialize Tools
    tools = [
        generate_image_tool,
        check_background_tool,
        remove_background_tool,
        resize_image_tool,
        image_to_image_tool,
        read_prompt_file_tool
    ]

    # Initialize Model
    llm = get_gemini_model()

    # Create the ReAct agent graph (new LangGraph method)
    # The agent automatically handles tool calling and reasoning
    agent_graph = create_react_agent(
        model=llm, 
        tools=tools,
        prompt="""You are an expert sticker creation assistant. You MUST complete ALL steps below for EVERY request — never stop after just one step.

Workflow (execute ALL steps in order):
0. READ PROMPT FILE (if applicable): If the user mentions a JSON file or prompt file, call 'read_prompt_file' FIRST to parse it. Then use the parsed output to call the appropriate generation tool.
1. GENERATE: Create the image.
   - Use 'generate_image' for text-to-image requests.
   - Use 'image_to_image' when the user provides a local base image.
2. CHECK BACKGROUND: After generating, ALWAYS call 'check_image_background' on the generated image.
3. REMOVE BACKGROUND: If the check returns 'has_background', call 'remove_background' on the image.
4. RESIZE: ALWAYS call 'resize_for_sticker' on the final image (after background removal if it was needed, or directly on the generated image if it was already transparent).

CRITICAL RULES:
- You MUST call all tools in sequence. Do NOT stop after generating the image.
- After each tool call, immediately proceed to the next step.
- If a user mentions a .json file, ALWAYS call 'read_prompt_file' first.
- If a user mentions a local file, assume it is in the 'data/input' directory unless specified otherwise.
- JSON prompt files are in the 'data/prompts' directory by default.
- Use the file path returned by each tool as input for the next tool.
- Be concise in your responses."""
    )

    return agent_graph
