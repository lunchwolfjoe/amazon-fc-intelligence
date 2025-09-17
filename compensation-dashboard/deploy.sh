#!/bin/bash

echo "🚀 Deploying Compensation Dashboard to AWS Amplify..."

# Check if Amplify CLI is installed
if ! command -v amplify &> /dev/null; then
    echo "❌ Amplify CLI not found. Installing..."
    npm install -g @aws-amplify/cli
fi

# Initialize Amplify if not already done
if [ ! -d "amplify" ]; then
    echo "🔧 Initializing Amplify project..."
    amplify init --yes
fi

# Add hosting if not already added
if [ ! -f "amplify/backend/hosting/amplifyhosting/amplifyhosting-template.json" ]; then
    echo "🌐 Adding Amplify hosting..."
    amplify add hosting
fi

# Build and deploy
echo "📦 Building and deploying..."
amplify publish --yes

echo "✅ Deployment complete!"
echo ""
echo "🎉 Your dashboard is now live!"
echo "📊 You can view it at the URL provided above"
echo ""
echo "🔄 To update the dashboard:"
echo "   1. Make your changes"
echo "   2. Run: amplify publish"
echo ""
echo "💡 To add a custom domain:"
echo "   1. Go to AWS Amplify Console"
echo "   2. Select your app"
echo "   3. Go to Domain Management"
echo "   4. Add your custom domain"