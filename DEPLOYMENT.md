# Deployment Guide for Resume Tailoring Application

This guide covers deployment options for your Resume Tailoring application to various platforms.

## 🚀 Quick Deploy Options

### Option 1: Render.com (Recommended - Free Tier Available)

**Step 1: Prepare Your Repository**
```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

**Step 2: Deploy on Render**
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `Iskos1/Resume-Tailoring`
4. Configure:
   - **Name**: resume-tailoring
   - **Environment**: Node
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Instance Type**: Free
5. Add Environment Variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key
6. Click "Create Web Service"

Your app will be live at: `https://resume-tailoring.onrender.com`

**Note**: Free tier may spin down after inactivity. First request may take 30-60 seconds.

---

### Option 2: Railway.app (Simple & Fast)

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project" → "Deploy from GitHub repo"
3. Select your `Resume-Tailoring` repository
4. Railway auto-detects Node.js
5. Add environment variable:
   - `OPENAI_API_KEY`: Your API key
6. Deploy!

Your app will be live at: `https://your-app.railway.app`

---

### Option 3: Vercel (Serverless)

**Step 1: Install Vercel CLI** (optional)
```bash
npm install -g vercel
```

**Step 2: Deploy**
```bash
cd "/Users/isk/Resume Tailoring"
vercel
```

Or use the Vercel dashboard:
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Add environment variable: `OPENAI_API_KEY`
4. Deploy

Your app will be live at: `https://your-app.vercel.app`

---

### Option 4: Heroku

**Step 1: Install Heroku CLI**
```bash
brew tap heroku/brew && brew install heroku
```

**Step 2: Deploy**
```bash
cd "/Users/isk/Resume Tailoring"
heroku login
heroku create resume-tailoring
heroku config:set OPENAI_API_KEY=your-api-key-here
git push heroku main
heroku open
```

Your app will be live at: `https://resume-tailoring.herokuapp.com`

---

## 🔐 Security Checklist

Before deploying, ensure:

- ✅ `.env` file is in `.gitignore` (already done)
- ✅ Never commit API keys to GitHub
- ✅ Use environment variables for all secrets
- ✅ Rotate API keys regularly
- ✅ Set up HTTPS (handled by platforms automatically)

---

## 📋 Environment Variables Required

All platforms need these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `PORT` | Server port (auto-set by most platforms) | No |
| `NODE_ENV` | Set to `production` | No |

---

## 🔄 GitHub Actions Auto-Deploy

The repository includes a GitHub Actions workflow that:
- ✅ Runs on every push to `main`
- ✅ Tests the build
- ✅ Notifies deployment status

Most platforms (Render, Vercel, Railway) support auto-deploy from GitHub, so every push triggers a new deployment automatically.

---

## 🧪 Testing Your Deployment

After deployment:

1. Visit your deployed URL
2. Go to `/test_openai.html` to verify OpenAI connection
3. Test the resume editor
4. Test AI tailoring feature
5. Test PDF generation

---

## 📊 Platform Comparison

| Platform | Free Tier | Auto-Deploy | Ease | Speed |
|----------|-----------|-------------|------|-------|
| **Render** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐⭐ | Medium |
| **Railway** | ✅ $5 credit | ✅ Yes | ⭐⭐⭐⭐⭐ | Fast |
| **Vercel** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ | Fast |
| **Heroku** | ⚠️ Paid only | ✅ Yes | ⭐⭐⭐ | Medium |

---

## 🛠️ Troubleshooting

### Application Won't Start
- Check logs on your platform dashboard
- Verify `OPENAI_API_KEY` is set correctly
- Ensure Node version >= 18

### OpenAI API Errors
- Verify API key is valid and has credits
- Check API key permissions
- Visit `/test_openai.html` on your deployed URL

### Port Issues
- Most platforms set `PORT` automatically
- Server.js already uses `process.env.PORT || 5001`

---

## 📝 Post-Deployment

After successful deployment:

1. Test all features thoroughly
2. Update your GitHub README with the live URL
3. Set up custom domain (optional)
4. Monitor usage and costs
5. Set up error tracking (Sentry, LogRocket, etc.)

---

## 🎯 Recommended: Render.com Deployment

For most users, **Render.com** is the best choice:
- Free tier available
- Easy setup
- Auto-deploy from GitHub
- Good performance
- No credit card required initially

**Quick Deploy URL**: 
- Go to: https://render.com
- Click "New Web Service"
- Connect: `https://github.com/Iskos1/Resume-Tailoring`
- Add environment variable: `OPENAI_API_KEY`
- Click "Create Web Service"

Done! 🎉

---

## 📞 Support

If you encounter issues:
1. Check platform-specific documentation
2. Review server logs on platform dashboard
3. Verify environment variables are set
4. Test OpenAI connection at `/test_openai.html`

---

**Last Updated**: December 2025

