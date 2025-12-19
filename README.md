# Resume Tailoring Application

An AI-powered resume builder that uses OpenAI to automatically tailor your resume to specific job descriptions.

## 🌐 Live Demo

**Coming Soon**: Deploy your own instance following the [Deployment Guide](DEPLOYMENT.md)

## Features

- 📝 **Resume Editor**: Comprehensive form to edit all sections of your resume
- 🤖 **AI-Powered Tailoring**: Uses OpenAI GPT-4 to optimize your resume for specific job postings
- 📄 **PDF Export**: Download your tailored resume as a PDF
- 💾 **Auto-Save**: Your resume data is automatically saved locally

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure OpenAI API Key

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your-actual-api-key-here
```

### 3. Start the Server

```bash
npm start
```

The application will start on `http://localhost:5001`

## 🚀 Deployment

This application is ready to deploy to multiple platforms. See the [**Deployment Guide**](DEPLOYMENT.md) for detailed instructions.

**Recommended Platforms**:
- ⭐ [Render.com](https://render.com) - Free tier, easy setup
- [Railway.app](https://railway.app) - $5 free credit, instant deploy  
- [Vercel](https://vercel.com) - Serverless, fast
- [Heroku](https://heroku.com) - Classic platform

All platforms support one-click deployment from this GitHub repository!

## Usage

### Main Resume Editor
1. Navigate to `http://localhost:5001`
2. Fill in your resume information in all sections
3. Click "Save Resume" to persist changes

### AI Resume Tailoring
1. Open the "🤖 AI Resume Tailor" section
2. Paste a job description
3. Click "✨ Tailor Resume with AI"
4. The AI will optimize your resume to match the job requirements
5. Review the changes and save

### Test OpenAI Connection
Visit `http://localhost:5001/test_openai.html` to verify your OpenAI API is configured correctly.

### Download PDF
Click "📥 Download PDF" to open a print-friendly view of your resume that you can save as PDF.

## Project Structure

```
Resume Tailoring/
├── server.js              # Express server with OpenAI integration
├── package.json           # Node.js dependencies
├── .env                   # API keys (gitignored)
├── .env.example           # Template for environment variables
├── data/
│   ├── master_resume.json # Your resume data
│   └── backups/           # Automatic backups
└── public/
    ├── index.html         # Main resume editor
    ├── resume_pdf.html    # PDF export view
    └── test_openai.html   # API test page
```

## Technologies Used

- **Backend**: Node.js, Express
- **AI**: OpenAI GPT-4o
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Custom dark theme inspired by GitHub

## API Endpoints

- `GET /` - Main resume editor
- `GET /api/resume` - Get resume data
- `POST /api/resume` - Save resume data
- `POST /api/tailor` - AI-tailor resume to job description
- `GET /api/test-openai` - Test OpenAI connection
- `GET /preview` - PDF export view

## Troubleshooting

### "Invalid API key" Error
- Check that your API key is correctly set in `.env` or `server.js`
- Verify your OpenAI account has credits
- Test the connection at `/test_openai.html`

### Resume Not Saving
- Check browser console for errors
- Ensure `data/` directory exists and is writable

### AI Tailoring Not Working
- Ensure you have pasted a job description
- Check that your OpenAI API key has sufficient credits
- Look at server logs for detailed error messages

## Security Notes

- ⚠️ Never commit your `.env` file or expose your API key
- The `.env` file is gitignored by default
- Store API keys securely and rotate them regularly

## License

This project is for personal use.

