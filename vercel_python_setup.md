# PYTHON VERCEL SETUP - Step by Step

## Method 1: Web Interface (Easiest)
1. Go to vercel.com → New Project
2. Import your GitHub repo
3. Framework: **Other** (not in dropdown)
4. Root Directory: ./
5. Build Command: `pip install -r requirements.txt`
6. Output Directory: ./
7. Click Deploy

## Method 2: Vercel CLI (More Control)
1. Install Vercel CLI: npm i -g vercel
2. In your project folder:
   ```bash
   vercel
   ```
3. Answer prompts:
   - Set up and deploy? Yes
   - Which scope? Your account
   - Link to existing project? No
   - Project name: roxi-research-assistant
   - In which directory is your code located? ./
   - Want to override settings? Yes
   - Build Command: pip install -r requirements.txt

## Method 3: Manual Detection
Vercel will auto-detect Python from:
- vercel.json file
- requirements.txt file
- .py files in project

## Correct Settings:
Framework: Other (or leave blank)
Root Directory: ./
Build Command: pip install -r requirements.txt
Output Directory: ./
Install Command: pip install -r requirements.txt

## Environment Variables:
OPENAI_API_KEY = roxi_1Gt3uUT6jEO8s9TEGO47sx0-YAqZ8dgGO033rjOx7TQ
