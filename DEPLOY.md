# 🚀 Deploy ROXI to Vercel

## 📋 Prerequisites
- GitHub account
- Vercel account (free)
- Git installed

## 🗂️ Files Ready for Deployment
✅ `vercel.json` - Vercel configuration  
✅ `requirements.txt` - Python dependencies  
✅ `app.py` - Updated for serverless  

## 📝 Deployment Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/yourusername/roxi.git
git push -u origin main
```

### 2. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Connect your GitHub account
4. Select your ROXI repository
5. Configure settings:
   - Framework: **Python**
   - Root Directory: **./**
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: **.**

### 3. Set Environment Variables
In Vercel dashboard → Settings → Environment Variables:
```
OPENAI_API_KEY=your_roxi_api_key_here
```

### 4. Deploy!
Click "Deploy" - your app will be live at:
`https://your-project-name.vercel.app`

## 🔧 Notes
- PDF library will be temporary (serverless limitation)
- For permanent storage, consider Vercel KV or external storage
- API calls work normally
- All features available except persistent file storage

## 🎉 After Deployment
Your ROXI will be accessible online with:
- Search papers
- Download PDFs (temporary)
- Summarization features
- Beautiful modern UI

Ready to deploy! 🚀
