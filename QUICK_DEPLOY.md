# 🚀 Quick Deploy ROXI to Vercel

## Step 1: Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name it: `roxi-research-assistant`
4. Make it Public
5. Click "Create repository"

## Step 2: Push Your Code
```bash
# In your ROXI folder:
git init
git add .
git commit -m "Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/yourusername/roxi-research-assistant.git
git push -u origin main
```

## Step 3: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Select `roxi-research-assistant`
5. Click "Import"

## Step 4: Configure Vercel
- **Framework**: Other (Custom)
- **Root Directory**: `./`
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: `./`

## Step 5: Add Environment Variable
In Vercel project → Settings → Environment Variables:
- **Name**: `OPENAI_API_KEY`
- **Value**: `roxi_1Gt3uUT6jEO8s9TEGO47sx0-YAqZ8dgGO033rjOx7TQ`

## Step 6: Deploy! 🎉
Click "Deploy" and your ROXI will be live at:
`https://roxi-research-assistant-yourname.vercel.app`

## ✅ What Works Online
- 🔍 Paper search
- 📥 PDF downloads
- 🤖 AI summarization (mock)
- 📋 Information extraction (mock)
- 🌐 Modern responsive UI

## 📱 Mobile Ready
The site works perfectly on mobile devices!

Ready to launch your research assistant! 🚀
