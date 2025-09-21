import streamlit as st
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Welcome to Innomatics Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_onboarding_theme():
    """Get onboarding-specific theme"""
    return {
        'primary_bg': '#ffffff',
        'secondary_bg': '#f8fafc',
        'card_bg': '#ffffff',
        'primary_text': '#1e293b',
        'secondary_text': '#64748b',
        'accent': '#3b82f6',
        'accent_hover': '#2563eb',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'border': '#e2e8f0',
        'shadow': 'rgba(0, 0, 0, 0.1)',
        'gradient_1': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient_2': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'gradient_3': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
    }

def apply_onboarding_css():
    """Apply onboarding-specific CSS"""
    theme = get_onboarding_theme()
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Onboarding Styling */
    .stApp {{
        background: {theme['gradient_1']} !important;
        color: {theme['primary_text']} !important;
        font-family: 'Inter', sans-serif !important;
        min-height: 100vh !important;
    }}
    
    /* Hero Section */
    .hero-section {{
        background: {theme['card_bg']} !important;
        padding: 4rem 2rem !important;
        border-radius: 24px !important;
        box-shadow: 0 20px 60px {theme['shadow']} !important;
        text-align: center !important;
        margin: 3rem 0 !important;
        border: 1px solid {theme['border']} !important;
        backdrop-filter: blur(20px) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    .hero-section::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: {theme['gradient_2']} !important;
        opacity: 0.03 !important;
        animation: rotate 20s linear infinite !important;
        z-index: 0 !important;
    }}
    
    .hero-content {{
        position: relative !important;
        z-index: 1 !important;
    }}
    
    /* Feature Cards */
    .feature-card {{
        background: {theme['card_bg']} !important;
        padding: 2.5rem 2rem !important;
        border-radius: 20px !important;
        border: 1px solid {theme['border']} !important;
        box-shadow: 0 12px 40px {theme['shadow']} !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
        transition: all 0.4s ease !important;
        height: 100% !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
        transition: left 0.5s ease;
    }}
    
    .feature-card:hover {{
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 60px {theme['shadow']} !important;
        border-color: {theme['accent']} !important;
    }}
    
    .feature-card:hover::before {{
        left: 100%;
    }}
    
    /* Process Steps */
    .process-step {{
        background: {theme['card_bg']} !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 2px solid {theme['border']} !important;
        margin-bottom: 2rem !important;
        position: relative !important;
        transition: all 0.3s ease !important;
    }}
    
    .process-step:hover {{
        border-color: {theme['accent']} !important;
        box-shadow: 0 8px 32px {theme['shadow']} !important;
    }}
    
    .step-number {{
        position: absolute !important;
        top: -15px !important;
        left: 2rem !important;
        background: {theme['accent']} !important;
        color: white !important;
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }}
    
    /* CTA Buttons */
    .cta-button {{
        background: {theme['gradient_1']} !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1.5rem 3rem !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3) !important;
        cursor: pointer !important;
        text-decoration: none !important;
        display: inline-block !important;
        margin: 1rem !important;
    }}
    
    .cta-button:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 48px rgba(59, 130, 246, 0.4) !important;
    }}
    
    .cta-secondary {{
        background: transparent !important;
        color: {theme['accent']} !important;
        border: 2px solid {theme['accent']} !important;
    }}
    
    .cta-secondary:hover {{
        background: {theme['accent']} !important;
        color: white !important;
    }}
    
    /* Stats Section */
    .stats-container {{
        background: {theme['card_bg']} !important;
        padding: 3rem 2rem !important;
        border-radius: 20px !important;
        border: 1px solid {theme['border']} !important;
        margin: 3rem 0 !important;
        text-align: center !important;
    }}
    
    .stat-item {{
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .stat-item:hover {{
        transform: scale(1.05) !important;
    }}
    
    .stat-number {{
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: {theme['accent']} !important;
        margin-bottom: 0.5rem !important;
        font-family: 'Poppins', sans-serif !important;
    }}
    
    .stat-label {{
        color: {theme['secondary_text']} !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.9rem !important;
    }}
    
    /* Testimonial Section */
    .testimonial-card {{
        background: {theme['card_bg']} !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 1px solid {theme['border']} !important;
        box-shadow: 0 8px 32px {theme['shadow']} !important;
        margin: 1rem !important;
        position: relative !important;
    }}
    
    .testimonial-quote {{
        font-size: 1.1rem !important;
        line-height: 1.8 !important;
        color: {theme['primary_text']} !important;
        font-style: italic !important;
        margin-bottom: 1.5rem !important;
    }}
    
    .testimonial-author {{
        display: flex !important;
        align-items: center !important;
        gap: 1rem !important;
    }}
    
    .author-avatar {{
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        background: {theme['gradient_2']} !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }}
    
    /* Animations */
    .fade-in-up {{
        animation: fadeInUp 0.8s ease-out !important;
    }}
    
    .fade-in-left {{
        animation: fadeInLeft 1s ease-out !important;
    }}
    
    .fade-in-right {{
        animation: fadeInRight 1s ease-out !important;
    }}
    
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(60px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes fadeInLeft {{
        from {{
            opacity: 0;
            transform: translateX(-60px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes fadeInRight {{
        from {{
            opacity: 0;
            transform: translateX(60px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes rotate {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .hero-section {{
            padding: 3rem 1.5rem !important;
            margin: 2rem 0 !important;
        }}
        
        .feature-card {{
            padding: 2rem 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }}
        
        .cta-button {{
            padding: 1.2rem 2rem !important;
            font-size: 1rem !important;
            margin: 0.5rem !important;
        }}
        
        .stat-number {{
            font-size: 2.5rem !important;
        }}
    }}
    </style>
    \"\"\"
    
    st.markdown(css, unsafe_allow_html=True)

def render_hero_section():
    \"\"\"Render hero section\"\"\"
    theme = get_onboarding_theme()
    
    st.markdown(f\"\"\"
    <div class=\"hero-section fade-in-up\">
        <div class=\"hero-content\">
            <h1 style=\"margin: 0 0 1.5rem 0; font-size: 3.5rem; font-weight: 800; color: {theme['primary_text']}; font-family: 'Poppins', sans-serif;\">
                Welcome to <span style=\"color: {theme['accent']};\">Innomatics</span> 🎓
            </h1>
            <p style=\"font-size: 1.4rem; color: {theme['secondary_text']}; margin-bottom: 2rem; line-height: 1.6; max-width: 800px; margin-left: auto; margin-right: auto;\">
                Transform your career with AI-powered resume analysis and personalized feedback. 
                Join thousands of students who've accelerated their professional growth.
            </p>
            
            <div style=\"margin-top: 3rem;\">
                <a href=\"#get-started\" class=\"cta-button\">
                    🚀 Start Your Journey
                </a>
                <a href=\"#learn-more\" class=\"cta-button cta-secondary\">
                    📖 Learn More
                </a>
            </div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

def render_features_section():
    \"\"\"Render features section\"\"\"
    st.markdown('<div id=\"learn-more\"></div>', unsafe_allow_html=True)
    st.markdown(\"<h2 style='text-align: center; color: white; font-size: 2.5rem; font-weight: 700; margin: 4rem 0 3rem 0;'>Why Choose Innomatics? ✨</h2>\", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        {
            \"icon\": \"🤖\",
            \"title\": \"AI-Powered Analysis\",
            \"description\": \"Get detailed insights from advanced AI models that analyze your resume comprehensively and provide actionable feedback.\",
            \"animation\": \"fade-in-left\"
        },
        {
            \"icon\": \"📈\",
            \"title\": \"Progress Tracking\",
            \"description\": \"Monitor your improvement over time with detailed analytics and visual progress reports that show your career growth.\",
            \"animation\": \"fade-in-up\"
        },
        {
            \"icon\": \"🎯\",
            \"title\": \"Personalized Guidance\",
            \"description\": \"Receive customized recommendations tailored to your career goals and industry requirements for maximum impact.\",
            \"animation\": \"fade-in-right\"
        }
    ]
    
    for i, feature in enumerate(features):
        with [col1, col2, col3][i]:
            st.markdown(f\"\"\"
            <div class=\"feature-card {feature['animation']}\">
                <div style=\"font-size: 4rem; margin-bottom: 1.5rem;\">{feature['icon']}</div>
                <h3 style=\"margin: 0 0 1rem 0; color: {get_onboarding_theme()['primary_text']}; font-weight: 700;\">
                    {feature['title']}
                </h3>
                <p style=\"color: {get_onboarding_theme()['secondary_text']}; line-height: 1.6; margin: 0;\">
                    {feature['description']}
                </p>
            </div>
            \"\"\", unsafe_allow_html=True)

def render_process_section():
    \"\"\"Render how it works section\"\"\"
    st.markdown(\"<h2 style='text-align: center; color: white; font-size: 2.5rem; font-weight: 700; margin: 4rem 0 3rem 0;'>How It Works 🔄</h2>\", unsafe_allow_html=True)
    
    steps = [
        {
            \"number\": \"1\",
            \"title\": \"Upload Your Resume\",
            \"description\": \"Simply drag and drop your resume in PDF, DOCX, or TXT format. Our system supports all major file types.\",
            \"icon\": \"📄\"
        },
        {
            \"number\": \"2\", 
            \"title\": \"AI Analysis\",
            \"description\": \"Our advanced AI analyzes your resume against industry standards and provides comprehensive feedback.\",
            \"icon\": \"🔍\"
        },
        {
            \"number\": \"3\",
            \"title\": \"Get Personalized Feedback\",
            \"description\": \"Receive detailed insights, improvement suggestions, and a roadmap to enhance your professional profile.\",
            \"icon\": \"💡\"
        },
        {
            \"number\": \"4\",
            \"title\": \"Track Your Progress\",
            \"description\": \"Monitor your improvements over time and see how your resume score increases with each iteration.\",
            \"icon\": \"📊\"
        }
    ]
    
    for step in steps:
        st.markdown(f\"\"\"
        <div class=\"process-step fade-in-up\">
            <div class=\"step-number\">{step['number']}</div>
            <div style=\"display: flex; align-items: center; gap: 2rem; margin-left: 3rem;\">
                <div style=\"font-size: 3rem;\">{step['icon']}</div>
                <div>
                    <h3 style=\"margin: 0 0 0.5rem 0; color: {get_onboarding_theme()['primary_text']}; font-weight: 700;\">
                        {step['title']}
                    </h3>
                    <p style=\"margin: 0; color: {get_onboarding_theme()['secondary_text']}; line-height: 1.6;\">
                        {step['description']}
                    </p>
                </div>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)

def render_stats_section():
    \"\"\"Render statistics section\"\"\"
    theme = get_onboarding_theme()
    
    st.markdown(f\"\"\"
    <div class=\"stats-container fade-in-up\">
        <h2 style=\"margin: 0 0 3rem 0; color: {theme['primary_text']}; font-weight: 700; font-size: 2.2rem;\">
            Trusted by Students Worldwide 🌍
        </h2>
        
        <div style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;\">
            <div class=\"stat-item\">
                <div class=\"stat-number\">10K+</div>
                <div class=\"stat-label\">Students Helped</div>
            </div>
            <div class=\"stat-item\">
                <div class=\"stat-number\">95%</div>
                <div class=\"stat-label\">Improvement Rate</div>
            </div>
            <div class=\"stat-item\">
                <div class=\"stat-number\">500+</div>
                <div class=\"stat-label\">Companies Hiring</div>
            </div>
            <div class=\"stat-item\">
                <div class=\"stat-number\">4.9★</div>
                <div class=\"stat-label\">Student Rating</div>
            </div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

def render_testimonials():
    \"\"\"Render testimonials section\"\"\"
    st.markdown(\"<h2 style='text-align: center; color: white; font-size: 2.5rem; font-weight: 700; margin: 4rem 0 3rem 0;'>What Students Say 💬</h2>\", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    testimonials = [
        {
            \"quote\": \"Innomatics helped me improve my resume score from 65% to 89% in just two weeks. The AI feedback was incredibly detailed and actionable!\",
            \"author\": \"Priya Sharma\",
            \"role\": \"Computer Science Graduate\",
            \"avatar\": \"PS\"
        },
        {
            \"quote\": \"The progress tracking feature is amazing. I could see exactly how each change improved my resume. Got placed at my dream company!\",
            \"author\": \"Rahul Verma\",
            \"role\": \"Data Science Student\",
            \"avatar\": \"RV\"
        }
    ]
    
    for i, testimonial in enumerate(testimonials):
        with [col1, col2][i]:
            st.markdown(f\"\"\"
            <div class=\"testimonial-card fade-in-up\">
                <div class=\"testimonial-quote\">
                    \"{testimonial['quote']}\"
                </div>
                <div class=\"testimonial-author\">
                    <div class=\"author-avatar\">{testimonial['avatar']}</div>
                    <div>
                        <div style=\"font-weight: 700; color: {get_onboarding_theme()['primary_text']};\">
                            {testimonial['author']}
                        </div>
                        <div style=\"color: {get_onboarding_theme()['secondary_text']}; font-size: 0.9rem;\">
                            {testimonial['role']}
                        </div>
                    </div>
                </div>
            </div>
            \"\"\", unsafe_allow_html=True)

def render_cta_section():
    \"\"\"Render final call-to-action section\"\"\"
    theme = get_onboarding_theme()
    
    st.markdown('<div id=\"get-started\"></div>', unsafe_allow_html=True)
    
    st.markdown(f\"\"\"
    <div class=\"hero-section fade-in-up\" style=\"margin: 4rem 0 2rem 0;\">
        <div class=\"hero-content\">
            <h2 style=\"margin: 0 0 1.5rem 0; font-size: 2.8rem; font-weight: 800; color: {theme['primary_text']}; font-family: 'Poppins', sans-serif;\">
                Ready to Transform Your Career? 🚀
            </h2>
            <p style=\"font-size: 1.3rem; color: {theme['secondary_text']}; margin-bottom: 2.5rem; line-height: 1.6;\">
                Join thousands of students who've already improved their resumes and landed their dream jobs.
            </p>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(\"<div style='text-align: center; margin: 2rem 0;'>\", unsafe_allow_html=True)
        
        if st.button(\"🎓 Student Portal\", type=\"primary\", use_container_width=True, help=\"Access the student interface for resume analysis\"):
            st.session_state.redirect_to = 'student'
            st.success(\"🚀 Redirecting to Student Portal...\")
            time.sleep(2)
            # In a real app, this would redirect to student_interface.py
            st.info(\"👉 In the actual implementation, this would redirect to the Student Portal\")
        
        if st.button(\"💼 Placement Team Dashboard\", use_container_width=True, help=\"Access the placement team dashboard\"):
            st.session_state.redirect_to = 'placement'
            st.success(\"🚀 Redirecting to Placement Dashboard...\")
            time.sleep(2)
            # In a real app, this would redirect to placement_dashboard.py
            st.info(\"👉 In the actual implementation, this would redirect to the Placement Dashboard\")
        
        st.markdown(\"</div>\", unsafe_allow_html=True)

def render_footer():
    \"\"\"Render footer section\"\"\"
    theme = get_onboarding_theme()
    
    st.markdown(f\"\"\"
    <div style='background: {theme['card_bg']}; padding: 3rem 2rem; border-radius: 20px; margin-top: 4rem; border: 1px solid {theme['border']};'>
        <div style='text-align: center;'>
            <h3 style='color: {theme['accent']}; margin-bottom: 2rem; font-weight: 700; font-size: 1.8rem;'>
                Innomatics Research Labs
            </h3>
            
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-bottom: 2rem; text-align: left;'>
                <div>
                    <h4 style='color: {theme['primary_text']}; margin-bottom: 1rem; font-weight: 600;'>For Students</h4>
                    <div style='color: {theme['secondary_text']}; line-height: 2;'>
                        • Resume Analysis<br>
                        • Career Guidance<br>
                        • Progress Tracking<br>
                        • Interview Preparation
                    </div>
                </div>
                
                <div>
                    <h4 style='color: {theme['primary_text']}; margin-bottom: 1rem; font-weight: 600;'>For Placement Teams</h4>
                    <div style='color: {theme['secondary_text']}; line-height: 2;'>
                        • Batch Processing<br>
                        • Candidate Ranking<br>
                        • Analytics Dashboard<br>
                        • Automated Feedback
                    </div>
                </div>
                
                <div>
                    <h4 style='color: {theme['primary_text']}; margin-bottom: 1rem; font-weight: 600;'>Locations</h4>
                    <div style='color: {theme['secondary_text']}; line-height: 2;'>
                        • Hyderabad<br>
                        • Bangalore<br>
                        • Pune<br>
                        • Delhi NCR
                    </div>
                </div>
            </div>
            
            <div style='border-top: 1px solid {theme['border']}; padding-top: 2rem; color: {theme['secondary_text']}; font-size: 0.9rem;'>
                <p style='margin-bottom: 1rem;'>
                    Contact: <a href='mailto:info@innomatics.in' style='color: {theme['accent']};'>info@innomatics.in</a> | 
                    Phone: +91-9999999999 | 
                    <a href='#' style='color: {theme['accent']};'>Privacy Policy</a> | 
                    <a href='#' style='color: {theme['accent']};'>Terms of Service</a>
                </p>
                <p style='margin: 0;'>
                    © {datetime.now().year} Innomatics Research Labs. All rights reserved. | 
                    Empowering careers with AI-driven insights.
                </p>
            </div>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)

def main():
    \"\"\"Main onboarding application\"\"\"
    # Apply custom CSS
    apply_onboarding_css()
    
    # Hide Streamlit default elements
    st.markdown(\"\"\"
    <style>
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stAppHeader {display:none;}
    </style>
    \"\"\", unsafe_allow_html=True)
    
    # Render sections
    render_hero_section()
    render_features_section()
    render_process_section()
    render_stats_section()
    render_testimonials()
    render_cta_section()
    render_footer()
    
    # Handle redirects
    if 'redirect_to' in st.session_state:
        if st.session_state.redirect_to == 'student':
            st.balloons()
        elif st.session_state.redirect_to == 'placement':
            st.snow()

if __name__ == \"__main__\":
    main()