# Deploy to Google Cloud Run

## ✅ Why Google Cloud Run?

| Feature | Render | Google Cloud Run |
|---------|--------|------------------|
| **Free Memory** | 512MB | 4GB ✅ |
| **CPU** | Limited | 2 vCPU ✅ |
| **Free Tier** | Limited | Very generous ✅ |
| **Cold Start** | None | 3-5s |
| **Perfect for RAG** | ❌ OOM | ✅ YES |

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Google Cloud SDK

**Windows:**
- Download: https://cloud.google.com/sdk/docs/install
- Run installer: `GoogleCloudSDKInstaller.exe`
- Restart terminal after installation

**Verify installation:**
```bash
gcloud --version
```

---

### Step 2: Initialize Google Cloud

```bash
gcloud init
```

**This will:**
1. Open browser to login
2. Select/create a project
3. Set default region (choose `us-central1`)

---

### Step 3: Enable Cloud Run API

```bash
gcloud services enable run
```

---

### Step 4: Deploy!

```bash
cd c:\Users\Asus\rag-knowledge-assistant

gcloud run deploy rag-assistant \
  --source . \
  --memory 1Gi \
  --cpu 2 \
  --timeout 3600 \
  --allow-unauthenticated \
  --region us-central1 \
  --platform managed
```

**This command:**
- Builds Docker image from current directory
- Deploys to Cloud Run
- Sets 1GB memory (enough for TinyLLaMA)
- Sets 2 CPU cores (fast inference)
- Allows unauthenticated requests
- Auto-scales to 0 when idle (free!)

---

### Step 5: Get Your Live URL! 🎉

After deployment (2-3 minutes), you'll see:

```
✓ Deploying...
✓ Creating Revision...
✓ Routing traffic...
Service [rag-assistant] revision [1] has been deployed

Service URL: https://rag-assistant-xxxxx.run.app
```

---

## 🧪 Test Your Live API

```bash
# Test ingest
curl https://rag-assistant-xxxxx.run.app/ingest \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "data/sample_docs/sample.pdf"}'

# Test query
curl "https://rag-assistant-xxxxx.run.app/query?q=what%20is%20in%20this%20document"

# View Swagger docs
curl https://rag-assistant-xxxxx.run.app/docs
```

---

## 📊 Google Cloud Run Free Tier

**Every month you get:**
- ✅ 2 million requests (free)
- ✅ 360,000 GB-seconds CPU (free)
- ✅ 1 GB memory per instance
- ✅ Auto-scaling to 0 when idle
- ✅ No payment required (unless you exceed)

**Example cost if you exceed:**
- $0.24 per 1M requests
- $0.00001667 per GB-second

**Bottom line:** Practically free for your use case! 🎯

---

## 🔄 Update Deployment

### After pushing new code to GitHub:

```bash
gcloud run deploy rag-assistant \
  --source . \
  --memory 1Gi \
  --region us-central1
```

---

## 📝 Environment Variables

Set OPENAI_API_KEY on Cloud Run:

```bash
gcloud run deploy rag-assistant \
  --source . \
  --memory 1Gi \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=your-key-here
```

---

## ✅ Troubleshooting

### Check logs:
```bash
gcloud run logs read rag-assistant --region us-central1
```

### Increase memory if needed:
```bash
gcloud run deploy rag-assistant \
  --memory 2Gi \
  --region us-central1
```

### Delete service:
```bash
gcloud run services delete rag-assistant --region us-central1
```

---

## 🎯 You're All Set!

1. **Install Google Cloud SDK** (if not done)
2. **Run gcloud init**
3. **Run the deploy command** above
4. **Get your live URL** ✅
5. **Test with curl** or Swagger docs

Ready? Let's go! 🚀
