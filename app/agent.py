from langgraph.prebuilt import create_react_agent
from app.model import get_gemini_model
from app.tools.sticker_tool import (
    generate_image_tool, 
    check_background_tool, 
    remove_background_tool, 
    resize_image_tool
)

def create_sticker_agent():
    """
    Creates and returns a LangGraph agent specialized in sticker creation.
    Uses the new LangGraph method which returns a compiled graph directly.
    
    The agent follows this workflow:
    1. Generate image from prompt using Gemini Imagen API
    2. Check if background removal is needed
    3. Remove background if necessary
    4. Resize to standard sticker dimensions (370x320)
    """
    # Initialize Tools
    tools = [
        generate_image_tool,
        check_background_tool,
        remove_background_tool,
        resize_image_tool
    ]

    # Initialize Model
    llm = get_gemini_model()

    # Create the ReAct agent graph (new LangGraph method)
    # The agent automatically handles tool calling and reasoning
    agent_graph = create_react_agent(
        model=llm, 
        tools=tools,
        prompt="""You are an expert sticker creation assistant. Your job is to help users create professional stickers by:
1. Generating images from text prompts using the generate_image tool
2. Checking if the generated image needs background removal
3. Removing backgrounds when needed for clean transparent stickers
4. Resizing the final image to standard sticker dimensions (370x320px)

Always follow this workflow in order. Be concise in your responses and focus on the task at hand."""
    )

    return agent_graph
