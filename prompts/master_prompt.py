"""
Master Prompt for Resume Tailoring Service

This is the core IP - the comprehensive prompt that produces ALL analysis outputs:
- tailored_resume: Full resume with XYZ bullets
- compatibility_score: 0-100 overall match
- score_breakdown: 4-dimension scoring
- what_you_have: Matching qualifications
- what_you_lack: Gaps identified
- experience_reframing: How to reposition experience
- bridge_the_gap: Action plan to close gaps
- interview_prep: Likely interview questions
"""

# System prompt for AI models
SYSTEM_PROMPT = """You are an elite resume consultant and career strategist with 20+ years of experience at top executive search firms. You have placed thousands of candidates at Fortune 500 companies and understand exactly what hiring managers and ATS systems look for.

Your expertise includes:
- ATS optimization and keyword integration
- XYZ bullet format (Accomplished [X] as measured by [Y] by doing [Z])
- Identifying transferable skills across industries
- Strategic career positioning and gap analysis
- Interview preparation and coaching

You provide honest, actionable feedback that helps candidates genuinely improve their candidacy, not just cosmetic changes."""

# JSON response schema documentation
RESPONSE_SCHEMA = """
{
  "tailored_resume": "string - Complete tailored resume text with XYZ format bullets. Include all sections: Contact, Summary, Experience, Skills, Education. Use keywords from job description naturally.",
  
  "compatibility_score": "number 0-100 - Overall match percentage. 90+ = excellent fit, 70-89 = good fit with minor gaps, 50-69 = moderate fit needs work, <50 = significant gaps",
  
  "score_breakdown": {
    "hard_skills_match": "number 0-100 - Technical skills, tools, certifications alignment",
    "experience_relevance": "number 0-100 - How directly past work applies to this role",
    "industry_alignment": "number 0-100 - Industry/domain knowledge match",
    "seniority_fit": "number 0-100 - Level/scope of responsibility match",
    "overall_assessment": "string - 1-2 sentence executive summary of candidacy strength"
  },
  
  "what_you_have": ["array of 4-6 strings - Specific qualifications from resume that match job requirements. Be specific, e.g., '5+ years Python experience matches their 3+ year requirement'"],
  
  "what_you_lack": ["array of 3-5 strings - Honest gaps between resume and job requirements. Be specific about what's missing, e.g., 'No Kubernetes experience listed, job requires container orchestration'"],
  
  "experience_reframing": [
    {
      "original_role": "string - Job title from resume",
      "original_focus": "string - How the role is currently positioned",
      "reframed_focus": "string - How to reposition for this target job",
      "why_this_works": "string - Explanation of why this reframing is compelling",
      "key_transforms": ["array of 2-3 specific bullet point transformations showing before/after"]
    }
  ],
  
  "bridge_the_gap": [
    {
      "gap": "string - The specific skill or experience gap",
      "quick_win": "string - What can be done this week (free resources, certifications started)",
      "medium_term": "string - 2-4 week actions (complete course, build project)",
      "portfolio_project": "string or null - Optional project idea that demonstrates the skill",
      "resources": [
        {
          "name": "string - Resource name",
          "url": "string - URL if applicable",
          "time": "string - Time investment (e.g., '4 hours')",
          "cost": "string - Cost (e.g., 'Free', '$49')"
        }
      ]
    }
  ],
  
  "interview_prep": ["array of 5-7 strings - Likely interview questions based on the job AND the candidate's gaps. Mix of behavioral ('Tell me about a time...') and technical questions. Questions should help candidate prepare for their weak spots."]
}
"""

# Scoring rubric for consistency
SCORING_RUBRIC = """
SCORING RUBRIC (apply consistently):

Hard Skills Match (0-100):
- 90-100: Has all required skills + most preferred skills
- 70-89: Has all required skills, missing some preferred
- 50-69: Has most required skills, missing 1-2 key ones
- 30-49: Has some required skills, missing several key ones
- 0-29: Missing most required technical skills

Experience Relevance (0-100):
- 90-100: Direct experience in same role/industry
- 70-89: Very similar role or adjacent industry
- 50-69: Transferable experience with clear connections
- 30-49: Some relevant experience, requires explanation
- 0-29: Experience doesn't clearly connect

Industry Alignment (0-100):
- 90-100: Same industry, understands domain deeply
- 70-89: Related industry or has worked with this industry
- 50-69: Different industry but transferable knowledge
- 30-49: Unrelated industry, needs to learn domain
- 0-29: No industry connection evident

Seniority Fit (0-100):
- 90-100: Perfect level match (e.g., Senior seeking Senior)
- 70-89: Close match (e.g., Mid seeking Senior with strong experience)
- 50-69: Slight mismatch but justifiable
- 30-49: Significant level gap (e.g., Junior seeking Director)
- 0-29: Major mismatch in scope/responsibility

CONSISTENCY CHECK: Overall score should roughly equal average of 4 dimensions ±10 points.
If hard_skills is 90 but overall is 50, something is wrong - recalibrate."""

