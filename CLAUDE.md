# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rowboat is a multi-agent AI workflow platform that enables building AI assistants and workflows. It consists of:
- **Frontend**: Next.js 14 web app with TypeScript and Tailwind CSS
- **Backend**: Python microservices (FastAPI/Flask) for agent execution and workflow generation
- **Infrastructure**: Docker Compose orchestration with MongoDB, Redis, and Qdrant

## Essential Commands

### Starting Development
```bash
# Set required environment variable
export OPENAI_API_KEY=your-openai-api-key

# Start all services (creates dirs, runs docker-compose)
./start.sh
```

### Frontend Development (apps/rowboat)
```bash
npm run dev        # Development server (port 3000)
npm run build      # Production build
npm run lint       # Run linting
```

### Python Services Development
```bash
# Rowboat Agents (apps/rowboat_agents)
cd apps/rowboat_agents
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)
flask --app src.app.main run --port=4040

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

### Environment Configuration
- Copy `.env.example` to `.env` and configure required services
- `USE_RAG=true` enables document upload and processing features
- `USE_AUTH=true` enables Auth0 authentication

### Common Modifications
- **Adding new tools**: Update `/app/lib/project_tools.ts` and tool types
- **Modifying agents**: Edit graph logic in `/apps/rowboat_agents/src/graph/`
- **UI changes**: Components in `/apps/rowboat/components/`

### Docker Compose Profiles
- Use `--profile qdrant` to enable vector database
- Use `--profile docs` to run documentation site
- RAG workers have individual profiles for scaling