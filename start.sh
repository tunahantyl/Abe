#!/bin/bash
# UniSkor Startup Script

echo "🚀 Starting UniSkor..."

# Check if virtual environment exists
if [ ! -d "uniskor-backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd uniskor-backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start backend
echo "🔧 Starting backend..."
cd uniskor-backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd uniskor-web
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ UniSkor started!"
echo "📊 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait $BACKEND_PID $FRONTEND_PID