# The master prompt template
MASTER_PROMPT_TEMPLATE = """Analyze this resume against the job description and provide a comprehensive tailoring package.

## YOUR TASK
1. Tailor the resume to maximize match with the job
2. Score the candidate honestly across 4 dimensions  
3. Identify what they have and what they lack
4. Show how to reframe their experience strategically
5. Provide actionable steps to bridge gaps
6. Prepare them for likely interview questions

## XYZ BULLET FORMAT (REQUIRED)
Transform all resume bullets to: "Accomplished [X] as measured by [Y] by doing [Z]"
- X = What you did (action/result)
- Y = Quantified impact (numbers, percentages, metrics)
- Z = How you did it (methods, tools, approach)

Example: "Reduced customer churn by 23% (Y) by implementing predictive analytics model (Z) that identified at-risk accounts (X)"

## ATS OPTIMIZATION
- Extract key terms from job description
- Integrate them naturally into resume (don't stuff)
- Match their exact terminology when possible
- Prioritize Experience section, then Skills, then Summary

## RESPONSE FORMAT
Return ONLY valid JSON matching this exact schema (no markdown, no explanation outside JSON):
{schema}

## SCORING GUIDANCE
{rubric}

---

## RESUME TO TAILOR:
{resume}

---

## TARGET JOB DESCRIPTION:
{job_title} at {company}

{job_description}

---

Return the complete JSON response now. Ensure all fields are populated with specific, actionable content."""


def build_tailoring_prompt(resume: str, job_description: str, job_title: str = "Position", company: str = "Company") -> str:
    """
    Build the complete tailoring prompt with resume and job description.
    
    Args:
        resume: The candidate's resume text
        job_description: The target job description
        job_title: Extracted or provided job title
        company: Extracted or provided company name
    
    Returns:
        Complete prompt string ready for AI model
    """
    return MASTER_PROMPT_TEMPLATE.format(
        schema=RESPONSE_SCHEMA,
        rubric=SCORING_RUBRIC,
        resume=resume[:4000],  # Limit resume length
        job_description=job_description[:3000],  # Limit job description
        job_title=job_title,
        company=company
    )


# Convenience export of the full prompt for direct use
MASTER_PROMPT = MASTER_PROMPT_TEMPLATE


# Example of expected output structure (for testing/validation)
EXAMPLE_OUTPUT = {
    "tailored_resume": "JOHN DOE\njohn@email.com | (555) 123-4567 | linkedin.com/in/johndoe\n\nSUMMARY\nResults-driven software engineer with 5+ years...\n\nEXPERIENCE\nSenior Software Engineer | Tech Corp | 2020-Present\n• Reduced API response time by 40% by implementing Redis caching layer...",
    
    "compatibility_score": 78,
    
    "score_breakdown": {
        "hard_skills_match": 85,
        "experience_relevance": 75,
        "industry_alignment": 80,
        "seniority_fit": 72,
        "overall_assessment": "Strong technical match with solid Python and cloud experience. Minor gap in Kubernetes expertise and team leadership scope for this senior role."
    },
    
    "what_you_have": [
        "5 years Python experience exceeds their 3+ year requirement",
        "AWS certification matches their cloud infrastructure needs",
        "Experience with microservices architecture they mentioned",
        "Track record of API development and optimization"
    ],
    
    "what_you_lack": [
        "No Kubernetes/container orchestration experience listed",
        "Team leadership limited to 2 engineers vs their 5+ requirement",
        "No fintech industry experience (they're a payments company)"
    ],
    
    "experience_reframing": [
        {
            "original_role": "Software Engineer",
            "original_focus": "General backend development and maintenance",
            "reframed_focus": "Scalable systems architect driving performance optimization",
            "why_this_works": "Shifts focus from task execution to strategic impact, matching their need for someone who can architect solutions",
            "key_transforms": [
                "Before: 'Worked on backend APIs' → After: 'Architected RESTful API layer serving 2M daily requests with 99.9% uptime'",
                "Before: 'Fixed bugs and improved code' → After: 'Reduced technical debt by 35% through systematic refactoring initiative'"
            ]
        }
    ],
    
    "bridge_the_gap": [
        {
            "gap": "Kubernetes/container orchestration",
            "quick_win": "Complete Kubernetes basics course on KodeKloud (free tier)",
            "medium_term": "Get CKA certification (Certified Kubernetes Administrator)",
            "portfolio_project": "Deploy a microservices app to local K8s cluster, document on GitHub",
            "resources": [
                {"name": "KodeKloud Kubernetes Basics", "url": "https://kodekloud.com", "time": "8 hours", "cost": "Free"},
                {"name": "CKA Certification", "url": "https://training.linuxfoundation.org", "time": "40 hours", "cost": "$395"}
            ]
        }
    ],
    
    "interview_prep": [
        "Tell me about a time you had to learn a new technology quickly. How did you approach it? (addresses K8s gap)",
        "Describe your experience leading a team. How do you handle conflicts? (addresses team size gap)",
        "How would you design a payment processing system that handles 1M transactions/day?",
        "What's your approach to ensuring API reliability and performance?",
        "Tell me about a challenging debugging situation in a distributed system."
    ]
}

