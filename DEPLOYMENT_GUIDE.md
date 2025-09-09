# 🚀 AI Solution Finder - Free Deployment Guide

## Prerequisites
- GitHub account
- Your code pushed to a GitHub repository

## Step 1: Deploy Database (FREE - MongoDB Atlas)

### 1.1 Setup MongoDB Atlas
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for free account
3. Click "Build a Database" → Choose FREE tier (M0 Sandbox)
4. Select your preferred cloud provider and region
5. Create cluster (takes 2-3 minutes)

### 1.2 Configure Database Access
1. Click "Database Access" → "Add New Database User"
2. Choose "Password" authentication
3. Create username/password (save these!)
4. Give "Read and write to any database" permissions

### 1.3 Configure Network Access
1. Click "Network Access" → "Add IP Address"
2. Click "Allow Access from Anywhere" (0.0.0.0/0)
3. Confirm

### 1.4 Get Connection String
1. Click "Databases" → "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your database user password
5. Replace `<dbname>` with `ai_solution_finder`

Example: `mongodb+srv://username:password@cluster0.abcde.mongodb.net/ai_solution_finder?retryWrites=true&w=majority`

## Step 2: Deploy Backend (FREE - Railway)

### 2.1 Setup Railway
1. Go to [Railway](https://railway.app)
2. Sign up with GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Connect your repository

### 2.2 Configure Environment Variables
In Railway dashboard, go to Variables tab and add:
```
MONGO_URL=mongodb+srv://your-connection-string-here
EMERGENT_LLM_KEY=sk-emergent-cD9899fF097Ea04B75
DB_NAME=ai_solution_finder
PORT=8001
```

### 2.3 Configure Build Settings
1. Set Root Directory: `backend`
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python -m uvicorn ai_server:app --host 0.0.0.0 --port $PORT`

### 2.4 Deploy
1. Click "Deploy"
2. Wait for deployment (5-10 minutes)
3. Note your Railway URL: `https://your-app-name.railway.app`

## Step 3: Deploy Frontend (FREE - Vercel)

### 3.1 Setup Vercel
1. Go to [Vercel](https://vercel.com)
2. Sign up with GitHub account
3. Click "New Project"
4. Import your GitHub repository

### 3.2 Configure Build Settings
1. Root Directory: `frontend`
2. Build Command: `yarn build`
3. Output Directory: `build`
4. Install Command: `yarn install`

### 3.3 Configure Environment Variables
In Vercel dashboard, add environment variable:
```
REACT_APP_BACKEND_URL=https://your-railway-app.railway.app
```
(Use your Railway URL from Step 2.4)

### 3.4 Deploy
1. Click "Deploy"
2. Wait for deployment (3-5 minutes)
3. Your app will be live at: `https://your-app-name.vercel.app`

## Step 4: Test Your Deployment

### 4.1 Backend Testing
Test your Railway backend:
```bash
curl https://your-railway-app.railway.app/api/
```
Should return: `{"message": "AI Solution Finder API is running!", "version": "1.0.0"}`

### 4.2 Frontend Testing
1. Visit your Vercel URL
2. Try entering a query like "I need Infrastructure as Code tools"
3. Verify AI recommendations are working
4. Test feedback and save functionality

## Step 5: Custom Domain (Optional - FREE)

### 5.1 Vercel Custom Domain
1. In Vercel dashboard → Settings → Domains
2. Add your domain name
3. Configure DNS records as shown

### 5.2 Railway Custom Domain
1. In Railway dashboard → Settings → Domains
2. Add your backend domain
3. Configure DNS records

## 🎯 Cost Breakdown

| Service | Free Tier Limits | Cost |
|---------|------------------|------|
| MongoDB Atlas | 512MB storage, 100 connections | FREE |
| Railway | $5 credit/month, 512MB RAM | FREE |
| Vercel | 100GB bandwidth, unlimited projects | FREE |
| **Total Monthly Cost** | | **$0** |

## 🔧 Production Optimizations

### Security Enhancements
1. Update CORS origins to your domain only
2. Add rate limiting
3. Implement API key rotation
4. Set up monitoring alerts

### Performance Optimizations  
1. Enable Vercel Analytics
2. Add Railway metrics monitoring
3. Implement caching strategies
4. Optimize database queries

## 🆘 Troubleshooting

### Common Issues:

**Backend not connecting to database:**
- Check MongoDB Atlas IP whitelist (0.0.0.0/0)
- Verify connection string and credentials
- Check Railway environment variables

**Frontend can't reach backend:**
- Verify REACT_APP_BACKEND_URL in Vercel
- Check Railway deployment logs
- Ensure CORS is configured correctly

**AI recommendations not working:**
- Verify EMERGENT_LLM_KEY is set correctly
- Check Railway logs for API errors
- Ensure you have credits remaining

### Getting Help:
1. Check Railway deployment logs
2. Check Vercel build logs  
3. Test API endpoints directly
4. Monitor MongoDB Atlas metrics

## 🚀 Going Live Checklist

- [ ] MongoDB Atlas cluster running
- [ ] Railway backend deployed and responding
- [ ] Vercel frontend deployed and loading
- [ ] Backend API endpoints working
- [ ] AI recommendations functioning
- [ ] Database connections successful
- [ ] Environment variables configured
- [ ] Custom domains configured (optional)
- [ ] SSL certificates active
- [ ] Performance monitoring enabled

## 🎉 Congratulations! 

Your AI Solution Finder is now live and accessible to users worldwide - completely FREE!

**Frontend URL:** https://your-app-name.vercel.app  
**Backend API:** https://your-railway-app.railway.app/api  
**Database:** MongoDB Atlas cluster  

Share your app with the world! 🌍