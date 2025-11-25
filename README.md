# M.A.R.S. Project 🚀

**Market Analysis & Risk Simulation** - A turn-based strategic simulation game where players manage an aerospace company operating Type 2 LEO vehicles.

## ⚡ Quick Start (Choose Your Method)

### 🐳 Docker - ZERO Dependencies Required! (RECOMMENDED)
**Works on Windows, Mac, and Linux!**

**Windows:** Double-click `start-docker.bat`  
**Mac/Linux:** Run `chmod +x start-docker.sh && ./start-docker.sh`  
**Or run:** `docker-compose up`

✅ No Python needed  
✅ No Node.js needed  
✅ Just Docker Desktop!

### 🪟 Windows Users - With Dependencies
**Double-click `start.bat`** - Requires Python & Node.js installed

**Don't have Python/Node.js?** Use Docker instead (see above) or run `check-dependencies.bat` to see what's missing.

### 🍎 Mac/Linux Users - With Dependencies
**Run:** `chmod +x start.sh && ./start.sh` - Requires Python 3.11+ & Node.js 18+ installed

**Don't have Python/Node.js?** Use Docker instead (see above) - it's the easiest option!

### 📝 Manual Setup
See detailed instructions below.

---

## 🎯 Project Overview

M.A.R.S. is a complete, production-ready business simulation game that combines market analysis, financial management, risk assessment, and environmental considerations. Players make strategic decisions about pricing, investments, technology research, and mission planning while competing in a dynamic market.

### Core Features

- **Strategic Gameplay**: Manage ticket prices, investments, and mission planning
- **Market Dynamics**: Compete with dynamic competitor pricing and market saturation
- **Tech Tree**: Unlock technologies through R&D investments (Reusable Stage 1, Green Hydrogen)
- **Environmental Impact**: Track and reduce CO2 emissions through green technology
- **Risk Management**: Contingency budgets, HR efficiency, and safety investments
- **Fleet Management**: Purchase vehicles, manage launch slots, and handle market constraints
- **Investor System**: Attract investors with randomized profiles and preferences
- **Analytics Dashboard**: Visualize performance with charts and financial metrics
- **Real-time Feedback**: Live projections showing impact of decisions before launching
- **Narrative Elements**: Contextual flavor text and dynamic news feed

## 📋 Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Charts**: Recharts
- **Deployment**: Docker-ready, supports Render, Railway, Vercel, Netlify

## 🚀 Quick Start

### Option 1: Docker - One-Click Start (Easiest) ⚡

**Windows:**
```bash
start-docker.bat
```
Or double-click `start-docker.bat` in File Explorer.

**Mac/Linux:**
```bash
chmod +x start-docker.sh
./start-docker.sh
```

**Or run directly:**
```bash
docker-compose up
```

This will:
- Build and start the backend API
- Build and start the frontend
- Make everything available at `http://localhost:3000`
- **No Python or Node.js installation needed!**

**To stop:**
```bash
docker-compose down
```

### Option 2: With Dependencies Installed

