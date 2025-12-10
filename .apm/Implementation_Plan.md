# Super Fast Resume Tailoring Service – APM Implementation Plan
**Memory Strategy:** Dynamic-MD
**Last Modification:** Systematic review complete - restructured Phase 2, split packed tasks.
**Project Overview:** Build a real-time, streaming resume tailoring service with perfection. Features include dual AI (Gemini + Claude), live preview as you type, comprehensive analysis (score breakdown, gap analysis, experience reframing, interview prep, ATS optimization), styled PDF output, and deployment via GitHub + Render.

---

## Phase 1: Foundation – Backend & AI Integration

### Task 1.1 – Add Claude API Integration - Agent_Backend
**Objective:** Integrate Anthropic Claude API alongside existing Gemini.
**Output:** Working Claude API client in `app.py` with abstracted interface.
**Guidance:** Add python-dotenv for ANTHROPIC_API_KEY, create abstracted AI client class.

1. Install `anthropic` package and add to `requirements.txt`
2. Create environment variable setup for `ANTHROPIC_API_KEY` in `.env`
3. Build `AIClient` class with `generate()` method that works with either model
4. Add model selection parameter (default: Gemini for speed, Claude for quality)
5. Test both APIs with simple prompts to verify integration

### Task 1.2 – Implement SSE Streaming Infrastructure - Agent_Backend
**Objective:** Create SSE endpoint infrastructure with Gemini streaming.
**Output:** `/api/stream-tailor` endpoint with working Gemini streaming.
**Guidance:** Use Flask's `Response` with `text/event-stream`. Start with Gemini as it's faster.

1. Create new `/api/stream-tailor` POST endpoint
2. Implement SSE response format with proper CORS and cache headers
3. Build generator function using Gemini's `generate_content(stream=True)`
4. Yield chunks in SSE format: `data: {chunk}\n\n`
5. Add connection error handling and cleanup
6. Test with curl: `curl -N http://localhost:5000/api/stream-tailor`

### Task 1.3 – Add Claude Streaming Support - Agent_Backend
**Objective:** Add Claude streaming to the existing SSE infrastructure.
**Output:** Streaming endpoint supports both Gemini and Claude via parameter.
**Guidance:** **Depends on: Task 1.2 Output.** Claude uses different streaming API.

1. Study Claude's `messages.stream()` API differences from Gemini
2. Add `model` parameter to `/api/stream-tailor` (gemini|claude)
3. Implement Claude streaming generator using `with client.messages.stream()`
4. Unify chunk format between both providers
5. Test Claude streaming independently
6. Test model switching works correctly

### Task 1.4 – Add Job Description Text Input - Agent_Backend
**Objective:** Support direct text paste alongside URL scraping.
**Output:** API accepts both `job_url` and `job_text` parameters.
**Guidance:** Text input is faster and more reliable than scraping.

1. Modify `/api/stream-tailor` to accept `job_text` parameter
2. Add validation: require either `job_url` OR `job_text` (not both, not neither)
3. If `job_text` provided, skip URL scraping entirely
4. Extract job title/company from text using enhanced regex or AI
5. Test with both input methods to verify parity

### Task 1.5 – Build Complete Master Prompt - Agent_AI
**Objective:** Create the comprehensive prompt that produces ALL analysis outputs.
**Output:** Single master prompt file with full JSON schema and instructions.
**Guidance:** This is the core IP. Must produce: tailored_resume, compatibility_score, score_breakdown (4 dimensions), what_you_have, what_you_lack, experience_reframing, bridge_the_gap, interview_prep.

1. Define complete JSON response schema with all fields documented:
   ```json
   {
     "tailored_resume": "string - full resume text with XYZ bullets",
     "compatibility_score": "number 0-100",
     "score_breakdown": {
       "hard_skills_match": "number 0-100",
       "experience_relevance": "number 0-100", 
       "industry_alignment": "number 0-100",
       "seniority_fit": "number 0-100",
       "overall_assessment": "string - 1-2 sentence summary"
     },
     "what_you_have": ["array of matching qualifications"],
     "what_you_lack": ["array of gaps"],
     "experience_reframing": [{
       "original_role": "string",
       "original_focus": "string",
       "reframed_focus": "string",
       "why_this_works": "string",
       "key_transforms": ["array of bullet transformations"]
     }],
     "bridge_the_gap": [{
       "gap": "string",
       "quick_win": "string - this week",
       "medium_term": "string - 1-4 weeks",
       "portfolio_project": "string - optional",
       "resources": [{"name": "", "time": "", "cost": "", "url": ""}]
     }],
     "interview_prep": ["array of 5-7 likely questions"]
   }
   ```
2. Write system prompt with:
   - Role: Expert resume consultant and career coach
   - XYZ bullet format requirement: "Accomplished [X] as measured by [Y] by doing [Z]"
   - ATS optimization: Extract and naturally incorporate job keywords
   - Scoring rubric with examples (what 90% vs 60% vs 30% looks like)
