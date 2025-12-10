"""
ResumeEngine - Fastest Resume Tailoring
Paste URL → Get Tailored Resume in seconds

Environment Variables Required:
  GEMINI_API_KEY - Google Gemini API key (https://makersuite.google.com/app/apikey)
  ANTHROPIC_API_KEY - Anthropic Claude API key (https://console.anthropic.com/)
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_file, Response
from dotenv import load_dotenv
import google.generativeai as genai
import anthropic
from fpdf import FPDF
import tempfile
import urllib.request
from html.parser import HTMLParser
from prompts.master_prompt import build_tailoring_prompt, SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

# Config
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ============================================
# AI CLIENT ABSTRACTION
# ============================================

class AIClient:
    """
    Unified AI client supporting both Gemini and Claude.
    Default: Gemini (faster)
    Quality: Claude (better reasoning)
    """
    
    def __init__(self):
        self.gemini_model = None
        self.claude_client = None
        
        # Initialize Gemini if available
        if GEMINI_API_KEY:
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize Claude if available
        if ANTHROPIC_API_KEY:
            self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def generate(self, prompt: str, model: str = "gemini", system_prompt: str = None) -> str:
        """
        Generate text using specified AI model.
        
        Args:
            prompt: The user prompt/message
            model: "gemini" (default, faster) or "claude" (quality)
            system_prompt: Optional system instructions (used by Claude)
        
        Returns:
            Generated text response
        
        Raises:
            ValueError: If requested model is not available
            Exception: On API errors
        """
        if model == "gemini":
            return self._generate_gemini(prompt, system_prompt)
        elif model == "claude":
            return self._generate_claude(prompt, system_prompt)
        else:
            raise ValueError(f"Unknown model: {model}. Use 'gemini' or 'claude'.")
    
    def _generate_gemini(self, prompt: str, system_prompt: str = None) -> str:
        """Generate using Google Gemini API."""
        if not self.gemini_model:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY in .env")
        
        # Gemini includes system prompt in the main prompt
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        try:
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _generate_claude(self, prompt: str, system_prompt: str = None) -> str:
        """Generate using Anthropic Claude API."""
        if not self.claude_client:
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env")
        
        try:
            message = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt or "You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def is_available(self, model: str) -> bool:
        """Check if a model is configured and available."""
        if model == "gemini":
            return self.gemini_model is not None
        elif model == "claude":
            return self.claude_client is not None
        return False


# Global AI client instance
ai_client = AIClient()

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
    """Professional PDF resume generator with clean styling."""
    
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)
        
    def header(self):
        pass  # No header
        
    def footer(self):
        pass  # No footer
    
    def add_content(self, text):
        """Parse resume text and add formatted content to PDF."""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                self.ln(3)
                continue
            
            # Detect section headers (ALL CAPS lines)
            if self._is_section_header(line):
                self.ln(4)
                self.set_font('Helvetica', 'B', 11)
                self.set_text_color(30, 41, 59)  # Slate-800
                self.cell(0, 7, line, ln=True)
                self.set_draw_color(148, 163, 184)  # Slate-400
                self.line(20, self.get_y(), 190, self.get_y())
                self.ln(2)
                self.set_font('Helvetica', '', 10)
                self.set_text_color(51, 65, 85)  # Slate-700
                continue
            
            # Detect name (first non-empty line, typically)
            if i == 0 or (i == 1 and not lines[0].strip()):
                self.set_font('Helvetica', 'B', 16)
                self.set_text_color(15, 23, 42)  # Slate-900
                self.cell(0, 10, line, ln=True, align='C')
                self.set_font('Helvetica', '', 10)
                self.set_text_color(51, 65, 85)
                continue
            
            # Contact info (lines with @ or phone patterns near top)
            if i < 5 and ('@' in line or '|' in line or 'linkedin' in line.lower()):
                self.set_font('Helvetica', '', 9)
                self.set_text_color(100, 116, 139)  # Slate-500
                self.cell(0, 5, line, ln=True, align='C')
                self.set_font('Helvetica', '', 10)
                self.set_text_color(51, 65, 85)
                continue
            
            # Bullet points
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                bullet_text = line.lstrip('•-* ').strip()
                self.set_x(25)
                self.set_font('Helvetica', '', 10)
                self.multi_cell(165, 5, '• ' + bullet_text)
                continue
            
            # Job title / Company lines (often formatted as "Title | Company | Date")
            if '|' in line and len(line) < 100:
                self.set_font('Helvetica', 'B', 10)
                self.multi_cell(0, 5, line)
                self.set_font('Helvetica', '', 10)
                continue
            
            # Regular text
            self.multi_cell(0, 5, line)
    
    def _is_section_header(self, line):
        """Check if line is a section header."""
        # All caps and reasonable length
        if line.isupper() and 3 <= len(line) <= 40:
            return True
        # Common section headers
        headers = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'SUMMARY', 'PROJECTS', 
                   'CERTIFICATIONS', 'AWARDS', 'PUBLICATIONS', 'WORK EXPERIENCE',
                   'PROFESSIONAL EXPERIENCE', 'TECHNICAL SKILLS']
        return line.upper() in headers


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
    MAIN ENDPOINT: URL or Text → Tailored Resume
    Accepts either job_url OR job_text parameter.
    """
    start_time = time.perf_counter()
    
    if not GEMINI_API_KEY:
        return jsonify({"error": "Set GEMINI_API_KEY in .env file"}), 400
    
    data = request.get_json()
    job_url = data.get('job_url', '').strip()
    job_text_input = data.get('job_text', '').strip()
    
    # Validate: require either job_url OR job_text (not both empty, not both provided)
    if not job_url and not job_text_input:
        return jsonify({"error": "Provide either job_url or job_text"}), 400
    
    # Load resume
    resume_data = load_resume()
    resume = resume_data.get('content', '')
    
    if not resume:
        return jsonify({"error": "Save your resume first"}), 400
    
    try:
        scrape_start = time.perf_counter()
        
        # Get job description from text or URL
        if job_text_input:
            # Direct text input - skip scraping entirely
            job_text = job_text_input[:8000]
            job_title, company = extract_job_info(job_text)
        else:
            # Scrape URL
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
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
    """Generate styled PDF from tailored resume."""
    data = request.get_json()
    content = data.get('resume_content', '')
    job_title = data.get('job_title', 'Tailored')
    
    if not content:
        return jsonify({"error": "No content"}), 400
    
    pdf = ResumePDF()
    
    # Clean content for PDF compatibility
    content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.add_content(content)
    
    # Save to temp file
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp.name)
    
    # Clean job title for filename
    import re
    safe_title = re.sub(r'[^\w\s-]', '', job_title)[:30].strip().replace(' ', '_')
    from datetime import datetime
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"Resume_{safe_title}_{date_str}.pdf"
    
    return send_file(
        temp.name,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


# ============================================
# SSE STREAMING ENDPOINT
# ============================================

@app.route('/api/stream-tailor', methods=['POST'])
def stream_tailor():
    """
    SSE Streaming endpoint for real-time resume tailoring.
    Streams AI response chunks as Server-Sent Events.
    
    Request JSON:
        - job_url: URL to scrape (optional if job_text provided)
        - job_text: Direct job description text (optional if job_url provided)
        - model: "gemini" (default, faster) or "claude" (quality)
    
    Response: SSE stream with data chunks
    """
    data = request.get_json()
    
    job_url = data.get('job_url', '').strip()
    job_text = data.get('job_text', '').strip()
    model = data.get('model', 'gemini')
    
    # Validate input
    if not job_url and not job_text:
        return jsonify({"error": "Provide either job_url or job_text"}), 400
    
    # Validate model
    if model not in ['gemini', 'claude']:
        return jsonify({"error": "Model must be 'gemini' or 'claude'"}), 400
    
    # Check AI availability
    if not ai_client.is_available(model):
        return jsonify({"error": f"{model.title()} API key not configured"}), 400
    
    # Load resume
    resume_data = load_resume()
    resume = resume_data.get('content', '')
    
    if not resume:
        return jsonify({"error": "Save your resume first"}), 400
    
    # Get job description
    if job_text:
        # Direct text input - use as is
        job_description = job_text[:8000]
        job_title, company = extract_job_info(job_text)
    else:
        # Scrape URL
        if not job_url.startswith(('http://', 'https://')):
            job_url = 'https://' + job_url
        
        job_description = scrape_url(job_url)
        
        if len(job_description) < 50:
            return jsonify({"error": "Could not read job posting"}), 400
        
        job_title, company = extract_job_info(job_description)
    
    job_title = job_title or "Position"
    company = company or "Company"
    
    def generate_stream():
        """Generator function for SSE streaming."""
        try:
            # Send metadata first
            metadata = json.dumps({
                "type": "metadata",
                "job_title": job_title,
                "company": company
            })
            yield f"data: {metadata}\n\n"
            
            # Build comprehensive prompt using master prompt
            prompt = build_tailoring_prompt(
                resume=resume,
                job_description=job_description,
                job_title=job_title,
                company=company
            )

            # Stream with Gemini
            if model == "gemini" and ai_client.gemini_model:
                response = ai_client.gemini_model.generate_content(
                    prompt,
                    stream=True
                )
                
                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        chunk_data = json.dumps({
                            "type": "chunk",
                            "content": chunk.text
                        })
                        yield f"data: {chunk_data}\n\n"
                
                # Send completion signal with full response for parsing
                complete_data = json.dumps({
                    "type": "complete",
                    "full_response": full_response
                })
                yield f"data: {complete_data}\n\n"
            
            elif model == "claude" and ai_client.claude_client:
                # Stream with Claude using messages.stream()
                system_prompt = SYSTEM_PROMPT
                
                full_response = ""
                with ai_client.claude_client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        chunk_data = json.dumps({
                            "type": "chunk",
                            "content": text
                        })
                        yield f"data: {chunk_data}\n\n"
                
                # Send completion signal
                complete_data = json.dumps({
                    "type": "complete",
                    "full_response": full_response
                })
                yield f"data: {complete_data}\n\n"
            
            else:
                # Fallback for unknown model
                error_data = json.dumps({
                    "type": "error",
                    "message": f"Model {model} not available or not configured"
                })
                yield f"data: {error_data}\n\n"
        
        except Exception as e:
            error_data = json.dumps({
                "type": "error",
                "message": str(e)
            })
            yield f"data: {error_data}\n\n"
    
    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )


# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*50)
    print("  RESUME ENGINE - Super Fast Resume Tailoring")
    print("="*50)
    
    # Check API keys
    if not GEMINI_API_KEY and not ANTHROPIC_API_KEY:
        print("\n⚠️  No AI API keys configured!")
        print("   Set GEMINI_API_KEY and/or ANTHROPIC_API_KEY in .env file")
        print("   Gemini: https://makersuite.google.com/app/apikey")
        print("   Claude: https://console.anthropic.com/")
    else:
        if GEMINI_API_KEY:
            print("✓ Gemini API configured")
        if ANTHROPIC_API_KEY:
            print("✓ Claude API configured")
    
    # Development vs Production
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"\n🚀 http://localhost:5000")
    print(f"   Mode: {'Development' if debug_mode else 'Production'}")
    print("="*50 + "\n")
    
    app.run(debug=debug_mode, port=5000)
