# Flow Data Integration Guide

## Overview

This guide explains how to integrate monthly ETF flow data into the dashboard. Flow data is the most challenging aspect because it's not freely available and requires either:
1. Paid API subscription
2. Bloomberg Terminal access
3. Manual entry

---

## Option A: ETF.com API Integration (Recommended)

### 1. Sign Up for API Access
- Visit: https://www.etf.com/etfanalytics/etf-finder
- Contact sales for API pricing (typically $99-299/month)
- Request access to "Fund Flows" endpoint

### 2. Get Your API Credentials
You'll receive:
- API Key
- API Secret (maybe)
- Base URL: `https://api.etf.com/v1/`

### 3. Update Code

**File:** `backend/fetch_competitor_data.py`

Replace lines 52-70 with:

```python
def fetch_etf_flows(self, ticker: str, months_back: int = 1) -> Dict:
    """Fetch ETF flow data from ETF.com API"""
    
    api_key = os.getenv('ETF_COM_API_KEY')
    if not api_key:
        return self._get_fallback_flows(ticker)
    
    try:
        # ETF.com API endpoint (verify actual endpoint with their docs)
        url = f'https://api.etf.com/v1/fund/{ticker}/flows'
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Request last 12 months of data
        params = {
            'period': 'monthly',
            'months': 12
        }
        
        response = self.session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant periods
        # (Adjust based on actual API response format)
        flows = data.get('flows', [])
        
        # Get most recent completed month (previous month)
        prev_month = flows[0] if flows else {}
        
        # Calculate aggregates
        flows_3m = sum(f.get('amount', 0) for f in flows[:3])
        flows_ytd = sum(f.get('amount', 0) for f in flows if f.get('year') == datetime.now().year)
        flows_1y = sum(f.get('amount', 0) for f in flows[:12])
        
        return {
            'ticker': ticker,
            'flows_prev_month': prev_month.get('amount', 0),
            'flows_3m': flows_3m,
            'flows_ytd': flows_ytd,
            'flows_1y': flows_1y,
            'as_of_date': prev_month.get('date', ''),
            'source': 'ETF.com API'
        }
        
    except Exception as e:
        print(f"✗ ETF.com API error for {ticker}: {str(e)}")
        return self._get_fallback_flows(ticker)

def _get_fallback_flows(self, ticker: str) -> Dict:
    """Fallback to manual data if API fails"""
    manual_data_file = '/home/claude/tema-dashboard/data/manual_flows.json'
    
    if os.path.exists(manual_data_file):
        with open(manual_data_file, 'r') as f:
            manual_data = json.load(f)
            if ticker in manual_data.get('flows', {}):
                return manual_data['flows'][ticker]
    
    return {
        'ticker': ticker,
        'flows_prev_month': 0,
        'flows_3m': 0,
        'flows_ytd': 0,
        'flows_1y': 0,
        'as_of_date': '',
        'source': 'manual_fallback',
        'note': 'Data unavailable - requires manual update'
    }
```

### 4. Add API Key to Environment

**File:** `backend/.env`

```env
ETF_COM_API_KEY=your-actual-api-key-here
```

### 5. Test Integration

```bash
cd backend
python -c "
from fetch_competitor_data import CompetitorDataFetcher
fetcher = CompetitorDataFetcher()
result = fetcher.fetch_etf_flows('VOLT')
print(result)
"
```

Expected output:
```json
{
  "ticker": "VOLT",
  "flows_prev_month": 15200000,
  "flows_3m": 42500000,
  "flows_ytd": 85000000,
  "flows_1y": 125000000,
  "as_of_date": "2025-12-31",
  "source": "ETF.com API"
}
```

---

## Option B: Bloomberg Terminal Integration

### 1. Install Bloomberg API

```bash
pip install blpapi --break-system-packages
```

### 2. Update Code

**File:** `backend/fetch_bloomberg_flows.py` (new file)

