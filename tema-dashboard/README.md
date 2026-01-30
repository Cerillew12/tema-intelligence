# Tema ETF Competitive Intelligence Dashboard - Enhanced Edition

## 🎯 Overview

This enhanced dashboard provides:
1. ✅ **Accurate AUM data** - Direct from Tema's official website
2. ✅ **Monthly net flows** - Previous calendar month flow tracking
3. ✅ **Market share analysis** - Tema funds vs. competitors comparison
4. ✅ **Real-time updates** - Automated daily data refresh
5. ✅ **Professional UI** - Modern, responsive design

## 📁 Project Structure

```
tema-dashboard/
├── backend/
│   ├── api_server.py           # Flask API server
│   ├── fetch_tema_data.py      # Scrapes Tema website
│   ├── fetch_competitor_data.py # Fetches competitor data
│   └── requirements.txt        # Python dependencies
├── frontend/
│   └── index.html              # Dashboard UI
├── data/
│   ├── tema_funds.json         # Cached Tema data
│   ├── competitor_funds.json   # Cached competitor data
│   └── market_share.json       # Market share calculations
├── vercel.json                 # Vercel deployment config
├── railway.json                # Railway deployment config
└── README.md                   # This file
```

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 16+ (optional, for frontend development)

### Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Fetch initial data:**
```bash
python fetch_tema_data.py
python fetch_competitor_data.py
```

3. **Start the API server:**
```bash
python api_server.py
```
Server will run at `http://localhost:5000`

4. **Open the frontend:**
```bash
cd ../frontend
# Open index.html in browser or use live server
python -m http.server 8000
```
Dashboard will be at `http://localhost:8000`

## 🌐 Deployment Options

### Option 1: Vercel (Recommended for Simplicity)

**Steps:**
1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd tema-dashboard
vercel
```

3. Follow prompts to link to your GitHub repo

**Pros:** 
- Free tier available
- Automatic deployments from GitHub
- Global CDN
- Serverless functions included

**Cons:**
- Limited execution time for functions (10s on free tier)

### Option 2: Railway (Recommended for Backend)

**Steps:**
1. Create account at [railway.app](https://railway.app)

2. Install Railway CLI:
```bash
npm install -g @railway/cli
```

3. Deploy:
```bash
railway init
railway up
```

4. Set environment variables in Railway dashboard

**Pros:**
- Free $5/month credit
- Persistent backend
- Easy database integration
- Good for scheduled tasks

**Cons:**
- Credit limits on free tier

### Option 3: GitHub Pages + External Backend

**Frontend (GitHub Pages):**
1. Push frontend folder to GitHub repo
2. Go to Settings > Pages
3. Select branch and `/frontend` folder
4. Site published at `https://yourusername.github.io/repo-name/`

**Backend (Railway/Render):**
- Deploy backend separately using Railway or Render
- Update frontend API_BASE_URL to point to backend

**Pros:**
- Free frontend hosting
- Decoupled architecture
- Easy version control

**Cons:**
- Need to manage two deployments

## ⚙️ Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# API Keys (if using paid data sources)
ALPHA_VANTAGE_KEY=your-key-here
ETF_COM_API_KEY=your-key-here

# Database (optional)
DATABASE_URL=postgresql://...

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://stevemunroe.github.io
```

### Data Sources

The system is configured with multiple data sources:

**Tema Funds (Primary):**
- Source: temaetfs.com (official website)
- Method: Web scraping
- Update frequency: Daily at 5 PM ET
- ✅ Most accurate

**Competitor Funds:**
- Source: Yahoo Finance (free)
- Fallback: Manual JSON updates
- Method: yfinance library
- ⚠️ May have delays

**Flow Data:**
- ⚠️ **REQUIRES MANUAL INPUT OR PAID API**
- Recommended: ETF.com API (paid)
- Alternative: Bloomberg Terminal
- Workaround: Manual CSV upload

## 📊 Data Update Process

### Automated (Daily)
The backend runs scheduled tasks:
- 5:00 PM ET: Fetch Tema website data
- 5:15 PM ET: Fetch competitor data
- 5:30 PM ET: Calculate market share
- 5:45 PM ET: Cache results

### Manual Refresh
Click "Refresh Data" button in dashboard or:
```bash
curl -X POST http://your-api-url/api/refresh
```

## 🔧 Customization

### Adding New Competitors

Edit `backend/fetch_competitor_data.py`:

```python
COMPETITORS = {
    'VOLT': ['GRID', 'URNM', 'URA', 'NLR', 'YOUR_NEW_TICKER'],
    # ... other funds
}
```

### Changing Update Schedule

Edit `backend/api_server.py`:

```python
# Change from 5 PM to 6 PM
schedule.every().day.at("18:00").do(api_handler.refresh_data)
```

### Styling

Edit `frontend/index.html` CSS section to match your brand colors.

## 🚨 Known Limitations & Required Manual Work

### 1. Flow Data ⚠️ **ACTION REQUIRED**
**Problem:** Monthly flow data requires paid API access

**Solutions:**
- **Option A (Recommended):** Subscribe to ETF.com API ($99/month)
- **Option B:** Use Bloomberg Terminal (if available)
- **Option C:** Manual CSV upload monthly

**Implementation for Option C:**
1. Create `/data/manual_flows.json`:
```json
{
  "VOLT": {
    "flows_prev_month": 15200000,
    "flows_ytd": 85000000,
    "as_of_date": "2026-12-31"
  }
}
```

2. Update monthly after market data available

### 2. Competitor AUM Accuracy ⚠️ **ACTION REQUIRED**
**Problem:** Yahoo Finance data can be delayed

**Solutions:**
- Verify quarterly against official fund websites
- Consider paid data feed (Morningstar, FactSet)
- Implement manual override system

### 3. Real-time Price Updates
**Current:** Data updates daily at 5 PM
**For real-time:** Need WebSocket connection or paid API

### 4. Historical Data
**Current:** No historical tracking
**To add:** Implement database storage (PostgreSQL on Railway)

## 📈 Future Enhancements

### Phase 2 Features
- [ ] Historical flow tracking (database required)
- [ ] Automated email alerts for significant changes
- [ ] PDF report generation
- [ ] Excel export functionality
- [ ] Mobile app version

### Phase 3 Features
- [ ] Predictive analytics
- [ ] Competitor benchmarking scores
- [ ] Social sentiment analysis
- [ ] Integration with CRM systems

## 🐛 Troubleshooting

### Data Not Loading
1. Check API server is running: `curl http://localhost:5000/api/health`
2. Check CORS settings if frontend on different domain
3. Verify data files exist in `/data` folder

### Incorrect AUM Values
1. Run manual data fetch: `python fetch_tema_data.py`
2. Check Tema website HTML structure hasn't changed
3. Update scraping selectors if needed

### Flow Data Missing
1. This is expected - flow data requires manual input or paid API
2. See "Flow Data" section above for solutions

## 📞 Support & Contributions

### Getting Help
- Check logs: `tail -f /var/log/tema-dashboard.log`
- API health: `GET /api/health`
- Test endpoint: `GET /api/tema-funds`

### Contributing
1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License

MIT License - See LICENSE file

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Beautiful Soup Web Scraping](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Vercel Deployment Guide](https://vercel.com/docs)

---

**Built with ❤️ for Tema ETFs competitive analysis**

Last Updated: January 2026
