# AI Investment Analyst Platform (VentureIQ)

Multi-Agent system for comprehensive startup evaluation using Google AI and web intelligence with modern dashboard interface.

## 🚀 Key Features

### 🤖 Multi-Agent Architecture
- **Pitch Deck Agent**: Analyzes business models and presentations
- **Data Room Agent**: Evaluates financial metrics and traction
- **Web Content Agent**: Performs competitive intelligence with Tavily search
- **Interaction Agent**: Assesses founder quality from calls/transcripts
- **Aggregator Agent**: Synthesizes insights and generates scores
- **Question Generator**: Creates targeted due diligence questions

### 📊 Investment Scoring Framework
- **Team (25%)**: Founder-market fit, technical execution, prior outcomes
- **Market (25%)**: TAM/SAM/SOM, growth indicators, competitive intensity
- **Product (20%)**: Differentiation, UX, technical defensibility
- **Traction (20%)**: Growth metrics, retention, sales efficiency
- **Financials (5%)**: Runway, burn rate, capital efficiency
- **Moat (5%)**: Network effects, data advantages, regulatory barriers

### 🔍 Enhanced Web Intelligence
- **Real-time web search** powered by Tavily API
- Company verification and registration lookup
- Funding history and investor signals
- Product reviews and customer feedback
- Competitive landscape analysis
- Hiring velocity and talent signals
- Social proof and media coverage
- Market validation data

### 💾 Analysis Storage & Persistence
- **Local JSON-based storage** in `data/analyses/`
- Automatic saving of all analyses
- Browse and retrieve past analyses
- Search and filter saved reports
- Storage statistics and management
- Export capabilities

### 🎨 Modern Dashboard (VentureIQ)
- **Professional dark-themed UI** inspired by modern AI tools
- Real-time analysis progress tracking
- Interactive visualizations with Plotly
- Multiple file upload support
- Saved analyses browser
- Responsive design
- Color-coded scoring displays
- Collapsible sections for detailed insights

### ❓ Founder Question Generation
- Priority-ranked interview questions
- Domain-specific technical queries
- Vision and alignment assessment
- Risk mitigation probes
- Gap analysis based on missing data

## 📋 Prerequisites

### Required API Keys
```bash
# Add these to .env file
GOOGLE_API_KEY=your_google_api_key          # Required for Gemini AI
TAVILY_API_KEY=your_tavily_api_key          # Required for web search
LANGSMITH_API_KEY=your_langsmith_key        # Optional - for tracing
```

### System Requirements
- Python 3.10+
- 2GB+ RAM
- Internet connection for API access

## 🔧 Installation

### Option 1: Local Setup

```bash
# Clone the repository
git clone <repo-url>
cd INVESTMENT_Analysis_Hackathon

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run both backend and frontend together
make run-all

# OR run separately:
# Terminal 1 - Backend API
make run-backend

# Terminal 2 - Dashboard UI
make run-frontend
```

### Option 2: Docker Deployment

```bash
# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📱 Usage

### Web Dashboard (Recommended)

1. **Open Dashboard**: Navigate to http://localhost:8050
2. **Upload Files**: Drag and drop or click to upload startup materials
   - Supported formats: PDF, XLSX, PPTX, DOCX, TXT, CSV
   - Multiple file upload supported
3. **Start Analysis**: Click "Start Analysis" button
4. **View Results**: See comprehensive analysis with:
   - Overall investment score
   - Detailed agent analyses
   - Web intelligence insights
   - Founder questions
   - Visual score breakdowns
5. **Browse History**: Access previously saved analyses from sidebar

### API Endpoints

#### 1. Full Analysis
Complete investment evaluation with all agents and web search.

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "files=@pitch_deck.pdf" \
  -F "files=@financials.xlsx" \
  -F "files=@data_room.xlsx"
```

**Response includes:**
- Investment scores (0-100 scale)
- Specialized agent analyses
- Web intelligence data
- Founder questions
- Confidence scores
- Auto-saved to storage

#### 2. Quick Summary
Fast executive summary without detailed scoring.

```bash
curl -X POST "http://localhost:8000/summary" \
  -F "files=@pitch_deck.pdf"
```

#### 3. Investment Scoring
Focused scoring analysis with KPI breakdown.

```bash
curl -X POST "http://localhost:8000/scoring" \
  -F "files=@pitch_deck.pdf" \
  -F "files=@financials.xlsx"
```

**Returns:**
- Detailed scores by category
- Rationale for each score
- Overall investment grade

