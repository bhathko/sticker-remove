import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_gemini_model(model_name="gemini-1.5-flash"):
    """
    Initializes and returns the Gemini Chat Model.
    Ensure GOOGLE_API_KEY is set in your .env file.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY not found in environment.")
        
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        convert_system_message_to_human=True
    )
