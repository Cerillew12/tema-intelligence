"""
Tema Dashboard API Server
Flask backend to serve ETF data to the frontend dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import schedule
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

DATA_DIR = '/home/claude/tema-dashboard/data'

class DashboardAPI:
    """API handler for dashboard data"""
    
    def __init__(self):
        self.tema_data = []
        self.competitor_data = {}
        self.market_share = {}
        self.last_updated = None
    
    def load_data(self):
        """Load data from JSON files"""
        try:
            # Load Tema funds data
            tema_file = os.path.join(DATA_DIR, 'tema_funds.json')
            if os.path.exists(tema_file):
                with open(tema_file, 'r') as f:
                    self.tema_data = json.load(f)
            
            # Load competitor data
            comp_file = os.path.join(DATA_DIR, 'competitor_funds.json')
            if os.path.exists(comp_file):
                with open(comp_file, 'r') as f:
                    self.competitor_data = json.load(f)
            
            # Load market share data
            share_file = os.path.join(DATA_DIR, 'market_share.json')
            if os.path.exists(share_file):
                with open(share_file, 'r') as f:
                    self.market_share = json.load(f)
            
            self.last_updated = datetime.now().isoformat()
            print(f"✓ Data loaded successfully at {self.last_updated}")
            
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
    
    def refresh_data(self):
        """Refresh data from sources"""
        print("Refreshing data...")
        # This would trigger the data fetchers
        # For now, just reload from files
        self.load_data()

# Initialize API handler
api_handler = DashboardAPI()
api_handler.load_data()


@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'Tema ETF Dashboard API',
        'version': '1.0',
        'endpoints': {
            '/api/tema-funds': 'Get all Tema ETF data',
            '/api/competitors': 'Get competitor data',
            '/api/market-share': 'Get market share analysis',
            '/api/dashboard': 'Get complete dashboard data',
            '/api/refresh': 'Trigger data refresh'
        }
    })


@app.route('/api/tema-funds')
def get_tema_funds():
    """Get all Tema ETF data"""
    return jsonify({
        'data': api_handler.tema_data,
        'count': len(api_handler.tema_data),
        'last_updated': api_handler.last_updated
    })


@app.route('/api/competitors')
def get_competitors():
    """Get competitor ETF data"""
    tema_ticker = request.args.get('ticker')
    
    if tema_ticker:
        return jsonify({
            'ticker': tema_ticker,
            'competitors': api_handler.competitor_data.get(tema_ticker, []),
            'last_updated': api_handler.last_updated
        })
    
    return jsonify({
        'data': api_handler.competitor_data,
        'last_updated': api_handler.last_updated
    })


@app.route('/api/market-share')
def get_market_share():
    """Get market share analysis"""
    return jsonify({
        'data': api_handler.market_share,
        'last_updated': api_handler.last_updated
    })


@app.route('/api/dashboard')
def get_dashboard_data():
    """Get complete dashboard data"""
    # Combine all data for dashboard
    dashboard_data = {
        'tema_funds': api_handler.tema_data,
        'competitors': api_handler.competitor_data,
        'market_share': api_handler.market_share,
        'summary': {
            'total_tema_aum': sum(fund.get('aum', 0) for fund in api_handler.tema_data),
            'total_funds': len(api_handler.tema_data),
            'avg_expense_ratio': sum(fund.get('expense_ratio', 0) for fund in api_handler.tema_data) / len(api_handler.tema_data) if api_handler.tema_data else 0,
            'last_updated': api_handler.last_updated
        }
    }
    
    return jsonify(dashboard_data)


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Trigger data refresh"""
    api_handler.refresh_data()
    return jsonify({
        'status': 'success',
        'message': 'Data refreshed',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': len(api_handler.tema_data) > 0
    })


def run_scheduler():
    """Run scheduled tasks in background"""
    # Schedule daily data refresh at 5 PM ET (market close + 1 hour)
    schedule.every().day.at("17:00").do(api_handler.refresh_data)
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    # Start background scheduler
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Run Flask app
    print("=" * 60)
    print("Tema Dashboard API Server")
    print("=" * 60)
    print("API running at: http://localhost:5000")
    print("Endpoints:")
    print("  - /api/tema-funds")
    print("  - /api/competitors")
    print("  - /api/market-share")
    print("  - /api/dashboard")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
