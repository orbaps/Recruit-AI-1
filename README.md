# 🎯 Recruit AI 

A comprehensive AI-powered CV analysis tool that evaluates resumes against job descriptions using multiple AI providers (Gemini, OpenAI GPT, Claude, xAI Grok, Mistral, and more). Features both placement team dashboard and student interface with detailed feedback, section-wise scoring, and actionable improvement suggestions.

![Project Overview](docs/pic1.png)
 
# 🌟 Features

## Core Features
- **Multi-AI Provider Support**: Choose between Google Gemini, OpenAI GPT, Claude, xAI Grok, Mistral, Perplexity, Together AI, and Cohere 
- **File Format Support**: Upload PDF, DOCX, or TXT files
- **Section-wise Analysis**: Detailed breakdown of CV sections with individual scores
- **Comprehensive Scoring**: Overall CV match score against job requirements
- **Actionable Feedback**: Specific improvement suggestions for each section
- **Secure API Key Handling**: Users provide their own API keys (not stored)
- **Modern UI**: Clean, intuitive Streamlit interface with multiple themes
- **Real-time Analysis**: Instant AI-powered CV evaluation

## 🎓 Student Interface Features
- **Welcome/Onboarding Screen**: Professional introduction for new users
- **Login/Registration**: Email and social login options (Google, LinkedIn)
- **Resume Upload & Analysis**: Multi-AI provider support with instant feedback
- **Version Comparison**: Compare resume improvements over time
- **Progress Tracking**: Visualize your resume improvement journey
- **Tips & Guides**: Expert advice for resume writing
- **Performance Dashboard**: Charts and metrics tracking

## 🏢 Placement Team Dashboard
- **Job Description Management**: Create, edit, and manage job postings
- **Batch Resume Processing**: Upload and analyze multiple resumes
- **Candidate Shortlisting**: Rank and filter candidates by scores
- **Detailed Reports**: Comprehensive candidate evaluation reports
- **Side-by-Side Comparison**: Compare multiple candidates
- **Email Integration**: Send feedback directly to candidates

# 🚀 Quick Start

## Prerequisites

- Python 3.7 or higher
- API key from at least one of the supported providers

## Installation
### Clone or create the project:
```bash
git clone https://github.com/orbaps/Recruit-AI-.git
cd Recruit-AI-
```
### Install required packages:
```bash
pip install -r requirements.txt
```
### Run the application:

#### For Placement Team Dashboard:
```bash
streamlit run placement_dashboard.py
```

#### For Student Interface:
```bash
streamlit run student_interface.py --server.port 8505
```

#### For Basic CV Analysis:
```bash
streamlit run cv_ranking_app.py
```

## 🔑 Getting API Keys

### Google Gemini
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Click "Create API Key"
- Copy your API key

### OpenAI
- Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- Sign in to your OpenAI account
- Click "Create new secret key"
- Copy your API key

