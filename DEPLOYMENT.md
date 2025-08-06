# 🚀 Netlify Deployment Guide

## 📋 **Prerequisites**
- GitHub account
- Netlify account (free)
- Your app ready for deployment

## 🎯 **Deployment Steps**

### **Step 1: Prepare Your Repository**
1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/upskill-recommender.git
   git push -u origin main
   ```

### **Step 2: Deploy Frontend to Netlify**

#### **Option A: Deploy via Netlify UI (Recommended)**
1. **Go to [Netlify](https://netlify.com)**
2. **Click "New site from Git"**
3. **Connect your GitHub repository**
4. **Configure build settings:**
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
   - **Base directory:** `frontend`
5. **Click "Deploy site"**

#### **Option B: Deploy via Netlify CLI**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy from frontend directory
cd frontend
netlify deploy --prod --dir=dist
```

### **Step 3: Configure Environment Variables**
1. **In Netlify dashboard, go to Site settings > Environment variables**
2. **Add your backend URL:**
   - **Key:** `VITE_API_URL`
   - **Value:** `https://your-backend-url.com` (or your backend URL)

### **Step 4: Deploy Backend (Choose One)**

#### **Option A: Railway (Recommended)**
1. **Go to [Railway](https://railway.app)**
2. **Connect your GitHub repository**
3. **Select the backend directory**
4. **Add environment variables:**
   - `GEMINI_API_KEY=your-api-key`
5. **Deploy**

#### **Option B: Render**
1. **Go to [Render](https://render.com)**
2. **Create new Web Service**
3. **Connect your GitHub repository**
4. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Add environment variables**
6. **Deploy**

#### **Option C: Heroku**
1. **Install Heroku CLI**
2. **Create `Procfile`:**
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. **Deploy:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### **Step 5: Update Frontend API URL**
1. **Get your backend URL** from the deployment
2. **In Netlify, update environment variable:**
   - `VITE_API_URL=https://your-backend-url.com`
3. **Trigger a new deployment**

## 🔧 **Configuration Files**

### **Frontend Configuration**
- ✅ `netlify.toml` - Netlify settings
- ✅ `package.json` - Dependencies and scripts
- ✅ Environment variables for API URL

### **Backend Configuration**
- ✅ `requirements.txt` - Python dependencies
- ✅ Environment variables for API key
- ✅ CORS configuration for production

## 🌟 **Your App Will Be Live At:**
- **Frontend:** `https://your-app-name.netlify.app`
- **Backend:** `https://your-backend-url.com`

## 🎉 **Features Available After Deployment:**
- ✅ **Smart course recommendations**
- ✅ **Career path suggestions**
- ✅ **Advanced filtering**
- ✅ **Real-time search**
- ✅ **Beautiful responsive UI**
- ✅ **AI-powered insights** (if API key is set)

## 🔍 **Testing Your Deployment**
1. **Visit your Netlify URL**
2. **Enter a job role** (e.g., "Software Engineer")
3. **Add some skills** (e.g., "Python, JavaScript")
4. **Click "Get Smart Recommendations"**
5. **Verify all features work**

## 🚨 **Troubleshooting**
- **CORS errors:** Ensure backend CORS allows your Netlify domain
- **API not found:** Check environment variables in Netlify
- **Build fails:** Verify Node.js version and dependencies
- **Backend errors:** Check logs in your backend hosting platform

## 📞 **Need Help?**
- **Netlify Docs:** https://docs.netlify.com
- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs

Your Upskill Recommender will be live and helping users worldwide! 🌍 