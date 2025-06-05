# 🚀 Gemini Models Integration

Google's Gemini models are now fully integrated into your Rowboat application! This guide shows you how to use them.

## ✅ What's Already Set Up

Your environment has been configured with:

1. **API Key**: `GEMINI_API_KEY` is configured in your `.env` file
2. **Backend Support**: Agents service can automatically detect and use Gemini models
3. **Dependencies**: All required packages are installed and configured
4. **Docker**: Environment variables are configured for containerized deployment

## 🎯 Available Gemini Models

You can use any of these Gemini model names in your agent configurations:

### 🌟 Latest & Most Advanced
- `gemini-2.5-pro-preview-05-06` - **Latest model!** Best for coding, reasoning, and multimodal understanding

### 🚀 Stable Models  
- `gemini-1.5-pro` - Most capable stable model, best for complex reasoning
- `gemini-1.5-flash` - Fastest model, great for most tasks

### 🧪 Experimental Models
- `gemini-2.0-flash-exp` - Experimental model with latest features
- `gemini-2.0-flash-thinking-exp` - Experimental thinking model

### 💰 Pricing (API costs)
- **Gemini 2.5 Pro Preview**: $1.25/$10 per 1M tokens (input/output, ≤200K) 
- **Standard models**: More cost-effective for high-volume use

## 🛠️ How to Use Gemini Models

### 1. In the Web UI

1. Go to your project
2. Click on any agent to edit it
3. In the "Configurations" tab, change the **Model** field to any Gemini model:
   ```
   gemini-2.5-pro-preview-05-06
   ```
   (or use `gemini-1.5-flash` for faster/cheaper responses)
4. Save the agent
5. The agent will now use Gemini instead of OpenAI!

### 2. Model Detection

The system automatically detects the provider based on the model name:
- Models containing "gemini" → Google Gemini API
- Models containing "gpt" → OpenAI API  
- Models containing "claude" → Anthropic API

### 3. Example Agent Configurations

**For Advanced Coding Tasks:**
```json
{
  "name": "Advanced Coding Assistant",
  "model": "gemini-2.5-pro-preview-05-06",
  "instructions": "You are an expert programming assistant powered by Gemini 2.5 Pro Preview. Excel at code generation, debugging, architecture design, and complex reasoning...",
  "outputVisibility": "user_facing"
}
```

**For General Tasks (Faster/Cheaper):**
```json
{
  "name": "Gemini Assistant",
  "model": "gemini-1.5-flash",
  "instructions": "You are a helpful AI assistant powered by Google's Gemini model...",
  "outputVisibility": "user_facing"
}
```

## 🔧 Technical Details

### Message Format Conversion
The integration automatically handles message format conversion:
- OpenAI-style messages → Gemini format
- System messages → Prepended to first user message
- Assistant messages → Model role in Gemini

### Environment Variables
```bash
# Required for Gemini models
GEMINI_API_KEY=your_api_key_here

# Optional: Also supports Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Backend Code
The agents service in `apps/rowboat_agents/src/utils/common.py` includes:
- `generate_gemini_output()` - Direct Gemini API calls
- `generate_llm_output()` - Universal function with auto-detection
- Error handling and retry logic

## 🐳 Docker Deployment

For production deployment, the Docker containers are already configured with the necessary environment variables and dependencies.

To rebuild and start services:
```bash
./start.sh
```

## ✨ Quick Start Templates

New templates available in the project creation flow:

1. **"Gemini AI Assistant"** - Uses `gemini-1.5-flash` for general tasks
2. **"Advanced Coding Assistant"** - Uses `gemini-2.5-pro-preview-05-06` for development work

### 🎯 Use Cases for Gemini 2.5 Pro Preview:
- **Software Development**: Code generation, refactoring, debugging
- **Code Reviews**: Analyze and suggest improvements
- **Architecture Design**: System design and technical planning  
- **Complex Reasoning**: Multi-step problem solving
- **Multimodal Tasks**: Understanding code with images/diagrams

## 🚨 Troubleshooting

### Common Issues:

1. **API Key Error**: Ensure `GEMINI_API_KEY` is set in your `.env` file
2. **Import Error**: Make sure `google-generativeai` package is installed
3. **Docker Issues**: Rebuild containers if you're using Docker deployment

### Test Your Setup:

Run this command to verify Gemini integration:
```bash
cd apps/rowboat_agents
source venv/bin/activate
python3 -c "from src.utils.common import generate_gemini_output; print('✅ Gemini ready!')"
```

## 🎉 Next Steps

1. Create a new project or edit an existing agent
2. Set the model to `gemini-1.5-flash` or `gemini-1.5-pro`
3. Test your agent in the playground
4. Enjoy the power of Google's latest AI models!

---

**Need help?** Check the main documentation or create an issue in the repository.