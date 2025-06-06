#!/bin/bash

echo "🚀 Starting Rowboat Local Development Environment"
echo "================================================"

# Kill any existing services
echo "Stopping existing services..."
pkill -f "run_local.py" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in project root"
    echo "Please make sure you have a .env file with required API keys"
    exit 1
fi

echo "✅ Environment file found"

# Start agents service
echo "🤖 Starting Rowboat Agents Service (port 4040)..."
cd apps/rowboat_agents
source venv/bin/activate 2>/dev/null || {
    echo "❌ Virtual environment not found. Please run:"
    echo "   cd apps/rowboat_agents"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install quart hypercorn openai google-generativeai anthropic python-dotenv pymongo redis motor qdrant-client openai-agents"
    exit 1
}

python run_local.py &
AGENTS_PID=$!
cd ../..

# Wait for agents service to start
echo "⏳ Waiting for agents service to initialize..."
sleep 5

# Test agents service
if curl -s http://localhost:4040/health > /dev/null; then
    echo "✅ Agents service is healthy"
else
    echo "❌ Agents service failed to start"
    kill $AGENTS_PID 2>/dev/null
    exit 1
fi

# Start frontend service
echo "🖥️  Starting Frontend Service (port 3000)..."
cd apps/rowboat

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "📦 Installing frontend dependencies..."
    npm install --no-optional
fi

npm run dev &
FRONTEND_PID=$!
cd ../..

# Wait for frontend to start
echo "⏳ Waiting for frontend service to initialize..."
sleep 8

echo ""
echo "🎉 Local Development Environment Ready!"
echo "======================================"
echo "🤖 Agents Service:  http://localhost:4040"
echo "🖥️  Frontend:        http://localhost:3000"
echo "🔍 Health Check:     http://localhost:4040/health"
echo ""
echo "📝 Available Gemini Models:"
echo "   • gemini-1.5-pro"
echo "   • gemini-1.5-flash" 
echo "   • gemini-2.0-flash-exp"
echo "   • gemini-2.5-pro-preview-05-06 (latest)"
echo ""
echo "🛑 To stop services: pkill -f 'run_local.py|next dev'"
echo ""

# Keep script running to monitor services
trap 'echo "🛑 Shutting down services..."; kill $AGENTS_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

echo "🔍 Monitoring services (Ctrl+C to stop)..."
while true; do
    # Check if services are still running
    if ! kill -0 $AGENTS_PID 2>/dev/null; then
        echo "❌ Agents service stopped unexpectedly"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend service stopped unexpectedly"
        break
    fi
    sleep 5
done