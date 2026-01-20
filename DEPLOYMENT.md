# Docker & Cloud Deployment Guide

## 🐳 Run Locally with Docker

### Prerequisites
- Install Docker: https://docs.docker.com/get-docker/

### Build & Run Locally

```bash
# Build image
docker build -t rag-assistant .

# Run container
docker run -p 8000:8000 rag-assistant
```

**Access at:** http://localhost:8000/docs

---

## 🚀 Deploy on Render.com (RECOMMENDED - 24/7 Live)

### Step 1: Push to GitHub (✅ Already Done!)

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 3: Create Web Service
1. Dashboard → **"New +"** → **"Web Service"**
2. Connect GitHub repo → Select `rag-knowledge-assistant`
3. Fill in:
   - **Name:** `rag-assistant`
   - **Environment:** `Docker`
   - **Region:** `Oregon` (free tier)
   - **Plan:** `Free`
4. Click **"Create Web Service"**

### Step 4: Wait for Deployment
- Render will automatically:
  - Build Docker image
  - Deploy container
  - Give you a live URL

✅ **Your app will be live at:** `https://rag-assistant.onrender.com`

**Example API calls:**
```bash
# Ingest
curl -X POST https://rag-assistant.onrender.com/ingest

# Query
curl -X GET "https://rag-assistant.onrender.com/query?q=What%20is%20this%20about?"

# Swagger docs
https://rag-assistant.onrender.com/docs
```

---

## 💾 How It Works

✅ **Local Development:**
```bash
# Build image
docker build -t rag-assistant .

# Run with compose
docker-compose up
```

✅ **Production (Render):**
- Render pulls from GitHub
- Builds Dockerfile automatically
- Runs container 24/7
- Auto-restarts if crashes
- Free SSL/HTTPS certificate

✅ **Even If You Delete Local Files:**
- GitHub has all code ✓
- Docker image in Render registry ✓
- Data persists on Render ✓
- URL stays live 24/7 ✓

---

## 📊 Container Architecture

```
Your Laptop (Development)
    ↓
    Docker Build → Image
    ↓
    Docker Run → Container (local testing)
    ↓
Git Push → GitHub
    ↓
Render.com (Production)
    ↓
    Pulls from GitHub
    ↓
    Builds Docker Image
    ↓
    Runs Container 24/7
    ↓
Public URL (LIVE!)
```

---

## 🔧 Environment Variables (Optional)

If using Render, add environment variables:

1. Go to your Render service
2. **Settings** → **Environment**
3. Add:
   ```
   OPENAI_API_KEY=your_key_here (optional)
   ```

---

## ⚠️ Important Notes

### File Size
- Model files (1.5GB) will be included in Docker image
- Free tier has limits, may need paid plan for large models
- Alternative: Use HuggingFace inference API instead

### Cost
- **Render Free Tier:** Free with auto-sleep after 15 min inactivity
- **Render Paid:** $7/month for always-on (recommended for 24/7)

### Auto-Sleep Solution
If using free tier:
- Deploy stays live but auto-sleeps after 15 min of inactivity
- Solution: Use uptimerobot.com to ping your URL every 5 min (keeps it awake)

---

## ✅ Deployment Checklist

- [x] Dockerfile created
- [x] .dockerignore created
- [x] Code pushed to GitHub
- [ ] Create Render account
- [ ] Connect GitHub repo to Render
- [ ] Deploy container
- [ ] Test live URL
- [ ] Share URL with people

---

## Next Steps

1. **Go to https://render.com/auth/github**
2. **Create new Web Service**
3. **Select your `rag-knowledge-assistant` repo**
4. **Choose Docker as environment**
5. **Click Deploy**

**Takes ~5-10 minutes to deploy.**

Once live, everyone can access your RAG app 24/7! 🎉
