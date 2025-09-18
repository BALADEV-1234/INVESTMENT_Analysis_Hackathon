# README.md
# AI Investment Analyst Platform

Multi-Agent system for comprehensive startup evaluation using Google AI and web intelligence.

## Features

### 🤖 Multi-Agent Architecture
- **Pitch Deck Agent**: Analyzes business models and presentations
- **Data Room Agent**: Evaluates financial metrics and traction
- **Web Content Agent**: Performs competitive intelligence with Tavily search
- **Interaction Agent**: Assesses founder quality from calls/transcripts
- **Aggregator Agent**: Synthesizes insights and generates scores
- **Question Generator**: Creates targeted due diligence questions

### 📊 Scoring Framework
- Team (25%): Founder-market fit, technical execution, prior outcomes
- Market (25%): TAM/SAM/SOM, growth indicators, competitive intensity
- Product (20%): Differentiation, UX, technical defensibility
- Traction (20%): Growth metrics, retention, sales efficiency
- Financials (5%): Runway, burn rate, capital efficiency
- Moat (5%): Network effects, data advantages, regulatory barriers

### 🔍 Web Intelligence
- Company verification and registration
- Funding history and investor signals
- Product reviews and customer feedback
- Competitive landscape analysis
- Hiring velocity and talent signals
- Social proof and media coverage

### ❓ Founder Questions
- Priority-ranked interview questions
- Domain-specific technical queries
- Vision and alignment assessment
- Risk mitigation probes

## Quick Start

### Prerequisites
```bash
# Required API Keys (add to .env file)
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key  # For web search
LANGSMITH_API_KEY=your_langsmith_key  # Optional tracing
```

### Installation

#### Option 1: Local Setup
```bash
# Clone the repository
git clone <repo-url>
cd investment-analyst

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run backend
make run-backend

# In another terminal, run frontend
make run-frontend

# Or run both together
make run-all
```

#### Option 2: Docker
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Usage

### Web Dashboard (Recommended)
1. Open http://localhost:8050 in your browser
2. Upload startup materials (PDF, XLSX, PPTX, etc.)
3. Select analysis type (Full/Summary/Scoring/Questions)
4. Click "Analyze Startup"
5. View comprehensive results with scores and visualizations

### API Endpoints

#### Full Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "files=@pitch_deck.pdf" \
  -F "files=@financials.xlsx"
```

#### Summary Only
```bash
curl -X POST "http://localhost:8000/summary" \
  -F "files=@pitch_deck.pdf"
```

#### Investment Scoring
```bash
curl -X POST "http://localhost:8000/scoring" \
  -F "files=@