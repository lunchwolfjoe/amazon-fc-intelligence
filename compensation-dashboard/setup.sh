#!/bin/bash

echo "🎯 Setting up Compensation Dashboard..."

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Install API dependencies
echo "🔧 Installing API dependencies..."
cd api && npm install && cd ..

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the dashboard locally:"
echo "   Frontend: npm start"
echo "   API:      cd api && npm start"
echo ""
echo "🌐 To deploy to AWS Amplify:"
echo "   ./deploy.sh"
echo ""
echo "📊 Dashboard will be available at:"
echo "   Local:  http://localhost:3000"
echo "   API:    http://localhost:3001"