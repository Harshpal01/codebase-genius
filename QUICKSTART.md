# Quick Start Guide

Get Codebase Genius running in 5 minutes!

---

## ✅ Prerequisites

- Python 3.8+
- Git
- Gemini API key (already configured!)

---

## 🚀 Start the System

### Backend

To start the AI-powered backend:

```bash
cd backend
.\venv\Scripts\jac.exe serve main.jac
```

Server runs at: **http://localhost:8000**

### Frontend (Already Running)

The frontend is running on **http://localhost:8501**

To restart:
```bash
cd C:\Users\Administrator\CascadeProjects\codebase_genius\frontend
streamlit run app.py
```

---

## 🎯 Test It Now!

### Option 1: Web UI

1. Open **http://localhost:8501**
2. Go to "Generate Documentation" tab
3. Enter: `https://github.com/pallets/flask`
4. Click "Generate Docs"
5. View in "View Documentation" tab

### Option 2: API

```powershell
# Generate documentation
$body = @{
    github_url = "https://github.com/pallets/flask"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/walker/generate_docs" `
    -Method Post -Body $body -ContentType "application/json"

# View documentation
$body = @{
    repo_name = "flask"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/walker/get_documentation" `
    -Method Post -Body $body -ContentType "application/json"
```

---

## 📁 Output Location

Generated docs: `backend\outputs\<repo-name>\docs.md`

---

## 🤖 AI Features

The backend now uses Gemini AI for:
- Intelligent project overviews
- Context-aware installation guides
- Professional documentation generation

---

## 📚 More Information

- **Full Documentation:** See `README.md`
- **Testing Guide:** See `TESTING_GUIDE.md`
- **Current Status:** See `STATUS.md`

---

**Ready to generate documentation! 🚀**
