"""
Competitor ETF Data Fetcher
Fetches data for competitor ETFs to compare against Tema funds
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class CompetitorDataFetcher:
    """Fetches competitor ETF data from various sources"""
    
    # Define competitors for each Tema fund
    COMPETITORS = {
        'VOLT': ['GRID', 'URNM', 'URA', 'NLR'],  # Electrification/Nuclear competitors
        'RSHO': ['AMER', 'BLLD', 'PAVE'],  # Reshoring/Infrastructure competitors
        'CANC': ['ARKG', 'XBI', 'IBB'],  # Biotech/Healthcare competitors
        'TOLL': ['QUAL', 'JQUA', 'SPHQ'],  # Quality factor competitors
        'HRTS': ['XLV', 'IHI', 'IHF'],  # Healthcare competitors
        'MNTL': ['ESPO', 'GAMR', 'NERD'],  # Mental health/wellness related
        'DSPY': ['SPY', 'IVV', 'VOO'],  # S&P 500 competitors
        'AAUM': ['ARKK', 'GINN', 'TPSC'],  # Alternative assets competitors
        'ITOL': ['IQLT', 'IDEV', 'EFA'],  # International quality competitors
        'GDFN': ['ITA', 'PPA', 'XAR']  # Defense competitors
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_yahoo_finance_data(self, ticker: str) -> Optional[Dict]:
        """
        Fetch ETF data from Yahoo Finance
        NOTE: This requires proper API access or web scraping
        """
        # This is a placeholder - actual implementation would need:
        # 1. yfinance library for Python
        # 2. Or Alpha Vantage API
        # 3. Or direct Yahoo Finance API access
        
        try:
            # Example using yfinance (would need to install: pip install yfinance)
            import yfinance as yf
            
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'aum': info.get('totalAssets', 0),
                'expense_ratio': info.get('annualReportExpenseRatio', 0) * 100 if info.get('annualReportExpenseRatio') else 0,
                'ytd_return': info.get('ytdReturn', 0) * 100 if info.get('ytdReturn') else 0,
                'nav': info.get('navPrice', 0),
                'volume_avg_30d': info.get('averageVolume', 0),
                'updated_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error fetching Yahoo data for {ticker}: {str(e)}")
            return self._get_fallback_data(ticker)
    
    def _get_fallback_data(self, ticker: str) -> Dict:
        """Fallback data structure when APIs fail"""
        return {
            'ticker': ticker,
            'name': f'{ticker} ETF',
            'aum': 0,
            'expense_ratio': 0,
            'ytd_return': 0,
            'nav': 0,
            'volume_avg_30d': 0,
            'updated_at': datetime.now().isoformat(),
            'note': 'Data unavailable - manual update required'
        }
    
    def fetch_etf_flows(self, ticker: str, months_back: int = 1) -> Dict:
        """
        Fetch ETF flow data
        NOTE: This requires access to ETF.com API or similar service
        """
        # This is a placeholder for flow data
        # Actual implementation would need:
        # 1. ETF.com API access (paid)
        # 2. Bloomberg API (paid)
        # 3. Or FactSet API (paid)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        return {
            'ticker': ticker,
            'flows_1m': 0,  # Previous month flows
            'flows_3m': 0,
            'flows_ytd': 0,
            'flows_1y': 0,
            'as_of_date': end_date.strftime('%Y-%m-%d'),
            'note': 'Flow data requires paid API access - manual update needed'
        }
    
    def fetch_all_competitors(self) -> Dict[str, List[Dict]]:
        """Fetch all competitor data organized by Tema fund"""
        all_competitors = {}
        
        print("\nFetching competitor data...")
        print("=" * 60)
        
        for tema_fund, competitors in self.COMPETITORS.items():
            all_competitors[tema_fund] = []
            
            print(f"\n{tema_fund} competitors:")
            for comp_ticker in competitors:
                comp_data = self.fetch_yahoo_finance_data(comp_ticker)
                if comp_data:
                    all_competitors[tema_fund].append(comp_data)
                    print(f"  ✓ {comp_ticker}")
                time.sleep(0.5)  # Rate limiting
        
        return all_competitors
    
    def calculate_market_share(self, tema_data: List[Dict], competitor_data: Dict[str, List[Dict]]) -> Dict:
        """Calculate market share for each Tema fund vs its competitors"""
        market_share = {}
        
        for tema_fund in tema_data:
            ticker = tema_fund['ticker']
            tema_aum = tema_fund.get('aum', 0)
            
            # Get competitor AUMs
            competitors = competitor_data.get(ticker, [])
            competitor_aum = sum(comp.get('aum', 0) for comp in competitors)
            
            # Calculate total market (Tema + Competitors)
            total_market = tema_aum + competitor_aum
            
            # Calculate market share percentage
            if total_market > 0:
                share_pct = (tema_aum / total_market) * 100
            else:
                share_pct = 0
            
            market_share[ticker] = {
                'tema_aum': tema_aum,
                'competitor_aum': competitor_aum,
                'total_market': total_market,
                'market_share_pct': round(share_pct, 2),
                'competitors_count': len(competitors)
            }
        
        return market_share
    
    def save_to_json(self, data: Dict, filename: str):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Data saved to {filename}")


def main():
    """Main execution"""
    print("=" * 60)
    print("Competitor ETF Data Fetcher")
    print("=" * 60)
    
    fetcher = CompetitorDataFetcher()
    
    # Fetch competitor data
    competitor_data = fetcher.fetch_all_competitors()
    
    # Save competitor data
    output_file = '/home/claude/tema-dashboard/data/competitor_funds.json'
    fetcher.save_to_json(competitor_data, output_file)
    
    print("\n" + "=" * 60)
    print("COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
