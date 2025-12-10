"""
ResumeEngine - Fastest Resume Tailoring
Paste URL → Get Tailored Resume in seconds
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import urllib.request
from html.parser import HTMLParser

load_dotenv()

app = Flask(__name__)

# Config
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RESUME_FILE = os.path.join(DATA_DIR, 'master_resume.json')


# ============================================
# HELPERS
# ============================================

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_resume():
    ensure_data_dir()
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"content": ""}

def save_resume(content):
    ensure_data_dir()
    with open(RESUME_FILE, 'w') as f:
        json.dump({"content": content}, f)


# ============================================
# JOB SCRAPER
# ============================================

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.skip = True
            
    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.skip = False
            
    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.text.append(text)

def scrape_url(url):
    """Extract text from job posting URL"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        parser = TextExtractor()
        parser.feed(html)
        text = ' '.join(parser.text)
        
        # Clean up
        import re
        text = re.sub(r'\s+', ' ', text)
        return text[:8000]
    except Exception as e:
        return ""

def extract_job_info(text):
    """Extract job title and company from text"""
    import re
    
    title = None
    company = None
    
    # Common patterns
    patterns = [
        r'(?:job\s*title|position|role)\s*[:\-]?\s*([A-Za-z\s]+)',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\s+at\s+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text[:1000], re.IGNORECASE)
        if match:
            title = match.group(1).strip()[:50]
            break
    
    company_patterns = [
        r'(?:company|employer|at)\s*[:\-]?\s*([A-Za-z0-9\s&]+)',
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text[:1000], re.IGNORECASE)
        if match:
            company = match.group(1).strip()[:30]
            break
    
    return title, company


# ============================================
# PDF GENERATOR
# ============================================

class ResumePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font('Helvetica', '', 11)
        
    def add_content(self, text):
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                self.ln(4)
            elif line.isupper() and len(line) < 50:
                self.ln(6)
                self.set_font('Helvetica', 'B', 12)
                self.cell(0, 8, line, ln=True)
                self.set_font('Helvetica', '', 11)
            elif line.startswith('•') or line.startswith('-'):
                self.multi_cell(0, 6, line)
            else:
                self.multi_cell(0, 6, line)


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/master-resume', methods=['GET'])
def get_resume():
    data = load_resume()
    return jsonify(data)


@app.route('/api/master-resume', methods=['POST'])
def save_resume_api():
    data = request.get_json()
    content = data.get('content', '')
    save_resume(content)
    return jsonify({"success": True})


@app.route('/api/quick-tailor', methods=['POST'])
def quick_tailor():
    """
    MAIN ENDPOINT: URL → Tailored Resume
    """
    start_time = time.perf_counter()
    
    if not GEMINI_API_KEY:
        return jsonify({"error": "Set GEMINI_API_KEY in .env file"}), 400
    
    data = request.get_json()
    job_url = data.get('job_url', '').strip()
    
    if not job_url:
        return jsonify({"error": "Job URL required"}), 400
    
    # Load resume
    resume_data = load_resume()
    resume = resume_data.get('content', '')
    
    if not resume:
        return jsonify({"error": "Save your resume first"}), 400
    
    try:
        # Step 1: Scrape
        scrape_start = time.perf_counter()
        
        if not job_url.startswith(('http://', 'https://')):
            job_url = 'https://' + job_url
        
        job_text = scrape_url(job_url)
        
        if len(job_text) < 50:
            return jsonify({"error": "Could not read job posting"}), 400
        
        job_title, company = extract_job_info(job_text)
        job_title = job_title or "Position"
        company = company or "Company"
        
        scrape_time = time.perf_counter() - scrape_start
        
        # Step 2: AI Tailor
        tailor_start = time.perf_counter()
        
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Tailor this resume for the job. Use XYZ format for bullets.

RESUME:
{resume[:3500]}

JOB ({job_title} at {company}):
{job_text[:2000]}

Return JSON only:
{{"tailored_resume": "Full tailored resume text", "compatibility_score": 0-100}}"""

        response = model.generate_content(prompt)
        text = response.text
        
        # Parse JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        result = json.loads(text.strip())
        
        tailor_time = time.perf_counter() - tailor_start
        total_time = time.perf_counter() - start_time
        
        return jsonify({
            "success": True,
            "job_title": job_title,
            "company": company,
            "compatibility_score": result.get("compatibility_score", 0),
            "tailored_resume": result.get("tailored_resume", ""),
            "timing": {
                "scrape": round(scrape_time, 2),
                "tailor": round(tailor_time, 2),
                "total": round(total_time, 2)
            }
        })
        
    except json.JSONDecodeError:
        return jsonify({"error": "AI response error. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Generate PDF from tailored resume"""
    data = request.get_json()
    content = data.get('resume_content', '')
    
    if not content:
        return jsonify({"error": "No content"}), 400
    
    pdf = ResumePDF()
    
    # Clean content
    content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.add_content(content)
    
    # Save to temp file
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp.name)
    
    return send_file(
        temp.name,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='tailored_resume.pdf'
    )


# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  RESUME ENGINE")
    print("="*50)
    
    if not GEMINI_API_KEY:
        print("\n⚠️  Set GEMINI_API_KEY in .env file")
        print("   Get key: https://makersuite.google.com/app/apikey")
    
    print("\n🚀 http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)
