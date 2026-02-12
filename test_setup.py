#!/usr/bin/env python3
"""
Quick validation script to check if the project is properly configured
and using the latest LangGraph patterns.
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed."""
    print("🔍 Testing imports...")
    
    try:
        import langchain
        import langchain_core
        import langchain_google_genai
        import langgraph
        from langgraph.prebuilt import create_react_agent
        print("✅ LangChain packages installed correctly")
    except ImportError as e:
        print(f"❌ LangChain import error: {e}")
        return False
    
    try:
        import transformers
        import PIL
        import torch
        import cv2
        import numpy as np
        print("✅ ML/Image processing packages installed correctly")
    except ImportError as e:
        print(f"❌ ML package import error: {e}")
        return False
    
    try:
        from app.agent import create_sticker_agent
        from app.model import get_gemini_model
        from app.tools.sticker_tool import (
            generate_image_tool,
            check_background_tool,
            remove_background_tool,
            resize_image_tool,
            image_to_image_tool
        )
        from app.services.processor import StickerProcessor
        print("✅ Project modules imported successfully")
    except ImportError as e:
        print(f"❌ Project import error: {e}")
        return False
    
    try:
        import google.genai
        print("✅ Official Google GenAI (Nano Banana) package installed")
    except ImportError as e:
        print(f"❌ Google GenAI import error: {e}")
        return False
    
    return True

def test_environment():
    """Check environment variables."""
    print("\n🔍 Testing environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if google_key and google_key != "your_google_api_key_here":
        print("✅ GOOGLE_API_KEY is configured")
    else:
        print("⚠️  GOOGLE_API_KEY not configured (image generation will use fallback)")
    
    return True

def test_directories():
    """Check if required directories exist."""
    print("\n🔍 Testing directory structure...")
    
    required_dirs = ["data/input", "data/output"]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} exists")
        else:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ {dir_path} created")
    
    return True

def test_agent_creation():
    """Test if agent can be created with new LangGraph pattern."""
    print("\n🔍 Testing agent creation...")
    
    try:
        from app.agent import create_sticker_agent
        agent = create_sticker_agent()
        
        # Check if it's a graph (new pattern)
        if hasattr(agent, 'invoke') and hasattr(agent, 'stream'):
            print("✅ Agent created successfully using LangGraph pattern")
            print("✅ Agent supports invoke() method")
            print("✅ Agent supports stream() method")
            return True
        else:
            print("❌ Agent doesn't have expected LangGraph methods")
            return False
            
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_processor():
    """Test if processor methods are properly defined."""
    print("\n🔍 Testing StickerProcessor class...")
    
    try:
        from app.services.processor import StickerProcessor
        processor = StickerProcessor()
        
        # Check if all methods exist and are callable
        methods = ['generate_image', 'remove_background', 'resize_image', 'has_transparency']
        for method_name in methods:
            if hasattr(processor, method_name) and callable(getattr(processor, method_name)):
                print(f"✅ {method_name}() method exists and is callable")
            else:
                print(f"❌ {method_name}() method missing or not callable")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Processor test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Sticker Creator Project Validation")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Config", test_environment),
        ("Directory Structure", test_directories),
        ("Agent Creation (LangGraph)", test_agent_creation),
        ("Processor Methods", test_processor),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n🎉 All tests passed! Project is properly configured.")
        print("\n🚀 You can now run:")
        print("   python main.py              # Standard mode")
        print("   python main_streaming.py    # Streaming mode")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common fixes:")
        print("   pip install -r requirements.txt")
        print("   cp .env.example .env")
        print("   # Edit .env with your GOOGLE_API_KEY")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