```python
import blpapi
from datetime import datetime, timedelta
from typing import Dict, List

class BloombergFlowFetcher:
    """Fetch ETF flow data from Bloomberg Terminal"""
    
    def __init__(self):
        self.session = blpapi.Session()
        
    def connect(self):
        """Connect to Bloomberg Terminal"""
        if not self.session.start():
            raise Exception("Failed to start Bloomberg session")
        
        if not self.session.openService("//blp/refdata"):
            raise Exception("Failed to open Bloomberg service")
    
    def fetch_flows(self, ticker: str) -> Dict:
        """
        Fetch monthly flow data for ETF
        Bloomberg field: FUND_NET_ASSET_FLOW
        """
        
        try:
            self.connect()
            
            # Get reference data service
            refDataService = self.session.getService("//blp/refdata")
            request = refDataService.createRequest("HistoricalDataRequest")
            
            # Set up request
            request.getElement("securities").appendValue(f"{ticker} US Equity")
            request.getElement("fields").appendValue("FUND_NET_ASSET_FLOW")
            
            # Get last 12 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            request.set("startDate", start_date.strftime("%Y%m%d"))
            request.set("endDate", end_date.strftime("%Y%m%d"))
            request.set("periodicitySelection", "MONTHLY")
            
            # Send request
            self.session.sendRequest(request)
            
            # Process response
            flows = []
            while True:
                event = self.session.nextEvent(500)
                
                if event.eventType() == blpapi.Event.RESPONSE:
                    # Parse flow data
                    for msg in event:
                        securityData = msg.getElement("securityData")
                        fieldData = securityData.getElement("fieldData")
                        
                        for i in range(fieldData.numValues()):
                            dataPoint = fieldData.getValueAsElement(i)
                            date = dataPoint.getElementAsString("date")
                            flow = dataPoint.getElementAsFloat("FUND_NET_ASSET_FLOW")
                            flows.append({'date': date, 'amount': flow})
                    
                    break
            
            # Calculate periods
            return {
                'ticker': ticker,
                'flows_prev_month': flows[-1]['amount'] if flows else 0,
                'flows_3m': sum(f['amount'] for f in flows[-3:]),
                'flows_ytd': sum(f['amount'] for f in flows if f['date'].startswith(str(datetime.now().year))),
                'flows_1y': sum(f['amount'] for f in flows),
                'as_of_date': flows[-1]['date'] if flows else '',
                'source': 'Bloomberg Terminal'
            }
            
        except Exception as e:
            print(f"Bloomberg error: {e}")
            return self._get_fallback_flows(ticker)
        
        finally:
            self.session.stop()
```

### 3. Usage

```python
from fetch_bloomberg_flows import BloombergFlowFetcher

fetcher = BloombergFlowFetcher()
result = fetcher.fetch_flows('VOLT')
print(result)
```

---

## Option C: Manual Entry (No Cost)

### 1. Get Flow Data

**From Bloomberg Terminal:**
1. Open Bloomberg Terminal
2. Type: `VOLT US Equity DES`
3. Click "Flows" tab
4. Note the monthly flow values

**From ETF.com (Free):**
1. Visit: https://www.etf.com/VOLT
2. Scroll to "Fund Flows" section
3. Look for monthly inflow/outflow data
4. May need to check multiple times throughout month

**From ETFdb.com:**
1. Visit: https://etfdb.com/etf/VOLT/
2. Look for "Asset Flows" section
3. May be delayed by 1-2 weeks

### 2. Update Manual Flow File

**File:** `data/manual_flows.json`

Copy from template:
```bash
cp data/manual_flows_template.json data/manual_flows.json
```

Edit with your data:
```json
{
  "meta": {
    "last_updated": "2026-01-28",
    "data_source": "Bloomberg Terminal",
    "reporting_period": "December 2025"
  },
  "flows": {
    "VOLT": {
      "ticker": "VOLT",
      "flows_prev_month": 15200000,
      "flows_3m": 42500000,
      "flows_ytd": 85000000,
      "flows_1y": 125000000,
      "as_of_date": "2025-12-31"
    }
  }
}
```

### 3. Update Monthly

**Schedule:**
- Update within first 5 business days of each month
- After flow data becomes available from your source
- Before your monthly reporting deadline

