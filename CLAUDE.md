# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rowboat is a multi-agent AI workflow platform that enables building AI assistants and workflows. It consists of:
- **Frontend**: Next.js 14 web app with TypeScript and Tailwind CSS
- **Backend**: Python microservices (FastAPI/Flask) for agent execution and workflow generation
- **Infrastructure**: Docker Compose orchestration with MongoDB, Redis, and Qdrant

## Essential Commands

### Starting Development

#### Option 1: Docker (Full Infrastructure)
```bash
# Set required environment variable
export OPENAI_API_KEY=your-openai-api-key

# Start all services (creates dirs, runs docker-compose)
./start.sh
```

#### Option 2: Local Development (Faster Iteration)
```bash
# Set API keys in .env file
export OPENAI_API_KEY=your-openai-api-key
export GEMINI_API_KEY=your-gemini-api-key
export ANTHROPIC_API_KEY=your-anthropic-api-key

# Start both frontend and agents service
./start_local.sh

# Or start services individually:
# Agents service: cd apps/rowboat_agents && source venv/bin/activate && python run_local.py
# Frontend: cd apps/rowboat && npm run dev
```

### Frontend Development (apps/rowboat)
```bash
npm run dev        # Development server (port 3000)
npm run build      # Production build
npm run lint       # Run linting
```

### Python Services Development

#### Local Development (Recommended)
```bash
# Rowboat Agents (apps/rowboat_agents) - Virtual Environment Approach
cd apps/rowboat_agents
python3 -m venv venv
source venv/bin/activate
pip install quart hypercorn openai google-generativeai anthropic python-dotenv pymongo redis motor qdrant-client openai-agents
python run_local.py  # Runs on port 4040

# Copilot (apps/copilot)
cd apps/copilot
pip install -r requirements.txt
python app.py
```

#### Docker Development
```bash
# Rowboat Agents (apps/rowboat_agents) - System Dependencies Approach
cd apps/rowboat_agents
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)
# Note: This approach requires resolving dependency conflicts in requirements.txt

# Copilot (apps/copilot)
cd apps/copilot
pip install -r requirements.txt
python app.py
```

### Testing
```bash
# Frontend - No test command defined, use linting
cd apps/rowboat && npm run lint

# Backend agents - Interactive testing
cd apps/rowboat_agents
python -m tests.interactive --config default_config.json --sample_request default_example.json --load_messages
```

## Architecture & Key Concepts

### Service Architecture
- **apps/rowboat**: Main UI - handles project management, chat interface, tool configuration
- **apps/rowboat_agents**: Core agent execution engine using OpenAI Agents SDK
- **apps/copilot**: AI service that generates multi-agent workflows from natural language

### Data Flow
1. User creates project and configures agents/tools in the UI
2. Chat requests go through Next.js API routes to the agents service
3. Agents service orchestrates tool calls and LLM interactions
4. Results stream back to UI via Server-Sent Events (SSE)

### Key Integration Points
- **MCP Servers**: Tools are connected via Model Context Protocol in `/app/lib/project_tools.ts`
- **RAG Pipeline**: Document processing handled by worker scripts in `/app/scripts/`
- **Authentication**: Optional Auth0 integration configured in environment variables

### Database Schema
- Projects, agents, tools, and chats stored in MongoDB
- Vector embeddings stored in Qdrant for RAG functionality
- Redis used for caching and rate limiting

## Development Notes

### AI Model Integration
Rowboat supports multiple AI providers with automatic detection:
- **OpenAI**: GPT-4o, GPT-4, GPT-3.5-turbo (default)
- **Google Gemini**: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp, gemini-2.5-pro-preview-05-06
- **Anthropic**: Claude-3.5-sonnet, Claude-3-haiku, Claude-3-opus
- **Custom Providers**: OpenRouter, LiteLLM, Azure OpenAI

Model selection is automatic based on model name patterns in agent configurations.

### Environment Configuration
- Copy `.env.example` to `.env` and configure required services
- `OPENAI_API_KEY` - Required for OpenAI models
- `GEMINI_API_KEY` - Required for Google Gemini models
- `ANTHROPIC_API_KEY` - Required for Anthropic Claude models
- `USE_RAG=true` enables document upload and processing features
- `USE_AUTH=true` enables Auth0 authentication

### Local Development Benefits
- **Faster startup**: No Docker overhead (services start in ~10 seconds vs ~2-3 minutes)
- **Better debugging**: Direct Python execution with full logging and stack traces
- **Hot reloading**: Instant code changes without container rebuilds
- **Dependency isolation**: Virtual environments prevent system conflicts
- **Multi-model testing**: Easy testing of different AI providers

### Local Development Files
- **`start_local.sh`**: Comprehensive script to start both frontend and agents service locally
- **`apps/rowboat_agents/run_local.py`**: Python script for running agents service with virtual environment
- **Virtual environment**: Isolated Python dependencies in `apps/rowboat_agents/venv/`

### Common Modifications
- **Adding new tools**: Update `/app/lib/project_tools.ts` and tool types
- **Modifying agents**: Edit graph logic in `/apps/rowboat_agents/src/graph/`
- **UI changes**: Components in `/apps/rowboat/components/`
- **AI model integration**: Modify `/apps/rowboat_agents/src/utils/common.py` for new providers

### Docker Compose Profiles
- Use `--profile qdrant` to enable vector database
- Use `--profile docs` to run documentation site
- RAG workers have individual profiles for scaling