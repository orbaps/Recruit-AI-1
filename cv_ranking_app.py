import logging
import os
from typing import Dict, List, Optional, Union
from pathlib import Path
import streamlit as st
import google.generativeai as genai
import openai
import requests
import PyPDF2
import docx
import io
import json
import anthropic
import cohere

# Import configuration and utilities
from config import Config, setup_logging, validate_file_upload, validate_job_description, validate_api_key

# Initialize logging
logger = setup_logging()

# Theme Configuration
def get_theme_config():
    """Get theme configuration based on user preference"""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'
    
    themes = {
        'light': {
            'primary_bg': '#FFFFFF',
            'secondary_bg': '#F7F8FC', 
            'primary_text': '#1A202C',
            'secondary_text': '#4A5568',
            'accent': '#3182CE',
            'accent_hover': '#EBF8FF',
            'success': '#48BB78',
            'warning': '#F6AD55',
            'error': '#E53E3E',
            'card_shadow': 'rgba(0, 0, 0, 0.1)',
            'border': '#E2E8F0'
        },
        'dark': {
            'primary_bg': '#171923',
            'secondary_bg': '#2D3748',
            'primary_text': '#E2E8F0',
            'secondary_text': '#A0AEC0',
            'accent': '#63B3ED',
            'accent_hover': '#2A4365',
            'success': '#68D391',
            'warning': '#FBD38D',
            'error': '#FC8181',
            'card_shadow': 'rgba(0, 0, 0, 0.3)',
            'border': '#4A5568'
        }
    }
    return themes[st.session_state.theme_mode]

