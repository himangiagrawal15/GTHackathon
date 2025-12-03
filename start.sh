#!/bin/bash

echo "=========================================="
echo "Automated Insight Engine - Startup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p uploads outputs outputs/charts

echo ""
echo "✓ Setup complete!"
echo ""
echo "=========================================="
echo "Starting Backend Server..."
echo "=========================================="
echo ""
echo "Backend will run on: http://localhost:5000"
echo "API endpoints will be available at: http://localhost:5000/api"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""
echo "After the server starts, open frontend/index.html in your browser"
echo ""

# Start Flask app
cd backend
python app.py