#### 4. Founder Questions
Generate targeted due diligence questions.

```bash
curl -X POST "http://localhost:8000/questions" \
  -F "files=@pitch_deck.pdf"
```

**Output:**
- Priority-ranked questions
- Category-specific queries
- Gap analysis insights

#### 5. Storage Management

**List All Analyses**
```bash
curl -X GET "http://localhost:8000/analyses"
```

**Get Specific Analysis**
```bash
curl -X GET "http://localhost:8000/analyses/{analysis_id}"
```

**Delete Analysis**
```bash
curl -X DELETE "http://localhost:8000/analyses/{analysis_id}"
```

**Storage Statistics**
```bash
curl -X GET "http://localhost:8000/storage/stats"
```

#### 6. Health & Status

**Health Check**
```bash
curl -X GET "http://localhost:8000/health"
```

**Agent Status**
```bash
curl -X GET "http://localhost:8000/agents"
```

## 📂 Project Structure

```
INVESTMENT_Analysis_Hackathon/
├── main.py                              # FastAPI backend server
├── dashboard.py                         # Dash frontend application
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # Docker configuration
├── Makefile                             # Build and run commands
├── .env                                 # Environment variables (create from .env.example)
├── data/                                # Storage directory
│   └── analyses/                        # Saved analysis results
│       ├── index.json                   # Analysis index
│       └── {company_name}_{id}.json     # Individual analyses
└── src/
    ├── agents/                          # Specialized AI agents
    │   ├── base_agent.py
    │   ├── enhanced_web_content_agent.py
    │   ├── enhanced_aggregator_agent.py
    │   └── founder_question_agent.py
    ├── core/
    │   └── enhanced_multi_agent_orchestrator.py
    ├── storage/
    │   ├── __init__.py
    │   └── analysis_storage.py          # Storage management
    └── utils/
        └── file_processor.py             # File handling utilities
```

## 🔑 Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=investment-analyzer
LLM_MODEL=gemini-2.0-flash-exp

# API Configuration
API_URL=http://localhost:8000
```

## 🎯 Analysis Types Explained

### Full Analysis (Default)
- All agents activated
- Complete web search integration
- Investment scoring
- Founder questions
- ~5-10 minutes processing time

### Summary Mode
- Quick executive overview
- Key insights extraction
- No detailed scoring
- ~2-3 minutes processing time

### Scoring Mode
- Focus on investment metrics
- Detailed KPI breakdown
- Category-wise scoring
- ~3-5 minutes processing time

### Questions Mode
- Targeted due diligence questions
- Gap analysis
- Risk identification
- ~2-4 minutes processing time

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 8050 (frontend)
lsof -ti:8050 | xargs kill -9
```

### Missing API Keys
- Ensure `.env` file exists in project root
- Verify all required keys are set
- Check for typos in variable names

### Web Search Not Working
- Verify `TAVILY_API_KEY` is set correctly
- Check internet connectivity
- Review backend logs for API errors

### Analysis Fails
- Check file format compatibility
- Ensure files are not corrupted
- Review backend logs: `docker-compose logs backend`
- Try with smaller/simpler files first

### Dashboard Issues
```bash
# Clear browser cache
# Check browser console for errors
# Verify backend is running: curl http://localhost:8000/health
```

## 🚀 Performance Tips

1. **Use multiple files** for better analysis quality
2. **Include financials** for accurate scoring
3. **Provide context** in file names (e.g., `Q3_2024_financials.xlsx`)
4. **Optimize file sizes** - compress large PDFs
5. **Use Summary mode** for quick checks
6. **Enable LangSmith** for debugging and optimization

## 📊 Scoring Methodology

Scores are calculated using a weighted framework:

- **0-40**: High Risk - Significant concerns
- **40-60**: Medium Risk - Needs improvement
- **60-75**: Moderate Potential - Worth consideration
- **75-85**: Strong Potential - Recommended
- **85-100**: Exceptional - Highly recommended

Confidence scores indicate data quality and completeness.

## 🔐 Security Notes

- API keys stored in `.env` (not committed to git)
- Local storage only (no cloud uploads)
- All analysis data stays on your machine
- Files processed in memory, not permanently stored

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google Gemini** for AI capabilities
- **Tavily** for web search intelligence
- **Dash/Plotly** for visualization framework
- **FastAPI** for backend infrastructure
- **LangSmith** for observability

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Check `/docs` endpoint when backend is running
- **API Docs**: Visit http://localhost:8000/docs for interactive API documentation

---

Built with ❤️ for smarter investment decisions
