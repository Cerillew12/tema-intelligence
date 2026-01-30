#!/bin/bash

echo "=============================================="
echo "Tema ETF Dashboard - Quick Start Script"
echo "=============================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"
echo ""

# Create virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Create data directory if it doesn't exist
mkdir -p data
echo -e "${GREEN}✓ Data directory created${NC}"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo "1) Test data fetchers locally"
echo "2) Start API server"
echo "3) Run complete setup (fetch data + start server)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "=============================================="
        echo "Testing Data Fetchers"
        echo "=============================================="
        echo ""
        
        echo "Fetching Tema ETF data..."
        python backend/fetch_tema_data.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Tema data fetched successfully${NC}"
        else
            echo -e "${RED}✗ Error fetching Tema data${NC}"
        fi
        
        echo ""
        echo "Fetching competitor data..."
        python backend/fetch_competitor_data.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Competitor data fetched successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Competitor data fetch completed with warnings${NC}"
            echo "This is expected if yfinance is not installed or APIs are unavailable"
        fi
        ;;
        
    2)
        echo ""
        echo "=============================================="
        echo "Starting API Server"
        echo "=============================================="
        echo ""
        echo -e "${YELLOW}Make sure you have run option 1 first to fetch data!${NC}"
        echo ""
        read -p "Continue? (y/n): " continue
        
        if [ "$continue" = "y" ]; then
            echo "Starting server at http://localhost:5000"
            echo "Press Ctrl+C to stop"
            echo ""
            python backend/api_server.py
        fi
        ;;
        
    3)
        echo ""
        echo "=============================================="
        echo "Complete Setup"
        echo "=============================================="
        echo ""
        
        echo "Step 1: Fetching Tema data..."
        python backend/fetch_tema_data.py
        echo ""
        
        echo "Step 2: Fetching competitor data..."
        python backend/fetch_competitor_data.py
        echo ""
        
        echo "Step 3: Starting API server..."
        echo "Server will run at http://localhost:5000"
        echo ""
        echo -e "${GREEN}Open frontend/index.html in your browser to view the dashboard${NC}"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo ""
        python backend/api_server.py
        ;;
        
    4)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Open frontend/index.html in your web browser"
echo "2. Or serve it with: python -m http.server 8000 --directory frontend"
echo "3. Then visit http://localhost:8000"
echo ""
echo "For deployment to production, see DEPLOYMENT_GUIDE.md"
echo ""
