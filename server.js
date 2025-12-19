import express from 'express';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import https from 'https';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();

// OpenAI Setup
const client = new OpenAI({ 
    apiKey: process.env.OPENAI_API_KEY,
    httpAgent: new https.Agent({ rejectUnauthorized: false })
});

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Data Setup
const DATA_DIR = 'data';
const RESUME_FILE = path.join(DATA_DIR, 'master_resume.json');
const TAILORED_RESUME_FILE = path.join(DATA_DIR, 'tailored_resume.json');
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

// Load Resume
function loadResume(isTailored = false) {
    const file = isTailored ? TAILORED_RESUME_FILE : RESUME_FILE;
    if (fs.existsSync(file)) {
        return JSON.parse(fs.readFileSync(file, 'utf8'));
    }
    return { name: '', contact: {}, skills: [], experience: [], education: [], projects: [], awards: [] };
}

// Save Resume
function saveResume(data, isTailored = false) {
    const file = isTailored ? TAILORED_RESUME_FILE : RESUME_FILE;
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

// Routes
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));
app.get('/tailored', (req, res) => res.sendFile(path.join(__dirname, 'public', 'tailored.html')));
app.get('/preview', (req, res) => res.sendFile(path.join(__dirname, 'public', 'resume_pdf.html')));
app.get('/api/resume', (req, res) => res.json(loadResume()));
app.get('/api/resume/tailored', (req, res) => res.json(loadResume(true)));
app.post('/api/resume', (req, res) => { saveResume(req.body); res.json({ success: true }); });
app.post('/api/resume/tailored', (req, res) => { saveResume(req.body, true); res.json({ success: true }); });
app.post('/api/copy-to-tailored', (req, res) => { 
    const master = loadResume(false);
    saveResume(master, true);
    res.json({ success: true }); 
});

// Test OpenAI Route
app.get('/api/test-openai', async (req, res) => {
    try {
        const response = await client.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: 'You are a helpful assistant.' },
                { role: 'user', content: 'Say "OpenAI connection successful!" and nothing else.' }
            ],
            max_tokens: 50
        });

        res.json({ 
            success: true, 
            message: response.choices[0].message.content.trim(),
            model: response.model
        });
    } catch (error) {
        let msg = error.message;
        if (error.status === 401) msg = 'Invalid API key - please check your OPENAI_API_KEY';
        if (error.status === 429) msg = 'Rate limit exceeded';
        res.status(500).json({ error: msg, details: error.message });
    }
});

// AI Tailor Route - Updates tailored resume
app.post('/api/tailor', async (req, res) => {
    try {
        const { job_description } = req.body;
        const resume = loadResume(false); // Load master resume

        // Using gpt-4o for comprehensive reasoning and analysis
        const response = await client.chat.completions.create({
            model: 'gpt-4o',
            messages: [
                { role: 'system', content: 'You are an elite resume tailoring specialist who creates perfectly tailored resumes while maintaining 100% truthfulness. You always return valid JSON without any markdown formatting or explanations.' },
                { role: 'user', content: `Your task is to create a perfectly tailored resume that matches the job description while maintaining 100% truthfulness.

MASTER RESUME (Analyze this deeply - understand who this person is, their career journey, skills, and accomplishments):
${JSON.stringify(resume, null, 2)}

JOB DESCRIPTION (Analyze what they're looking for - keywords, technologies, skills, experience type, and ideal candidate profile):
${job_description}

COMPREHENSIVE TAILORING PROCESS:

STEP 1: DEEP ANALYSIS OF MASTER RESUME
- Analyze line by line, word by word to understand:
  * What type of professional this person is
  * Their core competencies and strengths
  * The work they have accomplished throughout their career
  * Their technical skills, tools, and methodologies
  * Their leadership, problem-solving, and impact-making abilities
- Remember and internalize this profile for the tailoring process

STEP 2: DEEP ANALYSIS OF JOB DESCRIPTION
- Identify what the employer is looking for:
  * Required and preferred technologies/tools
  * Key skills and competencies
  * Experience level and type
  * Industry-specific keywords and terminology
  * Problem-solving approaches they value
  * Cultural fit indicators
- Build a profile of the ideal candidate they want
- Extract exact keywords and phrases they're using

STEP 3: STRATEGIC SELECTION AND CONNECTION
3.1 SELECTION PROCESS:
- Select the most relevant projects and work experiences that align with job requirements
- Prioritize experiences that demonstrate the exact skills they're seeking
- Choose projects that showcase similar technologies or transferable skills

3.2 CREATIVE TAILORING (This is critical - be strategic and thorough):
- Tailor each selected experience toward what they're looking for
- Reframe accomplishments using their keywords and terminology WITHOUT lying or creating deception
- If they use specific keywords not in the master resume, find ways to professionally integrate related concepts you DO have
- Build compelling stories for each project/experience that directly address job requirements
- Show clear connections between your experience and their needs
- Emphasize metrics and outcomes that matter to this specific role

STEP 4: FORMAT AND POLISH FOR PERFECTION
CRITICAL FORMATTING RULES:
✓ Keep resume to EXACTLY 1 page worth of content
✓ Each project/experience description must be EXACTLY 4 SENTENCES describing achievements, followed by a 5TH SENTENCE that lists technologies/tools used
✓ Structure each project description as:
  - Sentence 1: Primary accomplishment with metrics
  - Sentence 2: Secondary accomplishment or methodology
  - Sentence 3: Another key achievement or impact
  - Sentence 4: Final accomplishment or outcome
  - Sentence 5: "Technologies/Skills: [comma-separated list]"
✓ Keep descriptions concise, impactful, and metrics-driven
✓ Use strong action verbs and quantifiable results
✓ Ensure the resume looks clean, professional, and ATS-friendly

KEYWORD OPTIMIZATION:
- Naturally weave in job description keywords throughout the resume
- Prioritize skills section to list most relevant technologies first
- Use exact terminology from the job posting where applicable
- Ensure technical terms match their preferred nomenclature

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON with the exact same structure as the input resume
- Maintain all field names and data types
- Keep all information truthful - never fabricate experience or skills
- Ensure JSON is properly formatted (no markdown, no explanations, no code blocks)
- Make the tailored resume read naturally while being optimized for this specific job

Return the complete tailored resume as valid JSON:` }
            ]
        });

        const tailoredResume = JSON.parse(response.choices[0].message.content.trim());
        saveResume(tailoredResume, true); // Save to tailored resume
        res.json(tailoredResume);
    } catch (error) {
        let msg = error.message;
        if (error.status === 401) msg = 'Invalid API key';
        if (error.status === 429) msg = 'Rate limit exceeded';
        res.status(500).json({ error: msg });
    }
});

// Start Server
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`✅ Server running at http://localhost:${PORT}`));