**Process:**
1. Gather data from Bloomberg/ETF.com
2. Update `manual_flows.json`
3. Commit to GitHub (triggers auto-deploy)
4. Or click "Refresh Data" in dashboard

---

## Hybrid Approach (Recommended Starting Point)

### Best Practice: Start Manual, Automate Later

**Month 1-3: Manual Entry**
- Use manual_flows.json
- Get comfortable with data format
- Validate accuracy
- Cost: $0

**Month 4+: Evaluate Need**
- If you're using dashboard weekly → subscribe to API
- If you're updating reliably → continue manual
- If Bloomberg is available → integrate it

**Implementation:**
The code already supports fallback to manual data, so you can:
1. Start with manual entry now
2. Subscribe to API later
3. Code will automatically use API when available

---

## Data Validation & Quality Checks

### Automated Checks (Built Into Code)

```python
def validate_flow_data(flow_data: Dict) -> bool:
    """Validate flow data makes sense"""
    
    # Check 1: Flows shouldn't be suspiciously large
    max_reasonable_flow = 100_000_000_000  # $100B
    if abs(flow_data.get('flows_prev_month', 0)) > max_reasonable_flow:
        print(f"⚠ Warning: Suspicious flow amount for {flow_data['ticker']}")
        return False
    
    # Check 2: YTD should be larger than 1 month
    # (Unless it's January)
    if datetime.now().month > 1:
        if abs(flow_data['flows_ytd']) < abs(flow_data['flows_prev_month']):
            print(f"⚠ Warning: YTD < 1 month for {flow_data['ticker']}")
            return False
    
    # Check 3: Dates should be recent
    try:
        as_of = datetime.strptime(flow_data['as_of_date'], '%Y-%m-%d')
        days_old = (datetime.now() - as_of).days
        if days_old > 45:  # More than 45 days old
            print(f"⚠ Warning: Flow data is {days_old} days old for {flow_data['ticker']}")
            return False
    except:
        pass
    
    return True
```

### Manual Validation Checklist

Before publishing flow data:
- [ ] Previous month adds up to 3-month total
- [ ] YTD total makes sense (not negative unless consistent outflows)
- [ ] Date is last day of previous month
- [ ] Units are correct (dollars, not millions)
- [ ] Sign is correct (positive = inflow, negative = outflow)
- [ ] Compare to AUM change (rough validation)

---

## Troubleshooting

### API Returns Error 401 (Unauthorized)
**Cause:** Invalid API key
**Fix:** 
1. Check API key in `.env` file
2. Verify key is active in ETF.com dashboard
3. Check for extra spaces in key

### Bloomberg Connection Fails
**Cause:** Bloomberg Terminal not running
**Fix:**
1. Launch Bloomberg Terminal
2. Log in
3. Retry connection

### Flow Data Looks Wrong
**Cause:** Unit conversion issue
**Fix:**
```python
# ETF.com might return in millions
if flow_data['amount'] < 1000:  # Suspiciously small
    flow_data['amount'] *= 1_000_000  # Convert millions to dollars
```

### Data Is Stale
**Cause:** Source hasn't updated yet
**Fix:**
- Wait until 5th business day of month
- Or use previous month's data temporarily

---

## Cost Comparison

| Method | Setup Time | Monthly Time | Cost/Year |
|--------|------------|--------------|-----------|
| Manual | 1 hour | 30 min | $0 |
| ETF.com API | 2 hours | 0 min | $1,188 - $3,588 |
| Bloomberg | 4 hours | 0 min | $25,000+ (Terminal cost) |

**Recommendation:** 
- **Small team (<5 people):** Manual entry
- **Active users (daily):** ETF.com API
- **Already have Bloomberg:** Use Bloomberg integration

---

## Next Steps

1. **Choose your method** (A, B, or C)
2. **Follow integration steps** above
3. **Test with one fund** (e.g., VOLT)
4. **Expand to all funds** once working
5. **Set calendar reminder** for monthly updates (if manual)

---

**Need help?** Check the main README.md troubleshooting section or contact ETF.com support for API questions.
