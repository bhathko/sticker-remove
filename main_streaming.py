import os
from app.agent import create_sticker_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def main():
    """
    Streaming version of the Sticker Creator Agent.
    Shows real-time progress as the agent thinks and acts.
    """
    # Ensure necessary directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    # Initialize the agent graph
    agent = create_sticker_agent()

    print("=" * 60)
    print("🎨 Sticker Creator Agent - STREAMING MODE")
    print("=" * 60)
    print("Watch the agent work in real-time!")
    print("\nType 'exit' or 'quit' to stop.")
    print("=" * 60)

    while True:
        user_input = input("\n✨ Describe your sticker: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\n👋 Goodbye!")
            break

        if not user_input.strip():
            continue

        try:
            print("\n🤖 Agent is working...\n")
            
            # Stream the agent's execution
            for event in agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": "sticker_creation_session"}},
                stream_mode="values"
            ):
                # Get the latest message
                if "messages" in event:
                    last_message = event["messages"][-1]
                    
                    # 1. Print AI Reasoning (Thought Process)
                    if last_message.type == 'ai':
                        if last_message.content:
                            print(f"\n💭 Agent: {last_message.content}")
                        
                        # 2. Print Tool Calls (Intent to act)
                        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                            for tc in last_message.tool_calls:
                                print(f"🛠️  Calling Tool: [{tc['name']}] with args: {tc['args']}")
                    
                    # 3. Print Tool Results (Observation)
                    elif last_message.type == 'tool':
                        print(f"👁️  Observation: {last_message.content}")
            
            print("\n" + "-" * 30)
            print("✅ Step Complete")
            print("-" * 30)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Tip: Make sure your GOOGLE_API_KEY is set in .env file")

if __name__ == "__main__":
    main()
