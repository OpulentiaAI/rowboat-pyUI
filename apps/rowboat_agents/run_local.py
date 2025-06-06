#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables from the main .env file
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Verify critical environment variables
required_vars = [
    'OPENAI_API_KEY', 
    'GEMINI_API_KEY', 
    'ANTHROPIC_API_KEY'
]

for var in required_vars:
    if not os.getenv(var):
        print(f"Error: {var} not found in environment variables")
        sys.exit(1)

print("Environment variables loaded successfully!")
print(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"Gemini API Key: {os.getenv('GEMINI_API_KEY')[:20]}...")
print(f"Anthropic API Key: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")

# Set the PYTHONPATH to include the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set default API key for development
os.environ['API_KEY'] = os.getenv('AGENTS_API_KEY', 'test')

# Now import and run the main app
try:
    from src.app.main import app
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    print("Starting Rowboat Agents service...")
    print("Available at: http://localhost:4040")
    print("Health check: http://localhost:4040/health")
    
    config = Config()
    config.bind = ["0.0.0.0:4040"]
    asyncio.run(serve(app, config))
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the virtual environment and all dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)