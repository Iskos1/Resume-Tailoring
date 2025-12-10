# ⚡ ResumeEngine

**Fastest Resume Tailoring** - Paste a job URL, get a tailored resume in seconds.

## How It Works

1. **Paste your master resume** (once)
2. **Paste any job URL**
3. **Get a tailored resume** optimized for that job

## Features

- 🚀 **Fast** - Tailors resume in ~10 seconds
- 🎯 **XYZ Method** - Every bullet uses "Accomplished X, measured by Y, by doing Z"
- 📊 **Match Score** - See how well you fit the job (0-100%)
- 📄 **PDF Download** - One-click download

## Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/resume-engine.git
cd resume-engine

# Install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add API key
echo "GEMINI_API_KEY=your_key_here" > .env
# Get key at: https://makersuite.google.com/app/apikey

# Run
python app.py
```

Open **http://localhost:5000**

## Tech Stack

- **Backend**: Flask + Google Gemini AI
- **Frontend**: Vanilla HTML/CSS/JS
- **PDF**: fpdf2

## License

MIT