**Windows:**
```bash
start.bat
```
Or double-click `start.bat` - This will automatically start both backend and frontend servers in separate windows.

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```
This requires Python 3.11+ and Node.js 18+ to be installed.

### Option 3: Manual Setup

#### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn

#### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "M.A.R.S Project"
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

#### Running the Application

1. **Start the Backend API** (in one terminal)
   ```bash
   cd backend
   python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Frontend** (in another terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

3. **Open in Browser**
   Navigate to the frontend URL shown in the terminal

## 📁 Project Structure

```
M.A.R.S Project/
├── backend/                    # Python backend
│   ├── api.py                 # FastAPI application & endpoints
│   ├── engine.py              # Core game logic
│   ├── models.py              # Data models (GlobalConfig, GameState, PlayerInputs)
│   ├── scoring.py             # Scoring system
│   ├── financial_metrics.py   # NPV, ROI, IRR calculations
│   ├── projections.py          # Real-time projection calculations
│   ├── investor_system.py     # Investor attraction system
│   ├── news_generator.py      # News feed generation
│   ├── flavor_text.py         # Contextual flavor text
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Docker configuration
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.tsx            # Main application
│   │   ├── main.tsx           # React entry point
│   │   ├── components/        # React components
│   │   │   ├── TopBar.tsx
│   │   │   ├── ControlPanel.tsx
│   │   │   ├── ReportCardModal.tsx
│   │   │   ├── NewsTicker.tsx
│   │   │   ├── ResearchTab.tsx
│   │   │   ├── AnalyticsCharts.tsx
│   │   │   ├── FinancialDirectorTab.tsx
│   │   │   ├── InvestorTab.tsx
│   │   │   ├── MissionForecast.tsx
│   │   │   ├── Advisor.tsx
│   │   │   └── WinScreen.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
│
├── README.md                   # This file
├── Roadmap.V3.md              # Current development roadmap
└── .gitignore                 # Git ignore rules
```

## 🎮 Game Mechanics

### Mission Types

1. **Short Suborbital/Orbital Tourist**
   - Low risk (5%)
   - Revenue: €200k-€400k per passenger
   - High volume potential (up to 7 passengers)

2. **Long Orbital Stay (Tourist)**
   - Medium risk (15%)
   - Revenue: €5M-€10M per passenger
   - Requires Safety Tech Level 5 to unlock

3. **Scientific/Industrial**
   - High risk (25%)
   - Fixed contract value (€1M-€100M)
   - Bonus R&D points on success

### Investment Options

- **Marketing**: Increases reputation and demand
- **Safety Investment**: Reduces mission failure risk
- **Green Investment**: Reduces CO2 impact and variable costs
- **R&D Investment**: Unlocks technologies (Reusable Stage 1, Green Hydrogen)
- **HR & Training**: Improves efficiency and can save failed missions
- **Contingency Budget**: Mitigates failure penalties

### Technology Tree

- **Reusable Stage 1** (Tech Level 10): Reduces launch costs by 20%
- **Green Hydrogen** (Tech Level 20): Reduces CO2 emissions by 50%

### Investor System

- **Randomized Investors**: Each offer attracts a random investor with unique preferences
- **Investor Types**:
  - 👩‍⚕️ Safety-focused (Doctors, Engineers) - Value high safety tech
  - 🌱 Environmental (Activists, Scientists) - Value low CO2 impact
  - 💻 Tech-focused (Entrepreneurs) - Value high tech levels
  - 💰 Financial (Bankers, VCs) - Value high reputation
  - ⚖️ Balanced - Consider multiple factors
- **Reputation Impact**: Accepted offers increase reputation, rejected offers decrease it

### Financial Metrics

- **NPV (Net Present Value)**: Discounted cash flow analysis
- **ROI (Return on Investment)**: Cumulative profit / total investment
- **IRR (Internal Rate of Return)**: Breakeven interest rate

## 🔌 API Endpoints

### Game Management

- `POST /start_game` - Initialize a new game
- `GET /state` - Get current game state
- `POST /play_turn` - Execute a turn with player inputs
- `GET /final_score` - Get final game score

### Real-time Features

- `POST /projected_stats` - Get projected stats for current inputs
- `GET /news_feed` - Get news feed with competitor prices and jokes
- `GET /investor_offer_chance` - Calculate investor offer acceptance chance
- `POST /make_investor_offer` - Process an investor offer immediately
- `GET /financial_metrics` - Get NPV, ROI, IRR metrics

### Request/Response Examples

**Start Game:**
```json
POST /start_game
Response: {
  "message": "Game started successfully",
  "state": { "budget": 500000000, "reputation": 50.0, ... }
}
```

**Play Turn:**
```json
POST /play_turn
Body: {
  "mission_type": "Short_Suborbital",
  "ticket_price": 300000,
  "marketing_spend": 5000000,
  "safety_invest": 10000000,
  "green_invest": 3000000,
  "rd_invest": 8000000,
  "hr_invest": 0,
  "contingency_budget": 0,
  "buy_vehicle": false,
  "investor_offer": 0
}
```

## 🎯 Game Strategy

### Cost Management

- **Fixed Costs**: €5M per turn (constant)
- **Variable Costs**: Base €35M (€15M fuel + €20M launch)
  - Reduced by Green Tech (-1% per level)
  - Reduced by Reusable Stage 1 (-20%)
  - Reduced by HR Efficiency

### Winning Strategies

1. **Balance Risk and Reward**: Higher risk missions offer better returns but require more safety investment
2. **Invest in Technology**: Unlock Reusable Stage 1 early to reduce costs
3. **Build Reputation**: Marketing and successful missions increase reputation, improving demand
4. **Manage Contingency**: Keep reserves for mission failures
5. **Expand Fleet**: More vehicles = more missions per turn
6. **Target Investors**: Match investor preferences to your company's strengths

## 🐳 Docker Deployment

### Quick Start with Docker Compose

The easiest way to run the entire application:

```bash
docker-compose up
```

This will:
- Build both backend and frontend containers
- Start the backend API on port 8000
- Start the frontend on port 3000
- Handle all dependencies automatically

**To stop:**
```bash
docker-compose down
```

**To rebuild after changes:**
```bash
docker-compose up --build
```

### Individual Docker Containers

**Backend only:**
```bash
cd backend
docker build -t mars-backend .
docker run -p 8000:8000 mars-backend
```

**Frontend only:**
```bash
cd frontend
docker build -t mars-frontend .
docker run -p 3000:3000 mars-frontend
```

## 📊 Deployment Options

### Backend (FastAPI)

- **Render**: Web Service, auto-deploy from Git
- **Railway**: Simple deployment with automatic builds
- **Heroku**: Traditional PaaS option
- **AWS/GCP/Azure**: Full cloud control

### Frontend (React/Vite)

- **Vercel**: Optimized for React, automatic deployments
- **Netlify**: Easy static site hosting
- **GitHub Pages**: Free hosting for static sites
- **AWS S3 + CloudFront**: Scalable CDN solution

## 🧪 Development

### Backend Development

```bash
cd backend
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Note**: Make sure you're in the `backend/` directory when running the server.

### Frontend Development

```bash
cd frontend
npm run dev
```

### Building for Production

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Server runs with: python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

## 📝 Key Game Constants

- **Starting Budget**: €500M
- **Starting Reputation**: 50/100
- **Max Passengers**: 7 per mission
- **Vehicle Cost**: €150M
- **Vehicle Build Time**: 1 turn
- **Base Available Slots**: 3 per turn
- **Max Years**: 10
- **Bankruptcy Threshold**: €0

## 🎓 Educational Value

This project demonstrates:
- **Business Strategy**: Market analysis, pricing, investment decisions
- **Financial Management**: NPV, ROI, IRR calculations
- **Risk Management**: Contingency planning, failure mitigation
- **Technology Management**: R&D investment, tech tree progression
- **Environmental Responsibility**: CO2 tracking and reduction
- **Full-Stack Development**: React frontend + FastAPI backend
- **API Design**: RESTful endpoints with proper error handling

## 📄 License

This project is part of the PoliTOrbital M.A.R.S. Project.

## 🤝 Contributing

This is a project for the PoliTOrbital competition. For questions or issues, please refer to the project documentation.

## 📚 Additional Resources

- **Roadmap**: See `Roadmap.V3.md` for current development plans
- **API Documentation**: Available at `http://localhost:8000/docs` when backend is running (Swagger UI)

---

**Status**: ✅ Production Ready - All features implemented and tested
