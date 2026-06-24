#!/bin/bash
set -e

# ============================================================
# KIBO.IS Complete Setup & Deployment Script
# Run this from your Mac Studio in Antigravity IDE
# ============================================================

KIBO_DIR="/Users/iceman/Documents/Code/Kibo/kibo-is"
VPS_IP="89.147.109.6"
VPS_PATH="/var/www/kibo.is"

echo "=== KIBO.IS Setup & Deployment ==="
echo ""

# ============================================================
# Step 1: Navigate to project directory
# ============================================================

cd "$KIBO_DIR"
echo "✓ Working directory: $KIBO_DIR"
echo ""

# ============================================================
# Step 2: Verify existing src/App.jsx
# ============================================================

if [ ! -f "src/App.jsx" ]; then
  echo "❌ src/App.jsx not found."
  exit 1
fi
echo "✓ Using existing src/App.jsx"
echo ""

# ============================================================
# Step 3: Install Tailwind CSS
# ============================================================

echo "📦 Installing Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer

echo "✓ Tailwind installed"
echo ""

# ============================================================
# Step 4: Create tailwind.config.js
# ============================================================

echo "⚙️  Configuring Tailwind..."

cat > tailwind.config.js << 'EOF'
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

echo "✓ Tailwind configured"
echo ""

# ============================================================
# Step 5: Build for production
# ============================================================

echo "🔨 Building for production..."
npm run build

if [ ! -d "dist" ]; then
  echo "❌ Build failed. dist/ folder not created."
  exit 1
fi

echo "✓ Build complete"
echo "✓ Files ready in dist/"
echo ""

# ============================================================
# Step 6: Deploy to VPS
# ============================================================

echo "🚀 Deploying to VPS ($VPS_IP)..."
echo "   Copying dist/* to $VPS_PATH/"

scp -r dist/* root@$VPS_IP:$VPS_PATH/

if [ $? -eq 0 ]; then
  echo "✓ Files deployed to VPS"
else
  echo "❌ SCP failed. Check SSH key and VPS connectivity."
  exit 1
fi

echo ""

# ============================================================
# Step 7: Verify deployment
# ============================================================

echo "🔍 Verifying deployment on VPS..."

ssh root@$VPS_IP << 'VERIFY'
echo "   Checking /var/www/kibo.is/..."
ls -la /var/www/kibo.is/ | head -10

echo ""
echo "   Checking if index.html exists..."
[ -f /var/www/kibo.is/index.html ] && echo "   ✓ index.html found" || echo "   ❌ index.html NOT found"

echo ""
echo "   Reloading nginx..."
sudo systemctl reload nginx

echo ""
echo "   Nginx status:"
sudo systemctl status nginx | head -3
VERIFY

echo ""

# ============================================================
# Step 8: Test the deployment
# ============================================================

echo "✅ Deployment complete!"
echo ""
echo "📍 Your KIBO.IS dashboard is now live at:"
echo "   https://kibo.is"
echo "   https://www.kibo.is"
echo ""
echo "🔗 DNS Status:"
nslookup kibo.is 2>/dev/null | grep -A 1 "Name:" || echo "   (DNS may still be propagating — up to 48 hours)"
echo ""
echo "📝 Next steps:"
echo "   1. Open https://kibo.is in your browser"
echo "   2. Start the FastAPI backend on your DGX (CPO agent system)"
echo "   3. Wire up /api/transactions to execute privacy work"
echo ""
echo "🔧 To monitor:"
echo "   ssh root@$VPS_IP 'tail -f /var/log/nginx/kibo.is.access.log'"
echo ""