3. Add few-shot examples showing ideal output format
4. Include error prevention: "Return ONLY valid JSON, no markdown formatting"
5. Save prompt as `prompts/master_prompt.py` for easy iteration
6. Test with both Gemini and Claude, validate JSON parsing works

---

## Phase 2: Feature Validation – Test Each Analysis Component

### Task 2.1 – Validate Score Breakdown Quality - Agent_AI
**Objective:** Ensure score breakdown produces accurate, consistent scores.
**Output:** Validated scoring with documented calibration.
**Guidance:** **Depends on: Task 1.5 Output.** Test with diverse job types.

1. Test with 5 different job descriptions (tech, marketing, finance, healthcare, entry-level)
2. Verify scores are logically consistent (can't have 90% skills but 20% overall)
3. Check overall_assessment text matches the numbers
4. Adjust scoring rubric in prompt if calibration is off
5. Document final scoring criteria

### Task 2.2 – Validate Gap Analysis Quality - Agent_AI
**Objective:** Ensure gap analysis is actionable and accurate.
**Output:** Validated gap detection with useful bridge suggestions.
**Guidance:** **Depends on: Task 1.5 Output.** Test with obvious gaps.

1. Test with resume missing obvious requirements (e.g., job needs Python, resume has none)
2. Verify quick_win suggestions are actually quick (< 1 week)
3. Check resource suggestions are real and accessible
4. Validate portfolio_project ideas are feasible
5. Adjust prompt if suggestions are too generic

### Task 2.3 – Validate Experience Reframing Quality - Agent_AI
**Objective:** Ensure reframing provides genuine insight.
**Output:** Validated reframing that reveals transferable value.
**Guidance:** **Depends on: Task 1.5 Output.** This is the "secret sauce."

1. Test with career-change scenario (e.g., teacher → tech)
2. Verify reframed_focus is genuinely different from original
3. Check why_this_works provides convincing reasoning
4. Validate key_transforms show specific bullet improvements
5. Adjust prompt to increase specificity if needed

### Task 2.4 – Validate Interview Prep Quality - Agent_AI
**Objective:** Ensure interview questions target actual weaknesses.
**Output:** Validated questions that help user prepare.
**Guidance:** **Depends on: Task 1.5 Output.** Questions should match gaps.

1. Cross-reference questions with what_you_lack items
2. Verify mix of behavioral and technical questions
3. Check questions are specific to the role, not generic
4. Validate 5-7 question limit is respected
5. Adjust prompt if questions are too generic

### Task 2.5 – Validate ATS Optimization - Agent_AI
**Objective:** Ensure tailored resume includes job keywords naturally.
**Output:** Validated keyword integration without stuffing.
**Guidance:** **Depends on: Task 1.5 Output.** Keywords should flow naturally.

1. Extract keywords from job description manually
2. Check tailored_resume contains those keywords
3. Verify keywords are used in context, not stuffed
4. Check section order is ATS-friendly (Experience before Education)
5. Test with online ATS checker if available

---

## Phase 3: Frontend – Real-Time Interface

### Task 3.1 – Redesign Input Section - Agent_Frontend
**Objective:** Add text paste option as primary input method.
**Output:** Updated input UI with tabs for Text vs URL.
**Guidance:** Text paste should be prominent; URL is secondary.

1. Create tabbed interface with "📝 Paste Text" and "🔗 URL" tabs
2. Text tab: Large textarea (min 300px height) for job description
3. URL tab: Keep existing URL input field
4. Add character count indicator below textarea
5. Style tabs consistently with dark theme
6. Default to Text tab on load

### Task 3.2 – Implement Request Debouncing & Cancellation - Agent_Frontend
**Objective:** Debounce input and cancel in-flight requests on new input.
**Output:** Smart input handling that avoids API spam.
**Guidance:** Critical for "real-time as you type" without overwhelming server.

1. Create debounce utility: `debounce(fn, 500ms)`
2. Track current AbortController for in-flight requests
3. On new input: cancel previous request, start debounce timer
4. Show "typing..." indicator during debounce period
5. Only fire request after 500ms of no typing
6. Test rapid typing doesn't cause race conditions

### Task 3.3 – Implement Streaming Response Display - Agent_Frontend
**Objective:** Connect to SSE endpoint and render streaming response.
**Output:** Real-time text display as AI generates response.
**Guidance:** **Depends on: Task 3.2 Output.** Use EventSource API.

1. Create EventSource connection to `/api/stream-tailor`
2. Handle `onmessage` events, append text chunks to display
3. Show typing cursor animation during streaming
4. On stream complete, parse full JSON for structured data
5. Handle `onerror` with retry logic or error display
6. Clean up EventSource on component unmount or new request

### Task 3.4 – Build Score Breakdown UI - Agent_Frontend
**Objective:** Display visual score breakdown with animated bars.
**Output:** Score gauge + 4 breakdown bars with percentages.
**Guidance:** **Depends on: Task 3.3 Output.** CSS styles already exist.

1. Connect score_breakdown JSON to existing UI elements
2. Animate circular score gauge on data load
3. Animate 4 breakdown bars with staggered timing
4. Color-code bars: green (70+), yellow (40-69), red (<40)
5. Display overall_assessment text below score
6. Test animations are smooth (60fps)

### Task 3.5 – Build Analysis Panels UI - Agent_Frontend
**Objective:** Display all analysis sections with real data.
**Output:** Populated cards for gaps, reframing, interview prep.
**Guidance:** **Depends on: Task 3.3 Output.** Components exist, need data binding.

1. Populate what_you_have list with green checkmarks
2. Populate what_you_lack list with red indicators
3. Render experience_reframing cards with before/after comparison
4. Display bridge_the_gap with timeline visualization
5. Show interview_prep as numbered question list
6. Hide sections gracefully if data is empty

---

## Phase 4: PDF & Polish

### Task 4.1 – Create Styled PDF Template - Agent_PDF
**Objective:** Design professional, clean PDF resume template.
**Output:** HTML/CSS template for resume PDF generation.
**Guidance:** Clean minimal aesthetic as requested.

1. Design HTML template with semantic sections (header, experience, skills, education)
2. Create CSS with clean typography (system fonts for compatibility)
3. Style section headers with subtle borders
4. Format bullet points with proper indentation
5. Add responsive spacing between sections
6. Test template renders correctly in browser

### Task 4.2 – Build Resume Text Parser - Agent_Backend
**Objective:** Parse AI-generated resume text into structured sections.
**Output:** Parser function that extracts name, contact, sections from text.
**Guidance:** AI output is text; need structure for template rendering.

1. Define section markers to detect (EXPERIENCE, SKILLS, EDUCATION, etc.)
2. Build regex patterns to extract contact info (email, phone, LinkedIn)
3. Create parser that returns structured dict with all sections
4. Handle variations in AI output format
5. Add fallback for unparseable sections
6. Test with multiple AI-generated resumes

### Task 4.3 – Implement PDF Generation Endpoint - Agent_Backend
**Objective:** Generate styled PDF from parsed resume.
**Output:** Updated `/api/download-pdf` using template + parser.
**Guidance:** **Depends on: Task 4.1 and Task 4.2 Output.** Use fpdf2 (more reliable than WeasyPrint).

1. Update `/api/download-pdf` to use new parser
2. Render HTML template with Jinja2 using parsed data
3. Use fpdf2 for PDF generation (already installed, no system deps)
4. Style PDF to match template design
5. Return PDF with filename: `Resume_[JobTitle]_[Date].pdf`
6. Test download works in browser

### Task 4.4 – Test with Real Resume - Agent_Backend
**Objective:** End-to-end validation with user's actual resume.
**Output:** Working system validated with real data.
**Guidance:** User will provide resume PDF for testing.

1. Request user's resume PDF
2. Extract text (use PyPDF2 or similar)
3. Update master_resume.json with extracted content
4. Test with 3 diverse job descriptions
5. Validate all features produce sensible, accurate output
6. Document any issues and fix

### Task 4.5 – Performance Optimization - Agent_Backend
**Objective:** Achieve <3 second initial response time.
**Output:** Optimized API with measured performance improvements.
**Guidance:** Use Gemini for streaming speed, consider parallel calls.

1. Profile current response times with timing logs
2. Implement parallel processing where possible
3. Consider: Gemini for resume, Claude for deep analysis
4. Add in-memory caching for repeated job descriptions
5. Measure improvements, document before/after times
6. Target: First token < 1s, complete response < 5s

---

## Phase 5: Deploy

### Task 5.1 – Prepare for Production - Agent_Deploy
**Objective:** Make codebase production-ready.
**Output:** Production configs, proper error handling, security review.
**Guidance:** Ensure no secrets are committed.

1. Review .gitignore: ensure .env, __pycache__, venv/ are ignored
2. Update render.yaml with ANTHROPIC_API_KEY environment variable
3. Add structured error logging with timestamps
4. Create production config (debug=False, proper CORS)
5. Test locally with `gunicorn app:app` to simulate production
6. Security check: no hardcoded keys, no sensitive data in responses

### Task 5.2 – Push to GitHub - Agent_Deploy
**Objective:** Commit and push all changes to repository.
**Output:** Updated GitHub repository with complete new system.
**Guidance:** Use meaningful commit messages.

1. Run `git status` to review all changes
2. Stage changes: `git add -A`
3. Commit with message: "feat: Complete resume tailoring system with real-time streaming, dual AI, and comprehensive analysis"
4. Push: `git push origin main`
5. Verify on GitHub: https://github.com/Iskos1/Resume-Tailoring
6. Confirm no secrets visible in repo

### Task 5.3 – Deploy to Render - Agent_Deploy
**Objective:** Deploy to Render.com for public access.
**Output:** Live production URL.
**Guidance:** Render auto-deploys from GitHub main branch.

1. Log into Render dashboard
2. Verify GitHub repo is connected
3. Add environment variables:
   - GEMINI_API_KEY
   - ANTHROPIC_API_KEY
4. Trigger manual deploy or push to trigger auto-deploy
5. Monitor build logs for errors
6. Test live URL, document final production URL
7. Verify all features work in production