### Anthropic (Claude)
- Visit [Anthropic Console](https://console.anthropic.com/)
- Sign in to your Anthropic account
- Navigate to API Keys section
- Generate a new API key

### xAI (Grok)
- Visit [xAI Console](https://console.x.ai/)
- Sign in with your account
- Navigate to API Keys section
- Generate a new API key

### Other Providers
- **Cohere**: [Cohere Dashboard](https://dashboard.cohere.ai/api-keys)
- **Mistral AI**: [Mistral Console](https://console.mistral.ai/)
- **Perplexity**: [Perplexity Settings](https://www.perplexity.ai/settings/api)
- **Together AI**: [Together Platform](https://api.together.xyz/settings/api-keys)

## 📚 Usage Guide

### For Students:
1. **Access Student Interface**: Run `streamlit run student_interface.py`
2. **Create Account**: Register with email or use social login
3. **Upload Resume**: Drag and drop or browse for your resume file
4. **Get Feedback**: Receive instant AI-powered analysis
5. **Track Progress**: Compare versions and see improvements over time
6. **Access Tips**: Get expert advice on resume writing

### For Placement Teams:
1. **Access Dashboard**: Run `streamlit run placement_dashboard.py`
2. **Manage Jobs**: Create and edit job descriptions
3. **Batch Process**: Upload multiple candidate resumes
4. **Review Candidates**: Sort and filter by scores
5. **Generate Reports**: Create detailed candidate evaluations
6. **Send Feedback**: Email results directly to candidates

### Basic CV Analysis:
#### Step 1: Configure AI Settings
- Select your preferred AI provider (Gemini, OpenAI, Claude, etc.)
- Choose the specific model you want to use
- Enter your API key securely

#### Step 2: Upload Your CV
- Option A: Upload a file (PDF, DOCX, or TXT)
- Option B: Copy and paste your CV content directly

#### Step 3: Add Job Description
Paste the complete job description including:

- Job requirements
- Required skills
- Responsibilities
- Qualifications

![Project Overview](docs/pic2.png) 

#### Step 4: Analyze
Click "🚀 Analyze CV" to get comprehensive feedback

![Project Overview](docs/pic3.png) 

## 📊 Analysis Output
The system provides:

- Overall Score: Match percentage (0-100)
- Section-wise Analysis: Individual scores for each CV section
- Strengths: What works well in your CV
- Weaknesses: Areas needing improvement
- Missing Skills: Skills mentioned in job description but not in CV
- Recommendations: Specific, actionable improvement suggestions

![Project Overview](docs/pic4.png) 

# 🛠️ Technical Details
## Dependencies
```bash
streamlit>=1.28.0
google-generativeai>=0.3.0
openai>=1.0.0
requests>=2.31.0
PyPDF2>=3.0.1
python-docx>=0.8.11
```

## File Processing
- **PDF**: Extracted using PyPDF2
- **DOCX**: Processed with python-docx
- **TXT**: Direct text reading

## Security Features
- API keys are input as password fields (hidden)
- Keys are not stored or logged
- Session-based processing only

# 🔮 Future Enhancements
## Planned features:

- ✅ **Student Interface** - Complete student portal with progress tracking
- ✅ **Placement Dashboard** - Professional recruitment management system
- ✅ **Version Comparison** - Compare resume improvements over time
- ✅ **Batch Processing** - Upload and analyze multiple resumes
- ✅ **Multi-AI Support** - 8+ AI providers integrated
- 🔄 Export analysis reports (PDF/Excel)
- 🔄 Integration with ATS systems
- 🔄 Advanced scoring algorithms
- 🔄 Industry-specific analysis templates
- 🔄 Real-time collaboration features

# 🚀 Deployment

## Live Demo
To test the application, visit our deployed versions:

- **Main Application**: [Recruit AI on Streamlit](https://recruit-ai.streamlit.app/)
- **Student Interface**: Available on port 8505 when running locally
- **Placement Dashboard**: Available on port 8502 when running locally

## Local Deployment
```bash
# Clone the repository
git clone https://github.com/orbaps/Recruit-AI-.git
cd Recruit-AI-

# Install dependencies
pip install -r requirements.txt

# Run different interfaces
streamlit run cv_ranking_app.py                    # Main app
streamlit run student_interface.py --server.port 8505   # Student portal
streamlit run placement_dashboard.py --server.port 8502 # Admin dashboard
```

# 📞 Contact

## Project Maintainer
- **Name**: Amarendra Pratap Singh
- **GitHub**: [orbaps](https://github.com/orbaps/Recruit-AI-)
- **LinkedIn**: [Amarendra Pratap Singh](https://www.linkedin.com/in/orbaps)
- **Email**: amarendrapratapsingh.2004@gmail.com

## Original Creator
- **Name**: Bellmir Yahya
- **GitHub**: [Yasouimo](https://github.com/Yasouimo)
- **LinkedIn**: [Yahya Bellmir](https://www.linkedin.com/in/yahya-bellmir-a54176284/)
- **Email**: yahyabellmir@gmail.com

---

## 📝 License
This project is open source and available under the [MIT License](LICENSE).

## 🎆 Acknowledgments
- Thanks to all AI providers for their powerful APIs
- Streamlit community for the amazing framework
- Contributors and users for valuable feedback

## 🐛 Issues & Contributions
Found a bug or want to contribute? 
- 📝 [Report Issues](https://github.com/orbaps/Recruit-AI-/issues)
- 🔧 [Submit Pull Requests](https://github.com/orbaps/Recruit-AI-/pulls)
- ⭐ Don't forget to star the repository if you find it helpful!

---

**🚀 Built with ❤️ by [Amarendra Pratap Singh](https://github.com/orbaps) | Enhanced from original work by [Bellmir Yahya](https://github.com/Yasouimo)**
