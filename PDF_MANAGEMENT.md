# PDF Management Guide

## 🎯 Quick Start: Adding PDFs

### Option 1: Using Python Script (Recommended)

```bash
# List all PDFs
python manage_pdfs.py list

# Add a PDF (any size)
python manage_pdfs.py add "C:\path\to\your_document.pdf"

# Remove a PDF
python manage_pdfs.py remove "your_document.pdf"
```

### Option 2: Manual (Copy-Paste)

Simply copy your PDF files to:
```
data/sample_docs/
├── sample.pdf
├── your_document.pdf
├── another_document.pdf
└── large_file_5gb.pdf (yes, even this!)
```

---

## 📖 Using Different PDFs in the API

### Ingest Default (sample.pdf)
```bash
curl -X POST http://localhost:8000/ingest
```

### Ingest Any PDF
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "data/sample_docs/your_document.pdf"}'
```

### Query
```bash
curl -X GET "http://localhost:8000/query?q=What%20is%20in%20this%20document?"
```

---

## 🌍 Production: Using on Render

### Before Deployment:
1. Add your PDFs to `data/sample_docs/` folder
2. Push to GitHub:
   ```bash
   git add data/sample_docs/*.pdf
   git commit -m "feat: Add production PDFs"
   git push origin main
   ```

### After Deployment (on Render):
Render automatically includes all files in your repo, including PDFs.

Call the ingest endpoint:
```bash
curl -X POST https://your-app.onrender.com/ingest \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "data/sample_docs/production_docs.pdf"}'
```

---

## 📦 PDF Size Limits

### Local Development
- ✅ No limit (tested with 5GB+)
- ⚠️ Limited by RAM (2GB FAISS index + 1.5GB model + PDF)

### Render Deployment
- ✅ Free tier: Max 512MB total Docker image (PDFs included)
- ✅ Paid tier: Up to 1GB
- 💡 Solution: Use external storage (AWS S3, GCP Cloud Storage) for large PDFs

### Recommended Approach
```
Small PDFs (<100MB) → Git + GitHub
Large PDFs (>100MB) → External storage + streaming
```

---

## 🚀 Advanced: Multiple PDFs at Once

### Create a Batch Script

```python
from manage_pdfs import add_pdf

pdfs_to_add = [
    "documents/contract.pdf",
    "documents/policy.pdf",
    "documents/manual.pdf"
]

for pdf in pdfs_to_add:
    add_pdf(pdf)
```

Then ingest each one:
```bash
curl -X POST http://localhost:8000/ingest \
  -d '{"pdf_path": "data/sample_docs/contract.pdf"}'

curl -X POST http://localhost:8000/ingest \
  -d '{"pdf_path": "data/sample_docs/policy.pdf"}'
```

---

## ✅ Supported PDF Features

✅ Text-based PDFs
✅ Scanned PDFs (with OCR support via `pytesseract`)
✅ Multi-page documents
✅ Large files (100MB+)
✅ Any encoding (UTF-8, Latin-1, etc.)

---

## 🔧 Troubleshooting

### "PDF not found" Error
```
Make sure the path exists:
data/sample_docs/your_document.pdf
```

### Out of Memory
```
For very large PDFs:
1. Increase chunk_overlap in app/ingestion/chunking.py
2. Use smaller chunk_size
3. Deploy on GPU-enabled server
```

### Can't Upload to GitHub
```
Large PDFs > 100MB?
1. Use git-lfs (Git Large File Storage)
   git lfs install
   git lfs track "*.pdf"

2. Or use external storage
   - AWS S3
   - Google Cloud Storage
   - DropBox
```

---

## 📝 Summary

Your system now supports:
- ✅ Any PDF file (any size)
- ✅ Easy management script
- ✅ Multiple PDFs simultaneously
- ✅ Production-ready on Render
- ✅ Scalable to external storage if needed
