/**
 * Resume Tailoring System - Frontend Application
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const masterResumeTextarea = document.getElementById('masterResume');
    const jobDescriptionTextarea = document.getElementById('jobDescription');
    const saveMasterBtn = document.getElementById('saveMasterBtn');
    const saveStatus = document.getElementById('saveStatus');
    const tailorBtn = document.getElementById('tailorBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    
    // Results elements
    const resultsPanel = document.getElementById('resultsPanel');
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContent = document.getElementById('resultsContent');
    const emptyState = document.getElementById('emptyState');
    
    // Result data elements
    const compatibilityScore = document.getElementById('compatibilityScore');
    const scoreCircle = document.getElementById('scoreCircle');
    const matchingList = document.getElementById('matchingList');
    const gapsList = document.getElementById('gapsList');
    const tailoredResume = document.getElementById('tailoredResume');
    
    // New enhanced elements
    const overallAssessment = document.getElementById('overallAssessment');
    const reframingList = document.getElementById('reframingList');
    const bridgeList = document.getElementById('bridgeList');
    const interviewList = document.getElementById('interviewList');
    
    // Store the current tailored resume for PDF download
    let currentTailoredResume = '';
    
    // Add SVG gradient definition for the score circle
    addScoreGradient();
    
    // Initialize: Load master resume
    loadMasterResume();
    
    // Guide toggle
    const toggleGuideBtn = document.getElementById('toggleGuide');
    const guideSection = document.getElementById('guideSection');
    
    // Event Listeners
    saveMasterBtn.addEventListener('click', saveMasterResume);
    tailorBtn.addEventListener('click', tailorResume);
    downloadPdfBtn.addEventListener('click', downloadPdf);
    
    // Toggle guide visibility
    if (toggleGuideBtn && guideSection) {
        toggleGuideBtn.addEventListener('click', () => {
            const isHidden = guideSection.classList.contains('hidden');
            guideSection.classList.toggle('hidden');
            toggleGuideBtn.innerHTML = isHidden 
                ? '<span class="btn-icon">✕</span> Hide Guide'
                : '<span class="btn-icon">📚</span> What to Include';
        });
    }
    
    /**
     * Add SVG gradient definition for score circle
     */
    function addScoreGradient() {
        const svg = document.querySelector('.score-ring');
        if (!svg) return;
        
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#06d6a0"/>
                <stop offset="100%" style="stop-color:#00b4d8"/>
            </linearGradient>
        `;
        svg.insertBefore(defs, svg.firstChild);
    }
    
    /**
     * Load master resume from server
     */
    async function loadMasterResume() {
        try {
            const response = await fetch('/api/master-resume');
            const data = await response.json();
            if (data.content) {
                masterResumeTextarea.value = data.content;
            }
        } catch (error) {
            console.error('Failed to load master resume:', error);
        }
    }
    
    /**
     * Save master resume to server
     */
    async function saveMasterResume() {
        const content = masterResumeTextarea.value;
        
        try {
            saveMasterBtn.disabled = true;
            saveMasterBtn.innerHTML = '<span class="btn-icon">⏳</span> Saving...';
            
            const response = await fetch('/api/master-resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });
            
            const data = await response.json();
            
            if (data.success) {
                saveStatus.textContent = '✓ Saved successfully!';
                saveStatus.classList.add('visible');
                setTimeout(() => {
                    saveStatus.classList.remove('visible');
                }, 3000);
            }
        } catch (error) {
            console.error('Failed to save master resume:', error);
            saveStatus.textContent = '✗ Failed to save';
            saveStatus.style.color = 'var(--error)';
            saveStatus.classList.add('visible');
        } finally {
            saveMasterBtn.disabled = false;
            saveMasterBtn.innerHTML = '<span class="btn-icon">💾</span> Save Master Resume';
        }
    }
    
    /**
     * Tailor resume based on job description
     */
    async function tailorResume() {
        const masterResume = masterResumeTextarea.value.trim();
        const jobDescription = jobDescriptionTextarea.value.trim();
        
        // Validation
        if (!masterResume) {
            showError('Please enter your master resume first.');
            return;
        }
        
        if (!jobDescription) {
            showError('Please enter a job description.');
            return;
        }
        
        // Show loading state
        showLoading();
        
        try {
            tailorBtn.disabled = true;
            tailorBtn.innerHTML = '<span class="btn-icon">⏳</span> Analyzing...';
            
            const response = await fetch('/api/tailor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    master_resume: masterResume,
                    job_description: jobDescription
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Display results
            displayResults(data);
            
        } catch (error) {
            console.error('Failed to tailor resume:', error);
            showError('Failed to connect to the server. Please try again.');
        } finally {
            tailorBtn.disabled = false;
            tailorBtn.innerHTML = '<span class="btn-icon">✨</span> Tailor My Resume';
        }
    }
    
    /**
     * Display tailoring results
     */
    function displayResults(data) {
        // Hide other states
        loadingState.classList.add('hidden');
        errorState.classList.add('hidden');
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');
        
        // Animate score
        const score = data.compatibility_score || 0;
        animateScore(score);
        
        // Display score breakdown
        displayScoreBreakdown(data.score_breakdown);
        
        // Display experience reframing - THE KEY INSIGHT
        displayReframing(data.experience_reframing);
        
        // Populate what you have (matching qualifications)
        matchingList.innerHTML = '';
        const matches = data.what_you_have || data.matching_qualifications || [];
        if (matches.length > 0) {
            matches.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                matchingList.appendChild(li);
            });
        } else {
            matchingList.innerHTML = '<li>No direct matches found</li>';
        }
        
        // Populate what's missing (gaps)
        gapsList.innerHTML = '';
        const gaps = data.what_you_lack || data.gaps || [];
        if (gaps.length > 0) {
            gaps.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                gapsList.appendChild(li);
            });
        } else {
            gapsList.innerHTML = '<li>No significant gaps identified</li>';
        }
        
        // Display bridge the gap section
        displayBridgeTheGap(data.bridge_the_gap);
        
        // Display interview prep
        displayInterviewPrep(data.interview_prep);
        
        // Display tailored resume
        currentTailoredResume = data.tailored_resume || '';
        tailoredResume.textContent = currentTailoredResume;
        
        // Scroll to results
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    /**
     * Display score breakdown bars
     */
    function displayScoreBreakdown(breakdown) {
        if (!breakdown) return;
        
        // Overall assessment
        if (overallAssessment && breakdown.overall_assessment) {
            overallAssessment.textContent = breakdown.overall_assessment;
        }
        
        // Animate breakdown bars
        setTimeout(() => {
            animateBreakdownBar('hardSkills', breakdown.hard_skills_match || 0);
            animateBreakdownBar('experience', breakdown.experience_relevance || 0);
            animateBreakdownBar('industry', breakdown.industry_alignment || 0);
            animateBreakdownBar('seniority', breakdown.seniority_fit || 0);
        }, 500);
    }
    
    /**
     * Animate a breakdown bar
     */
    function animateBreakdownBar(id, value) {
        const bar = document.getElementById(`${id}Bar`);
        const valueEl = document.getElementById(`${id}Value`);
        if (bar && valueEl) {
            bar.style.width = `${value}%`;
            bar.style.backgroundColor = getScoreColor(value);
            valueEl.textContent = `${value}%`;
        }
    }
    
    /**
     * Get color based on score value
     */
    function getScoreColor(value) {
        if (value >= 80) return '#06d6a0';
        if (value >= 60) return '#00b4d8';
        if (value >= 40) return '#ffd166';
        return '#ef476f';
    }
    
    /**
     * Display experience reframing section
     */
    function displayReframing(reframings) {
        const section = document.getElementById('reframingSection');
        if (!reframings || reframings.length === 0) {
            if (section) section.style.display = 'none';
            return;
        }
        if (section) section.style.display = 'block';
        
        reframingList.innerHTML = '';
        reframings.forEach(reframe => {
            const card = document.createElement('div');
            card.className = 'reframe-card';
            
            let transformsHtml = '';
            if (reframe.key_transforms && reframe.key_transforms.length > 0) {
                transformsHtml = `
                    <div class="transforms-list">
                        ${reframe.key_transforms.map(t => `
                            <div class="transform-item">
                                <span class="transform-arrow">→</span>
                                <span class="transform-text">${escapeHtml(t)}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            card.innerHTML = `
                <div class="reframe-header">
                    <span class="reframe-role">${escapeHtml(reframe.original_role || 'Role')}</span>
                </div>
                <div class="reframe-comparison">
                    <div class="reframe-from">
                        <span class="reframe-label">Originally</span>
                        <p>${escapeHtml(reframe.original_focus || '')}</p>
                    </div>
                    <div class="reframe-arrow">→</div>
                    <div class="reframe-to">
                        <span class="reframe-label">Now Highlighting</span>
                        <p>${escapeHtml(reframe.reframed_focus || '')}</p>
                    </div>
                </div>
                <div class="reframe-why">
                    <strong>Why this works:</strong> ${escapeHtml(reframe.why_this_works || '')}
                </div>
                ${transformsHtml}
            `;
            
            reframingList.appendChild(card);
        });
    }
    
    /**
     * Display bridge the gap section
     */
    function displayBridgeTheGap(bridges) {
        const section = document.getElementById('bridgeSection');
        if (!bridges || bridges.length === 0) {
            if (section) section.style.display = 'none';
            return;
        }
        if (section) section.style.display = 'block';
        
        bridgeList.innerHTML = '';
        bridges.forEach(bridge => {
            const card = document.createElement('div');
            card.className = 'bridge-card';
            
            let resourcesHtml = '';
            if (bridge.resources && bridge.resources.length > 0) {
                resourcesHtml = `
                    <div class="resources-list">
                        <h5>📚 Resources</h5>
                        ${bridge.resources.map(r => `
                            <div class="resource-item">
                                <span class="resource-name">${escapeHtml(r.name || '')}</span>
                                <span class="resource-meta">${escapeHtml(r.time || '')} • ${escapeHtml(r.cost || '')}</span>
                                ${r.url ? `<a href="${r.url.startsWith('http') ? r.url : '#'}" target="_blank" class="resource-link">${r.url.startsWith('Search:') ? r.url : 'Open →'}</a>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            card.innerHTML = `
                <div class="bridge-header">
                    <span class="bridge-gap">📍 ${escapeHtml(bridge.gap || 'Gap')}</span>
                </div>
                <div class="bridge-actions">
                    <div class="bridge-action quick">
                        <span class="action-label">⚡ Quick Win (This Week)</span>
                        <p>${escapeHtml(bridge.quick_win || '')}</p>
                    </div>
                    <div class="bridge-action medium">
                        <span class="action-label">📅 Medium Term (1-4 Weeks)</span>
                        <p>${escapeHtml(bridge.medium_term || '')}</p>
                    </div>
                    ${bridge.portfolio_project ? `
                        <div class="bridge-action project">
                            <span class="action-label">🚀 Portfolio Project Idea</span>
                            <p>${escapeHtml(bridge.portfolio_project)}</p>
                        </div>
                    ` : ''}
                </div>
                ${resourcesHtml}
            `;
            
            bridgeList.appendChild(card);
        });
    }
    
    /**
     * Display interview prep section
     */
    function displayInterviewPrep(preps) {
        const section = document.getElementById('interviewSection');
        if (!preps || preps.length === 0) {
            if (section) section.style.display = 'none';
            return;
        }
        if (section) section.style.display = 'block';
        
        interviewList.innerHTML = '';
        preps.forEach(prep => {
            const li = document.createElement('li');
            li.className = 'interview-item';
            li.textContent = prep;
            interviewList.appendChild(li);
        });
    }
    
    /**
     * Animate the compatibility score
     */
    function animateScore(targetScore) {
        const circumference = 2 * Math.PI * 54; // 2πr where r=54
        const offset = circumference - (targetScore / 100) * circumference;
        
        // Reset
        scoreCircle.style.strokeDashoffset = circumference;
        compatibilityScore.textContent = '0';
        
        // Animate after a short delay
        setTimeout(() => {
            scoreCircle.style.strokeDashoffset = offset;
            
            // Animate number
            let current = 0;
            const increment = targetScore / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= targetScore) {
                    current = targetScore;
                    clearInterval(timer);
                }
                compatibilityScore.textContent = Math.round(current);
            }, 30);
        }, 100);
    }
    
    /**
     * Download tailored resume as PDF
     */
    async function downloadPdf() {
        if (!currentTailoredResume) {
            showError('No tailored resume to download. Please tailor your resume first.');
            return;
        }
        
        try {
            downloadPdfBtn.disabled = true;
            downloadPdfBtn.innerHTML = '<span class="btn-icon">⏳</span> Generating...';
            
            const response = await fetch('/api/download-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume_content: currentTailoredResume
                })
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to generate PDF');
            }
            
            // Download the PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tailored_resume.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
        } catch (error) {
            console.error('Failed to download PDF:', error);
            showError(error.message || 'Failed to generate PDF. Please try again.');
        } finally {
            downloadPdfBtn.disabled = false;
            downloadPdfBtn.innerHTML = '<span class="btn-icon">⬇</span> Download PDF';
        }
    }
    
    /**
     * Show loading state
     */
    function showLoading() {
        emptyState.classList.add('hidden');
        errorState.classList.add('hidden');
        resultsContent.classList.add('hidden');
        loadingState.classList.remove('hidden');
    }
    
    /**
     * Show error state
     */
    function showError(message) {
        loadingState.classList.add('hidden');
        emptyState.classList.add('hidden');
        resultsContent.classList.add('hidden');
        errorMessage.textContent = message;
        errorState.classList.remove('hidden');
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});

