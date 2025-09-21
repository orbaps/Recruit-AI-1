# Student Interface for Resume Upload and Instant Feedback
import streamlit as st
import json
import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from difflib import SequenceMatcher

# Import necessary functions from main app
try:
    from cv_ranking_app import (  # type: ignore
        extract_text_from_pdf, extract_text_from_docx, 
        analyze_cv_with_ai, parse_analysis_response,
        get_model_options, get_api_info
    )
except ImportError:
    # Fallback implementations - using Any to avoid type conflicts
    extract_text_from_pdf = lambda pdf_file: "Mock PDF text"  # type: ignore
    extract_text_from_docx = lambda docx_file: "Mock DOCX text"  # type: ignore
    analyze_cv_with_ai = lambda provider, api_key, model_name, cv_text, job_description: '{"overall_score": 85, "sections": []}'  # type: ignore
    parse_analysis_response = lambda response_text: {"overall_score": 85, "sections": []}  # type: ignore
    get_model_options = lambda provider: ["mock-model"]  # type: ignore
    get_api_info = lambda provider: {"url": "", "description": ""}  # type: ignore

def get_student_theme():
    """Get student-focused theme configuration"""
    return {
        'primary_bg': '#F8FAFC',
        'secondary_bg': '#FFFFFF', 
        'card_bg': '#FFFFFF',
        'primary_text': '#1A202C',
        'secondary_text': '#4A5568',
        'accent': '#4F46E5',
        'accent_light': '#EEF2FF',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'border': '#E5E7EB',
        'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }

def apply_student_css():
    """Apply student-focused CSS styling"""
    theme = get_student_theme()
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {{
        background: {theme['primary_bg']};
        font-family: 'Inter', sans-serif;
    }}
    
    .student-header {{
        background: {theme['gradient']};
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }}
    
    .upload-zone {{
        background: {theme['card_bg']};
        border: 2px dashed {theme['accent']};
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }}
    
    .upload-zone:hover {{
        border-color: {theme['accent']};
        background: {theme['accent_light']};
        transform: translateY(-2px);
    }}
    
    .feature-card {{
        background: {theme['card_bg']};
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid {theme['border']};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        height: 100%;
    }}
    
    .feature-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }}
    
    .score-card {{
        background: {theme['card_bg']};
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid {theme['border']};
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }}
    
    .comparison-card {{
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    .progress-indicator {{
        background: {theme['border']};
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }}
    
    .progress-fill {{
        background: {theme['gradient']};
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }}
    
    .timeline-item {{
        background: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        margin-left: 2rem;
    }}
    
    .timeline-item::before {{
        content: '';
        position: absolute;
        left: -12px;
        top: 1.5rem;
        width: 16px;
        height: 16px;
        background: {theme['accent']};
        border-radius: 50%;
        border: 4px solid {theme['primary_bg']};
    }}
    
    .fade-in {{
        animation: fadeIn 0.6s ease-in;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .slide-up {{
        animation: slideUp 0.5s ease-out;
    }}
    
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .improvement-item {{
        background: {theme['card_bg']};
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid {theme['accent']};
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    .strength-item {{
        background: linear-gradient(135deg, {theme['success']}15, {theme['success']}05);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {theme['success']};
        margin-bottom: 0.5rem;
    }}
    
    .weakness-item {{
        background: linear-gradient(135deg, {theme['warning']}15, {theme['warning']}05);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {theme['warning']};
        margin-bottom: 0.5rem;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def main():
    """Main function for Student Interface"""
    st.set_page_config(
        page_title="ResumeAI - Student Portal",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_student_css()
    
    # Initialize session state
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = 'welcome'
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'resume_history' not in st.session_state:
        st.session_state.resume_history = []
    
    # Navigation
    if not st.session_state.user_authenticated:
        if st.session_state.current_screen == 'welcome':
            render_welcome_screen()
        elif st.session_state.current_screen == 'login':
            render_login_registration()
    else:
        render_authenticated_interface()

def render_welcome_screen():
    """Render welcome/onboarding screen for new users"""
    theme = get_student_theme()
    
    st.markdown(f"""
    <div class="student-header fade-in">
        <h1 style="margin: 0 0 1rem 0; font-size: 3rem; font-weight: 800;">Welcome to ResumeAI</h1>
        <p style="font-size: 1.2rem; opacity: 0.9; margin: 0 0 2rem 0;">
            Get instant AI-powered feedback on your resume and improve your job prospects
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                ✨ Instant Analysis
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                📊 Detailed Feedback
            </span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                🚀 Career Growth
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features overview
    st.subheader("🎯 What You Can Do")
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        {
            "icon": "📄",
            "title": "Upload & Analyze",
            "description": "Upload your resume and get instant AI analysis with detailed feedback on every section."
        },
        {
            "icon": "📊",
            "title": "Track Progress",
            "description": "Compare different versions of your resume and track improvements over time."
        },
        {
            "icon": "🎯",
            "title": "Get Recommendations",
            "description": "Receive personalized suggestions to improve your resume for specific job roles."
        }
    ]
    
    for i, feature in enumerate(features):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="feature-card slide-up">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{feature['icon']}</div>
                <h4 style="margin: 0 0 1rem 0; color: {theme['primary_text']};">{feature['title']}</h4>
                <p style="color: {theme['secondary_text']}; line-height: 1.6; margin: 0;">
                    {feature['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # How it works
    st.subheader("🔄 How It Works")
    
    steps = [
        {"step": "1", "title": "Upload Resume", "desc": "Upload your PDF, DOCX, or text resume"},
        {"step": "2", "title": "AI Analysis", "desc": "Our AI analyzes your resume against industry standards"},
        {"step": "3", "title": "Get Feedback", "desc": "Receive detailed feedback and improvement suggestions"},
        {"step": "4", "title": "Improve & Resubmit", "desc": "Make improvements and track your progress"}
    ]
    
    cols = st.columns(4)
    for i, step in enumerate(steps):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="background: {theme['gradient']}; color: white; width: 50px; height: 50px; 
                           border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                           font-weight: bold; font-size: 1.2rem; margin: 0 auto 1rem auto;">
                    {step['step']}
                </div>
                <h5 style="margin: 0 0 0.5rem 0; color: {theme['primary_text']};">{step['title']}</h5>
                <p style="color: {theme['secondary_text']}; font-size: 0.9rem; margin: 0;">
                    {step['desc']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Ready to start
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <h3 style="color: {theme['primary_text']}; margin-bottom: 1rem;">Ready to improve your resume?</h3>
        <p style="color: {theme['secondary_text']}; margin-bottom: 2rem;">
            Join thousands of students who have improved their job prospects with AI-powered feedback
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.current_screen = 'login'
            st.rerun()

def render_login_registration():
    """Render login/registration screen with social options"""
    theme = get_student_theme()
    
    st.markdown(f"""
    <div class="student-header fade-in">
        <h1 style="margin: 0 0 1rem 0; font-size: 2.5rem; font-weight: 700;">Welcome to ResumeAI</h1>
        <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">
            Sign in to access your resume analysis history and track your progress
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Registration tabs
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_registration_form()

def render_login_form():
    """Render login form with social options"""
    theme = get_student_theme()
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("Sign In to Your Account")
        
        # Social login buttons
        st.markdown("**Quick Sign In:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("🔵 Continue with Google", use_container_width=True):
                st.success("Google OAuth integration would be implemented here")
                simulate_login("google_user@gmail.com", "Google User")
        
        with col2:
            if st.form_submit_button("💼 Continue with LinkedIn", use_container_width=True):
                st.success("LinkedIn OAuth integration would be implemented here")
                simulate_login("linkedin_user@linkedin.com", "LinkedIn User")
        
        st.markdown("**Or sign in with email:**")
        
        email = st.text_input("Email Address", placeholder="student@university.edu")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            st.markdown('<div style="text-align: right;"><a href="#" style="color: #4F46E5;">Forgot Password?</a></div>', unsafe_allow_html=True)
        
        if st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True):
            if email and password:
                simulate_login(email, email.split('@')[0].title())
            else:
                st.error("Please enter both email and password")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_registration_form():
    """Render registration form"""
    theme = get_student_theme()
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        st.subheader("Create Your Account")
        
        # Social registration
        st.markdown("**Quick Registration:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("🔵 Sign up with Google", use_container_width=True):
                st.success("Google OAuth registration would be implemented here")
                simulate_login("new_google_user@gmail.com", "New Google User")
        
        with col2:
            if st.form_submit_button("💼 Sign up with LinkedIn", use_container_width=True):
                st.success("LinkedIn OAuth registration would be implemented here")
                simulate_login("new_linkedin_user@linkedin.com", "New LinkedIn User")
        
        st.markdown("**Or create account with email:**")
        
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john.doe@university.edu")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # User type selection
        user_type = st.selectbox("I am a:", ["Student", "Job Seeker", "Recent Graduate"])
        
        # University/Institution (optional)
        university = st.text_input("University/Institution (Optional)", placeholder="Your University Name")
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        if st.form_submit_button("📝 Create Account", type="primary", use_container_width=True):
            if not all([full_name, email, password, confirm_password]):
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif not agree_terms:
                st.error("Please agree to the Terms of Service")
            else:
                simulate_login(email, full_name, user_type, university, is_new_user=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def simulate_login(email, name, user_type="Student", university="", is_new_user=False):
    """Simulate user login"""
    st.session_state.user_authenticated = True
    st.session_state.user_email = email
    st.session_state.user_name = name
    st.session_state.user_type = user_type
    st.session_state.university = university
    st.session_state.is_new_user = is_new_user
    
    if is_new_user:
        st.session_state.current_screen = 'onboarding'
    else:
        st.session_state.current_screen = 'dashboard'
    
    st.success(f"Welcome {'to ResumeAI' if is_new_user else 'back'}, {name}!")
    st.rerun()

def render_authenticated_interface():
    """Render the authenticated user interface"""
    # Navigation sidebar
    with st.sidebar:
        render_navigation()
    
    # Main content based on current screen
    if st.session_state.current_screen == 'onboarding':
        render_onboarding_screen()
    elif st.session_state.current_screen == 'dashboard':
        render_student_dashboard()
    elif st.session_state.current_screen == 'upload':
        render_upload_interface()
    elif st.session_state.current_screen == 'progress':
        render_progress_screen()
    elif st.session_state.current_screen == 'compare':
        render_comparison_screen()
    elif st.session_state.current_screen == 'tips':
        render_tips_screen()

def render_navigation():
    """Render navigation sidebar"""
    theme = get_student_theme()
    user_name = st.session_state.get('user_name', 'Student')
    
    st.markdown(f"""
    <div style="background: {theme['gradient']}; padding: 1.5rem; border-radius: 12px; 
                margin-bottom: 2rem; text-align: center; color: white;">
        <h3 style="margin: 0 0 0.5rem 0;">👋 {user_name}</h3>
        <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">Student Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    menu_items = [
        ("🏠", "Dashboard", "dashboard"),
        ("📄", "Upload Resume", "upload"),
        ("📊", "Progress", "progress"),
        ("🔄", "Compare Versions", "compare"),
        ("💡", "Tips & Guides", "tips")
    ]
    
    for icon, label, screen in menu_items:
        if st.button(f"{icon} {label}", key=f"nav_{screen}", 
                    use_container_width=True,
                    type="primary" if st.session_state.current_screen == screen else "secondary"):
            st.session_state.current_screen = screen
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    resume_count = len(st.session_state.get('resume_history', []))
    latest_score = st.session_state.get('latest_score', 'N/A')
    
    st.markdown(f"""
    <div style="background: {theme['card_bg']}; padding: 1rem; border-radius: 8px; 
                border: 1px solid {theme['border']};">
        <h5 style="margin: 0 0 1rem 0; color: {theme['primary_text']};">📈 Your Stats</h5>
        <div style="margin-bottom: 0.5rem;">
            <span style="color: {theme['secondary_text']};">Resumes Analyzed:</span>
            <strong style="color: {theme['accent']};">{resume_count}</strong>
        </div>
        <div>
            <span style="color: {theme['secondary_text']};">Latest Score:</span>
            <strong style="color: {theme['success']};">{latest_score}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_onboarding_screen():
    """Render onboarding screen for new users"""
    theme = get_student_theme()
    user_name = st.session_state.get('user_name', 'Student')
    
    st.markdown(f"""
    <div class="student-header fade-in">
        <h1 style="margin: 0 0 1rem 0; font-size: 2.5rem; font-weight: 700;">Welcome, {user_name}! 🎉</h1>
        <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">
            Let's get you started with your resume improvement journey
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Onboarding steps
    st.subheader("🚀 Let's Get Started")
    
    # Step 1: Profile Setup
    with st.expander("✅ Step 1: Complete Your Profile", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            field_of_study = st.selectbox(
                "Field of Study",
                ["Computer Science", "Engineering", "Business", "Liberal Arts", "Sciences", "Other"]
            )
            
            experience_level = st.selectbox(
                "Experience Level",
                ["No experience", "Internships only", "0-1 years", "1-3 years", "3+ years"]
            )
        
        with col2:
            career_goals = st.multiselect(
                "Career Interests",
                ["Software Development", "Data Science", "Product Management", 
                 "Marketing", "Finance", "Consulting", "Research", "Entrepreneurship"]
            )
            
            target_companies = st.text_input(
                "Target Companies (Optional)",
                placeholder="Google, Microsoft, Startup, etc."
            )
        
        if st.button("💾 Save Profile", type="primary"):
            st.session_state.user_profile = {
                'field_of_study': field_of_study,
                'experience_level': experience_level,
                'career_goals': career_goals,
                'target_companies': target_companies
            }
            st.success("✅ Profile saved successfully!")
    
    # Step 2: Upload First Resume
    with st.expander("📄 Step 2: Upload Your First Resume", expanded=False):
        st.info("💡 Upload your current resume to get instant feedback and see where you stand")
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume for AI analysis"
        )
        
        if uploaded_file:
            if st.button("🚀 Analyze My Resume", type="primary"):
                st.session_state.current_screen = 'upload'
                st.rerun()
    
    # Step 3: Quick Tutorial
    with st.expander("📚 Step 3: Quick Tutorial", expanded=False):
        st.markdown("""
        **Here's what you can do with ResumeAI:**
        
        1. **📄 Upload & Analyze**: Get instant feedback on your resume
        2. **📊 Track Progress**: See how your resume improves over time
        3. **🔄 Compare Versions**: Side-by-side comparison of different resume versions
        4. **💡 Get Tips**: Access our library of resume improvement guides
        
        **Pro Tips:**
        - Upload different versions to track your progress
        - Use job descriptions for targeted feedback
        - Check back regularly for new features and tips
        """)
        
        if st.button("✅ I'm Ready!", type="primary"):
            st.session_state.current_screen = 'dashboard'
            st.rerun()
    
    # Skip onboarding
    st.markdown("---")
    if st.button("⏭️ Skip Onboarding", type="secondary"):
        st.session_state.current_screen = 'dashboard'
        st.rerun()

def render_student_dashboard():
    """Render main student dashboard"""
    theme = get_student_theme()
    user_name = st.session_state.get('user_name', 'Student')
    
    # Dashboard header
    st.markdown(f"""
    <div style="background: {theme['gradient']}; padding: 2rem; border-radius: 16px; 
                margin-bottom: 2rem; color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h2 style="margin: 0 0 0.5rem 0;">Welcome back, {user_name}! 👋</h2>
                <p style="margin: 0; opacity: 0.9;">Ready to improve your resume and boost your career prospects?</p>
            </div>
            <div style="text-align: right;">
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    📊 Resume Score: {st.session_state.get('latest_score', 'N/A')}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.8;">
                    Last analyzed: {st.session_state.get('last_analysis', 'Never')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Upload New Resume", use_container_width=True, type="primary"):
            st.session_state.current_screen = 'upload'
            st.rerun()
    
    with col2:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state.current_screen = 'progress'
            st.rerun()
    
    with col3:
        if st.button("🔄 Compare Versions", use_container_width=True):
            st.session_state.current_screen = 'compare'
            st.rerun()
    
    with col4:
        if st.button("💡 Get Tips", use_container_width=True):
            st.session_state.current_screen = 'tips'
            st.rerun()
    
    # Recent activity
    st.subheader("📈 Your Resume Journey")
    
    if 'resume_history' not in st.session_state or not st.session_state.resume_history:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 3rem; border-radius: 16px; 
                    border: 2px dashed {theme['border']}; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <h4 style="color: {theme['primary_text']}; margin-bottom: 1rem;">No resumes uploaded yet</h4>
            <p style="color: {theme['secondary_text']}; margin-bottom: 2rem;">
                Upload your first resume to get started with AI-powered feedback
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        render_resume_history()
    
    # Performance overview
    if st.session_state.get('resume_history'):
        st.subheader("📊 Performance Overview")
        render_performance_charts()

def render_upload_interface():
    """Render resume upload interface"""
    st.info("Upload your resume here to get instant feedback!")

def render_resume_history():
    """Render resume upload history"""
    st.info("📈 Resume history will be displayed here once you upload multiple resumes!")

def render_performance_charts():
    """Render performance overview charts"""
    st.info("📊 Performance charts will be displayed here to track your progress!")

def render_progress_screen():
    """Render progress tracking screen"""
    st.info("📊 Progress tracking feature - Upload multiple resumes to see your improvement over time!")

def render_comparison_screen():
    """Render version comparison screen"""
    st.info("🔄 Version comparison feature - Compare your current resume feedback with previous versions!")

def render_tips_screen():
    """Render tips and guides screen"""
    st.info("💡 Tips and guides feature - Get expert advice on resume writing!")

if __name__ == "__main__":
    main()
