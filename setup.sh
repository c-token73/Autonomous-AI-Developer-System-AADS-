#!/bin/bash
# Autonomous AI Developer System - Setup Script

echo "🤖 Autonomous AI Developer System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "✓ Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "  Virtual environment activated"
else
    # Windows path
    source venv/Scripts/activate
    echo "  Virtual environment activated (Windows)"
fi
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  Dependencies installed"
echo ""

# Create .env if not exists
if [ ! -f ".env.local" ]; then
    echo "✓ Creating .env.local from .env template..."
    cp .env .env.local
    echo "  .env.local created - please configure with your settings"
else
    echo "✓ .env.local already exists"
fi
echo ""

# Run tests
echo "✓ Running tests..."
python -m pytest tests/ -q 2>/dev/null || echo "  Tests (optional - install pytest for testing)"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.local with your configuration"
echo "2. Run: streamlit run app.py"
echo "3. Open: http://localhost:8501"
echo ""
