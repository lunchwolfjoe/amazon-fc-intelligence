#!/bin/bash

echo "🚀 Starting Compensation Dashboard with API Server..."

# Install API dependencies if needed
if [ ! -d "node_modules_api" ]; then
    echo "📦 Installing API dependencies..."
    npm install --prefix . --package-lock-only=false express cors
fi

# Start API server in background
echo "🔧 Starting API server on port 3001..."
node api-server.js &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Start React development server
echo "⚛️  Starting React app on port 3000..."
npm start &
REACT_PID=$!

echo "✅ Dashboard started!"
echo "📊 API Server: http://localhost:3001"
echo "🌐 Dashboard: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $API_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $API_PID $REACT_PID