def apply_custom_css():
    """Apply custom CSS for theming"""
    theme = get_theme_config()
    
    css = f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .stApp {{
        background-color: {theme['primary_bg']} !important;
        color: {theme['primary_text']} !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Sidebar Styling */
    .css-1d391kg {{
        background-color: {theme['secondary_bg']} !important;
    }}
    
    /* Main Content */
    .main .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        background-color: {theme['primary_bg']} !important;
    }}
    
    /* Headers and Titles */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme['primary_text']} !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }}
    
    /* Card Styling */
    .metric-card {{
        background: {theme['secondary_bg']} !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px {theme['card_shadow']} !important;
        border: 1px solid {theme['border']} !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px {theme['card_shadow']} !important;
    }}
    
    /* Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['accent']}, {theme['accent']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }}
    
    .stButton > button:hover {{
        background: {theme['accent_hover']} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }}
    
    /* File Uploader */
    .stFileUploader {{
        background-color: {theme['secondary_bg']} !important;
        border: 2px dashed {theme['accent']} !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }}
    
    .stFileUploader:hover {{
        border-color: {theme['accent']} !important;
        background-color: {theme['accent_hover']} !important;
    }}
    
    /* Text Areas and Inputs */
    .stTextArea textarea, .stTextInput input {{
        background-color: {theme['secondary_bg']} !important;
        color: {theme['primary_text']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background-color: {theme['secondary_bg']} !important;
        color: {theme['primary_text']} !important;
        border: 1px solid {theme['border']} !important;
    }}
    
    /* Metrics */
    .metric-container {{
        background: {theme['secondary_bg']} !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border: 1px solid {theme['border']} !important;
        text-align: center !important;
        box-shadow: 0 2px 4px {theme['card_shadow']} !important;
    }}
    
    .metric-value {{
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: {theme['accent']} !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .metric-label {{
        font-size: 0.9rem !important;
        color: {theme['secondary_text']} !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    
    /* Progress Bars */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {theme['accent']}, {theme['success']}) !important;
        border-radius: 8px !important;
    }}
    
    /* Score Styling */
    .score-high {{
        color: {theme['success']} !important;
        font-weight: 600 !important;
    }}
    
    .score-medium {{
        color: {theme['warning']} !important;
        font-weight: 600 !important;
    }}
    
    .score-low {{
        color: {theme['error']} !important;
        font-weight: 600 !important;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {theme['secondary_bg']} !important;
        color: {theme['primary_text']} !important;
        border-radius: 8px !important;
        border: 1px solid {theme['border']} !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: {theme['secondary_bg']} !important;
        border: 1px solid {theme['border']} !important;
    }}
    
    /* Success/Warning/Error Messages */
    .stSuccess {{
        background-color: {theme['success']}20 !important;
        color: {theme['success']} !important;
        border-left: 4px solid {theme['success']} !important;
    }}
    
    .stWarning {{
        background-color: {theme['warning']}20 !important;
        color: {theme['warning']} !important;
        border-left: 4px solid {theme['warning']} !important;
    }}
    
    .stError {{
        background-color: {theme['error']}20 !important;
        color: {theme['error']} !important;
        border-left: 4px solid {theme['error']} !important;
    }}
    
    /* Info Messages */
    .stInfo {{
        background-color: {theme['accent']}20 !important;
        color: {theme['accent']} !important;
        border-left: 4px solid {theme['accent']} !important;
    }}
    
    /* Theme Toggle Button */
    .theme-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
        background: {theme['accent']} !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px {theme['card_shadow']} !important;
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px {theme['card_shadow']} !important;
    }}
    
    /* Animation Classes */
    .fade-in {{
        animation: fadeIn 0.5s ease-in !important;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .slide-in {{
        animation: slideIn 0.3s ease-out !important;
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(-100%); }}
        to {{ transform: translateX(0); }}
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        
        .metric-card {{
            margin-bottom: 0.5rem !important;
        }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# Configure the page
st.set_page_config(
    page_title="Recruit AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file with improved error handling"""
    try:
        logger.info(f"Extracting text from PDF: {pdf_file.name}")
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                text += page.extract_text()
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                continue
        
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"PDF extraction error: {str(e)}")

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file with improved error handling"""
    try:
        logger.info(f"Extracting text from DOCX: {docx_file.name}")
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        if not text.strip():
            raise Exception("No text could be extracted from the DOCX")
        
        logger.info(f"Successfully extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise Exception(f"DOCX extraction error: {str(e)}")

def call_gemini_api(api_key, model_name, cv_text, job_description):
    """Call Gemini API"""
    try:
        import google.generativeai as genai
        # Configure API
        genai.configure(api_key=api_key)  # type: ignore
        model = genai.GenerativeModel(model_name)  # type: ignore
        
        prompt = create_analysis_prompt(cv_text, job_description)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")

def call_openai_api(api_key, model_name, cv_text, job_description):
    """Call OpenAI API"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt = create_analysis_prompt(cv_text, job_description)
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert HR professional and recruiter."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API Error: {str(e)}")

def call_anthropic_api(api_key, model_name, cv_text, job_description):
    """Call Anthropic Claude API"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = create_analysis_prompt(cv_text, job_description)
        
        response = client.messages.create(
            model=model_name,
            max_tokens=3000,
            temperature=0.7,
            system="You are an expert HR professional and recruiter.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # Handle different response types safely
        try:
            return response.content[0].text  # type: ignore
        except AttributeError:
            return str(response.content[0])
    except Exception as e:
        raise Exception(f"Anthropic API Error: {str(e)}")

def call_cohere_api(api_key, model_name, cv_text, job_description):
    """Call Cohere API"""
    try:
        co = cohere.Client(api_key)
        
        prompt = f"You are an expert HR professional and recruiter.\n\n{create_analysis_prompt(cv_text, job_description)}"
        
        response = co.generate(
            model=model_name,
            prompt=prompt,
            max_tokens=3000,
            temperature=0.7
        )
        return response.generations[0].text
    except Exception as e:
        raise Exception(f"Cohere API Error: {str(e)}")

def call_xai_api(api_key, model_name, cv_text, job_description):
    """Call xAI (Grok) API"""
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = create_analysis_prompt(cv_text, job_description)
        
        data = {
            "messages": [
                {"role": "system", "content": "You are an expert HR professional and recruiter."},
                {"role": "user", "content": prompt}
            ],
            "model": model_name,
            "stream": False,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"xAI API Error: {str(e)}")

def call_mistral_api(api_key, model_name, cv_text, job_description):
    """Call Mistral AI API"""
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = create_analysis_prompt(cv_text, job_description)
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are an expert HR professional and recruiter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Mistral API Error: {str(e)}")

def call_perplexity_api(api_key, model_name, cv_text, job_description):
    """Call Perplexity API"""
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = create_analysis_prompt(cv_text, job_description)
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are an expert HR professional and recruiter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Perplexity API Error: {str(e)}")

def call_together_api(api_key, model_name, cv_text, job_description):
    """Call Together AI API"""
    try:
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = create_analysis_prompt(cv_text, job_description)
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are an expert HR professional and recruiter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Together AI API Error: {str(e)}")

def create_analysis_prompt(cv_text, job_description):
    """Create the analysis prompt for any AI model"""
    return f"""
    As an expert HR professional and recruiter, analyze the following CV against the job description.
    
    JOB DESCRIPTION:
    {job_description}
    
    CV CONTENT:
    {cv_text}
    
    Please provide a comprehensive analysis in the following JSON format:
    {{
        "overall_score": <score out of 100>,
        "sections": [
            {{
                "section_name": "<section name>",
                "content": "<section content summary>",
                "score": <score out of 10>,
                "feedback": "<detailed feedback>",
                "improvements": ["<improvement 1>", "<improvement 2>"]
            }}
        ],
        "strengths": ["<strength 1>", "<strength 2>"],
        "weaknesses": ["<weakness 1>", "<weakness 2>"],
        "missing_skills": ["<missing skill 1>", "<missing skill 2>"],
        "overall_recommendation": "<detailed recommendation>"
    }}
    
    Break down the CV into these sections: Personal Information, Summary/Objective, Experience, Education, Skills, and Additional Sections.
    Provide specific, actionable feedback for each section.
    Make sure to return valid JSON format.
    """

def analyze_cv_with_ai(provider, api_key, model_name, cv_text, job_description):
    """Analyze CV using selected AI provider"""
    if provider == "Gemini":
        return call_gemini_api(api_key, model_name, cv_text, job_description)
    elif provider == "OpenAI":
        return call_openai_api(api_key, model_name, cv_text, job_description)
    elif provider == "Anthropic (Claude)":
        return call_anthropic_api(api_key, model_name, cv_text, job_description)
    elif provider == "Cohere":
        return call_cohere_api(api_key, model_name, cv_text, job_description)
    elif provider == "xAI (Grok)":
        return call_xai_api(api_key, model_name, cv_text, job_description)
    elif provider == "Mistral AI":
        return call_mistral_api(api_key, model_name, cv_text, job_description)
    elif provider == "Perplexity":
        return call_perplexity_api(api_key, model_name, cv_text, job_description)
    elif provider == "Together AI":
        return call_together_api(api_key, model_name, cv_text, job_description)
    else:
        raise Exception("Unsupported AI provider")

def parse_analysis_response(response_text):
    """Parse the AI response and extract JSON"""
    try:
        # Try to find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
    except:
        pass
    return None

def display_score_meter(score, title):
    """Display an enhanced score meter with theming"""
    theme = get_theme_config()
    
    # Determine score category and color
    if score >= 75:
        score_class = "score-high"
        color = theme['success']
    elif score >= 50:
        score_class = "score-medium" 
        color = theme['warning']
    else:
        score_class = "score-low"
        color = theme['error']
    
    # Create custom metric display
    st.markdown(f"""
    <div class="metric-container fade-in">
        <div class="metric-value {score_class}">{score}</div>
        <div class="metric-label">{title}</div>
        <div style="width: 100%; background-color: {theme['border']}; border-radius: 10px; height: 8px; margin-top: 1rem;">
            <div style="width: {score}%; background: linear-gradient(90deg, {color}, {theme['accent']}); height: 100%; border-radius: 10px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_model_options(provider):
    """Get available models for each provider"""
    models = {
        "Gemini": [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro"
        ],
        "OpenAI": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ],
        "Anthropic (Claude)": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "Cohere": [
            "command-r-plus",
            "command-r",
            "command",
            "command-nightly",
            "command-light"
        ],
        "xAI (Grok)": [
            "grok-beta",
            "grok-vision-beta"
        ],
        "Mistral AI": [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "open-mistral-7b",
            "open-mixtral-8x7b",
            "open-mixtral-8x22b"
        ],
        "Perplexity": [
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-chat",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-8b-instruct",
            "llama-3.1-70b-instruct"
        ],
        "Together AI": [
            "meta-llama/Llama-2-70b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "meta-llama/Llama-2-7b-chat-hf",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "togethercomputer/RedPajama-INCITE-Chat-3B-v1"
        ]
    }
    return models.get(provider, [])

def get_api_info(provider):
    """Get API information for each provider"""
    info = {
        "Gemini": {
            "url": "https://makersuite.google.com/app/apikey",
            "description": "Get your Gemini API key from Google AI Studio"
        },
        "OpenAI": {
            "url": "https://platform.openai.com/api-keys", 
            "description": "Get your OpenAI API key from OpenAI Platform"
        },
        "Anthropic (Claude)": {
            "url": "https://console.anthropic.com/",
            "description": "Get your Claude API key from Anthropic Console"
        },
        "Cohere": {
            "url": "https://dashboard.cohere.ai/api-keys",
            "description": "Get your Cohere API key from Cohere Dashboard"
        },
        "xAI (Grok)": {
            "url": "https://console.x.ai/",
            "description": "Get your xAI API key from xAI Console"
        },
        "Mistral AI": {
            "url": "https://console.mistral.ai/",
            "description": "Get your Mistral API key from Mistral Console"
        },
        "Perplexity": {
            "url": "https://www.perplexity.ai/settings/api",
            "description": "Get your Perplexity API key from Perplexity Settings"
        },
        "Together AI": {
            "url": "https://api.together.xyz/settings/api-keys",
            "description": "Get your Together AI API key from Together Platform"
        }
    }
    return info.get(provider, {"url": "", "description": ""})

def main():
    # Apply theming
    apply_custom_css()
    
    # Initialize configuration validation
    config = Config()
    validation_results = config.validate_config()
    
    # Log application startup
    logger.info("CV Ranking Application started")
    
    # Check for configuration issues
    if not all(validation_results.values()):
        st.sidebar.warning("⚠️ Configuration Issues Detected")
        with st.sidebar.expander("Configuration Status", expanded=False):
            for check, result in validation_results.items():
                status = "✅" if result else "❌"
                st.write(f"{status} {check.replace('_', ' ').title()}")
    
    # Theme toggle in header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🌓" if st.session_state.theme_mode == 'light' else "☀️", 
                    help="Toggle theme", key="theme_toggle"):
            st.session_state.theme_mode = 'dark' if st.session_state.theme_mode == 'light' else 'light'
            st.rerun()
    
    # Header with enhanced styling
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("🎯 Recruit AI")
    st.markdown("**AI-Powered Resume Analysis & Recruitment Intelligence**")
    st.markdown("Upload your CV and job description to get comprehensive AI-powered analysis and improvement suggestions")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar for AI configuration and inputs
    with st.sidebar:
        st.markdown('<div class="slide-in">', unsafe_allow_html=True)
        st.header("🤖 AI Configuration")
        
        # AI Provider Selection with enhanced styling
        ai_provider = st.selectbox(
            "Choose AI Provider",
            ["Gemini", "OpenAI", "Anthropic (Claude)", "Cohere", "xAI (Grok)", "Mistral AI", "Perplexity", "Together AI"],
            help="Select your preferred AI provider"
        )
        
        # Model Selection based on provider
        available_models = get_model_options(ai_provider)
        selected_model = st.selectbox(
            "Choose Model",
            available_models,
            help=f"Select the {ai_provider} model to use"
        )
        
        # API Key Input with enhanced styling
        api_key = st.text_input(
            f"Enter your {ai_provider} API Key",
            type="password",
            help=f"Your {ai_provider} API key will be used securely and not stored"
        )
        
        # API Key help text with enhanced styling
        api_info = get_api_info(ai_provider)
        if api_info["url"]:
            st.info(f"💡 {api_info['description']}: {api_info['url']}")
        
        st.divider()
        
        st.header("📁 Upload CV")
        uploaded_file = st.file_uploader(
            "Choose your CV file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        st.header("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Enter the complete job description including requirements, skills, and responsibilities..."
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area with enhanced layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.header("📄 CV Content")
        cv_text = ""
        
        if uploaded_file is not None:
            try:
                # Validate uploaded file
                validation_result = validate_file_upload(uploaded_file)
                
                if not validation_result["valid"]:
                    for error in validation_result["errors"]:
                        st.error(f"⚠️ File Validation Error: {error}")
                    logger.warning(f"Invalid file upload: {validation_result['errors']}")
                    return
                
                logger.info(f"Processing uploaded file: {uploaded_file.name} ({validation_result['file_info']['size_mb']:.1f}MB)")
                
                if uploaded_file.type == "application/pdf":
                    cv_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    cv_text = extract_text_from_docx(uploaded_file)
                elif uploaded_file.type == "text/plain":
                    cv_text = str(uploaded_file.read(), "utf-8")
                    logger.info(f"Successfully loaded text file: {uploaded_file.name}")
                
                # Enhanced file display
                st.success(f"✓ Successfully loaded {uploaded_file.name} ({validation_result['file_info']['size_mb']:.1f}MB)")
                with st.expander("View extracted content", expanded=False):
                    st.text_area("Extracted CV Text", cv_text[:2000] + "..." if len(cv_text) > 2000 else cv_text, height=300, disabled=True)
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"⚠️ Error reading file: {error_msg}")
                logger.error(f"File processing error for {uploaded_file.name}: {error_msg}")
                
                # Provide helpful suggestions
                if "PDF" in error_msg:
                    st.info("💡 Try converting your PDF to a text-based format or ensure it's not an image-based PDF.")
                elif "DOCX" in error_msg:
                    st.info("💡 Ensure your Word document is in .docx format and not corrupted.")
        else:
            cv_text = st.text_area(
                "Or paste your CV content here",
                height=300,
                placeholder="Paste your CV content here if you didn't upload a file..."
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.header("🔍 Analysis Configuration")
        
        # Enhanced configuration display
        theme = get_theme_config()
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0; color: {theme['primary_text']};">Current Configuration</h4>
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {theme['secondary_text']};">AI Provider:</span>
                    <span style="color: {theme['accent']}; font-weight: 600;">{ai_provider}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {theme['secondary_text']};">Model:</span>
                    <span style="color: {theme['accent']}; font-weight: 600;">{selected_model}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not api_key:
            st.warning(f"⚠️ Please enter your {ai_provider} API key in the sidebar to proceed.")
        
        # Enhanced analyze button
        analyze_clicked = st.button(
            "🚀 Analyze CV", 
            type="primary", 
            use_container_width=True,
            help="Start comprehensive CV analysis"
        )
        
        # Analysis execution with enhanced error handling and validation
        if analyze_clicked:
            logger.info("Analysis requested by user")
            
            # Validate API key
            api_validation = validate_api_key(ai_provider, api_key)
            if not api_validation["valid"]:
                for error in api_validation["errors"]:
                    st.error(f"⚠️ API Key Error: {error}")
                logger.warning(f"Invalid API key for {ai_provider}")
                return
            
            # Validate CV content
            if not cv_text.strip():
                st.error("⚠️ Please upload a CV file or paste CV content")
                logger.warning("Analysis attempted without CV content")
                return
            
            # Validate job description
            job_validation = validate_job_description(job_description)
            if not job_validation["valid"]:
                for error in job_validation["errors"]:
                    st.error(f"⚠️ Job Description Error: {error}")
                logger.warning("Invalid job description provided")
                return
            
            # Show warnings if any
            for warning in job_validation.get("warnings", []):
                st.warning(f"⚠️ {warning}")
            
            # Proceed with analysis
            with st.spinner(f"🧐 Analyzing CV with {ai_provider} {selected_model}..."):
                try:
                    logger.info(f"Starting analysis with {ai_provider} model {selected_model}")
                    
                    analysis_response = analyze_cv_with_ai(
                        ai_provider, api_key, selected_model, cv_text, job_description
                    )
                    
                    if analysis_response:
                        logger.info("Analysis completed successfully")
                        parsed_analysis = parse_analysis_response(analysis_response)
                        
                        if parsed_analysis:
                            st.session_state.analysis = parsed_analysis
                            logger.info(f"Analysis parsed successfully, overall score: {parsed_analysis.get('overall_score', 'N/A')}")
                            st.success("✓ Analysis completed successfully!")
                        else:
                            st.session_state.raw_analysis = analysis_response
                            logger.warning("Analysis completed but couldn't parse structured data")
                            st.warning("⚠️ Analysis completed, but couldn't parse structured data. Showing raw response.")
                    else:
                        logger.error("Empty response from AI provider")
                        st.error("⚠️ Received empty response from AI provider. Please try again.")
                        
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Analysis failed: {error_msg}")
                    st.error(f"⚠️ Error during analysis: {error_msg}")
                    
                    # Provide helpful suggestions based on error type
                    if "API key" in error_msg.lower():
                        st.info("💡 Please check your API key and ensure it's valid for the selected provider.")
                    elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                        st.info("💡 You may have exceeded your API quota or rate limit. Try again later or switch providers.")
                    elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                        st.info("💡 Network connection issue. Please check your internet connection and try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced analysis results display
    if 'analysis' in st.session_state:
        analysis = st.session_state.analysis
        theme = get_theme_config()
        
        st.divider()
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.header("📊 Analysis Results")
        
        # Enhanced Overall Score with dashboard-style metrics
        col1, col2, col3 = st.columns([2, 1, 1], gap="large")
        with col1:
            st.subheader("🚀 Overall CV Performance")
            display_score_meter(analysis['overall_score'], "Overall Match Score")
        
        with col2:
            # Additional metrics
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {theme['accent']}; font-size: 1.5rem;">
                    {len(analysis.get('sections', []))}
                </div>
                <div class="metric-label">Sections Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {theme['success']}; font-size: 1.5rem;">
                    {len(analysis.get('strengths', []))}
                </div>
                <div class="metric-label">Key Strengths</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Section Analysis with better styling
        st.subheader("📋 Section-wise Analysis")
        
        for section in analysis['sections']:
            # Determine section score color
            score = section['score']
            if score >= 8:
                score_color = theme['success']
                score_icon = "✓"
            elif score >= 6:
                score_color = theme['warning']
                score_icon = "⚠️"
            else:
                score_color = theme['error']
                score_icon = "⚠️"
            
            with st.expander(f"{score_icon} {section['section_name']} - Score: {score}/10", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if 'content' in section and section['content']:
                        st.write("**Content Summary:**")
                        st.info(section['content'][:200] + "..." if len(section['content']) > 200 else section['content'])
                    
                    st.write("**Feedback:**")
                    st.write(section['feedback'])
                    
                    st.write("**Improvements:**")
                    for i, improvement in enumerate(section['improvements'], 1):
                        st.write(f"{i}. {improvement}")
                
                with col2:
                    # Visual score representation
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="font-size: 2rem; color: {score_color}; font-weight: bold;">
                            {score}/10
                        </div>
                        <div style="width: 100%; background-color: {theme['border']}; border-radius: 10px; height: 8px; margin-top: 1rem;">
                            <div style="width: {score * 10}%; background: {score_color}; height: 100%; border-radius: 10px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Enhanced Strengths and Weaknesses with better visual hierarchy
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("✅ Key Strengths")
            for strength in analysis['strengths']:
                st.markdown(f"""
                <div style="background: {theme['success']}20; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {theme['success']};">
                    <span style="color: {theme['success']}; font-weight: 600;">✓</span> {strength}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("⚠️ Areas for Improvement")
            for weakness in analysis['weaknesses']:
                st.markdown(f"""
                <div style="background: {theme['warning']}20; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {theme['warning']};">
                    <span style="color: {theme['warning']}; font-weight: 600;">⚡</span> {weakness}
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced Missing Skills section
        st.subheader("🔧 Missing Skills & Requirements")
        if analysis['missing_skills']:
            cols = st.columns(3)
            for i, skill in enumerate(analysis['missing_skills']):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="background: {theme['error']}20; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {theme['error']}; text-align: center;">
                        <span style="color: {theme['error']}; font-weight: 600;">📌 {skill}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✓ No major skills missing! Great job!")
        
        # Enhanced Overall Recommendation
        st.subheader("💡 AI Recommendation")
        st.markdown(f"""
        <div class="metric-card" style="background: {theme['accent']}10; border-left: 4px solid {theme['accent']};">
            <div style="color: {theme['primary_text']}; line-height: 1.6;">
                {analysis['overall_recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif 'raw_analysis' in st.session_state:
        st.divider()
        st.header("📊 Analysis Results")
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {get_theme_config()['primary_text']};">Raw Analysis Response</h4>
            <div style="color: {get_theme_config()['secondary_text']}; line-height: 1.6; margin-top: 1rem;">
                {st.session_state.raw_analysis}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Footer with theme support
    st.divider()
    theme = get_theme_config()
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem; background: {theme['secondary_bg']}; border-radius: 12px; margin-top: 2rem;'>
        <h3 style='color: {theme['accent']}; margin-bottom: 1rem; font-weight: 600;'>Recruit AI</h3>
        <p style='color: {theme['primary_text']}; font-weight: 500; margin-bottom: 0.5rem;'>Multi-AI Provider Support</p>
        <p style='color: {theme['secondary_text']}; font-size: 0.9rem; margin-bottom: 1rem;'>Supports 8 AI Providers: Gemini, OpenAI, Claude, Cohere, xAI Grok, Mistral, Perplexity & Together AI</p>
        <div style='display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;'>
            <div style='background: {theme['success']}20; padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid {theme['success']};'>
                <span style='color: {theme['success']}; font-weight: 600;'>✓ Secure</span>
            </div>
            <div style='background: {theme['accent']}20; padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid {theme['accent']};'>
                <span style='color: {theme['accent']}; font-weight: 600;'>🚀 Fast</span>
            </div>
            <div style='background: {theme['warning']}20; padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid {theme['warning']};'>
                <span style='color: {theme['warning']}; font-weight: 600;'>🧐 Smart</span>
            </div>
        </div>
        <p style='color: {theme['secondary_text']}; font-size: 0.8rem; margin-top: 1.5rem; font-style: italic;'>Upload your CV and get instant feedback to improve your job application success rate!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
