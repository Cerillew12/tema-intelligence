"""
Tema ETF Data Fetcher
Scrapes official Tema ETF website for accurate AUM, performance, and fund data
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class TemaDataFetcher:
    """Fetches real-time data from Tema ETFs official website"""
    
    BASE_URL = "https://temaetfs.com"
    
    # Tema ETF tickers and their page URLs
    TEMA_FUNDS = {
        'VOLT': '/volt',
        'RSHO': '/rsho',
        'CANC': '/canc',
        'TOLL': '/toll',
        'HRTS': '/hrts',
        'MNTL': '/mntl',
        'DSPY': '/dspy',
        'AAUM': '/aaum',
        'ITOL': '/itol',
        'GDFN': '/gdfn'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_fund_data(self, ticker: str) -> Optional[Dict]:
        """Fetch data for a specific Tema ETF"""
        
        if ticker not in self.TEMA_FUNDS:
            print(f"Unknown ticker: {ticker}")
            return None
        
        url = f"{self.BASE_URL}{self.TEMA_FUNDS[ticker]}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            fund_data = {
                'ticker': ticker,
                'name': self._extract_fund_name(soup),
                'aum': self._extract_aum(soup),
                'expense_ratio': self._extract_expense_ratio(soup),
                'inception_date': self._extract_inception_date(soup),
                'holdings_count': self._extract_holdings_count(soup),
                'nav': self._extract_nav(soup),
                'market_price': self._extract_market_price(soup),
                'performance': self._extract_performance(soup),
                'updated_at': datetime.now().isoformat()
            }
            
            print(f"✓ Fetched data for {ticker}: AUM=${fund_data['aum']:,.0f}")
            return fund_data
            
        except Exception as e:
            print(f"✗ Error fetching {ticker}: {str(e)}")
            return None
    
    def _extract_fund_name(self, soup: BeautifulSoup) -> str:
        """Extract fund full name"""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        return "Unknown Fund"
    
    def _extract_aum(self, soup: BeautifulSoup) -> float:
        """Extract Assets Under Management"""
        # Look for AuM in fund details section
        aum_pattern = r'AuM\s*\(\$\)\s*\$?([\d,]+)'
        text = soup.get_text()
        match = re.search(aum_pattern, text)
        
        if match:
            aum_str = match.group(1).replace(',', '')
            return float(aum_str)
        
        return 0.0
    
    def _extract_expense_ratio(self, soup: BeautifulSoup) -> float:
        """Extract gross expense ratio"""
        ratio_pattern = r'Gross\s+Expense\s+Ratio\s*([\d.]+)%'
        text = soup.get_text()
        match = re.search(ratio_pattern, text)
        
        if match:
            return float(match.group(1))
        
        return 0.0
    
    def _extract_inception_date(self, soup: BeautifulSoup) -> str:
        """Extract fund inception date"""
        date_pattern = r'Fund\s+Inception\s+Date\s*(\d{2}/\d{2}/\d{2,4})'
        text = soup.get_text()
        match = re.search(date_pattern, text)
        
        if match:
            return match.group(1)
        
        return ""
    
    def _extract_holdings_count(self, soup: BeautifulSoup) -> int:
        """Extract number of holdings"""
        holdings_pattern = r'#\s+of\s+Holdings\s*(\d+)'
        text = soup.get_text()
        match = re.search(holdings_pattern, text)
        
        if match:
            return int(match.group(1))
        
        return 0
    
    def _extract_nav(self, soup: BeautifulSoup) -> float:
        """Extract NAV price"""
        nav_pattern = r'NAV\s*\$?([\d.]+)'
        text = soup.get_text()
        match = re.search(nav_pattern, text)
        
        if match:
            return float(match.group(1))
        
        return 0.0
    
    def _extract_market_price(self, soup: BeautifulSoup) -> float:
        """Extract market price"""
        # Look for share price
        price_pattern = r'Share\s+Price:\s*\$?([\d.]+)'
        text = soup.get_text()
        match = re.search(price_pattern, text)
        
        if match:
            return float(match.group(1))
        
        return 0.0
    
    def _extract_performance(self, soup: BeautifulSoup) -> Dict:
        """Extract performance metrics"""
        performance = {
            'ytd': 0.0,
            '1m': 0.0,
            '3m': 0.0,
            '1y': 0.0,
            'since_inception': 0.0
        }
        
        # This would need more sophisticated parsing based on the table structure
        # For now, returning placeholder
        return performance
    
    def fetch_all_tema_funds(self) -> List[Dict]:
        """Fetch data for all Tema ETFs"""
        all_data = []
        
        for ticker in self.TEMA_FUNDS.keys():
            fund_data = self.fetch_fund_data(ticker)
            if fund_data:
                all_data.append(fund_data)
            time.sleep(1)  # Be polite to the server
        
        return all_data
    
    def save_to_json(self, data: List[Dict], filename: str = 'tema_funds.json'):
        """Save fetched data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Data saved to {filename}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("Tema ETF Data Fetcher")
    print("=" * 60)
    
    fetcher = TemaDataFetcher()
    
    # Fetch all Tema funds
    print("\nFetching data for all Tema ETFs...")
    tema_data = fetcher.fetch_all_tema_funds()
    
    # Save to JSON
    output_file = '/home/claude/tema-dashboard/data/tema_funds.json'
    fetcher.save_to_json(tema_data, output_file)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_aum = sum(fund.get('aum', 0) for fund in tema_data)
    print(f"Total Tema ETFs fetched: {len(tema_data)}")
    print(f"Total Tema AUM: ${total_aum:,.0f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
