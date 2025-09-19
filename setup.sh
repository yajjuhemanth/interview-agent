#!/bin/bash

# Interview Agent Setup Script
echo "🚀 Setting up Interview Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed. Please install pip and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration:"
    echo "   - Add your OpenAI API key"
    echo "   - Configure MySQL connection details"
    echo ""
    echo "🔗 You can get an OpenAI API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Check if user wants to set up database
read -p "🗄️  Do you want to set up the database now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔨 Setting up database..."
    python setup_db.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database setup completed successfully!"
    else
        echo "❌ Database setup failed. Please check your MySQL configuration in .env file."
        echo "Make sure MySQL is running and the credentials are correct."
        exit 1
    fi
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the application: python app.py"
echo "  3. Open browser: http://localhost:5000"
echo ""
echo "To test the API:"
echo "  python test_api.py"
echo ""
echo "To see a demo without setup:"
echo "  python demo.py"