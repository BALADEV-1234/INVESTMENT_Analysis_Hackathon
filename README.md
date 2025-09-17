# INVESTMENT_Analysis_Hackathon

# Environment Variables Template
# Copy this file to .env and fill in your actual values

# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# LLM Model Selection (Optional)
LLM_MODEL=gemini-2.5-flash

# LangSmith Configuration (Optional - for tracing and monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=multi-agent-investment-analyzer
TAVILY_API_KEY=your_tavily_api_key_here

# Instructions:
# 1. Get your Google AI API key from: https://makersuite.google.com/app/apikey
# 2. Get your LangSmith API key from: https://smith.langchain.com/
# 3. Replace the placeholder values with your actual keys
# 4. Save this file as .env (remove .example extension)

##Start the Server
```
python main.py
```
#Test with a file/files
```
curl -X POST "http://localhost:8000/analyze" \
  -F "files=@tests/test_pitch.pdf"
```
