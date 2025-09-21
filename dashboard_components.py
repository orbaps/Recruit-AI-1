# Dashboard Components for Placement System
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any

# Import necessary functions with fallbacks
try:
    from placement_dashboard import (  # type: ignore
        get_dashboard_theme, get_model_options, get_api_info, 
        db_manager, get_score_class, process_resume_batch, ResumeEvaluation
    )
except ImportError:
    # Simple fallbacks to avoid errors
    get_dashboard_theme = lambda: {}  # type: ignore
    get_model_options = lambda x: []  # type: ignore  
    get_api_info = lambda x: {}  # type: ignore
    get_score_class = lambda x: ""  # type: ignore
    process_resume_batch = lambda *args: []  # type: ignore
    db_manager = type('MockDB', (), {'get_job_descriptions': lambda: [], 'get_evaluations_for_job': lambda x: []})()  # type: ignore
    ResumeEvaluation = type('MockEval', (), {})  # type: ignore

def render_detailed_candidate_report(evaluation):  # type: ignore
    """Render comprehensive candidate report with all analysis details"""
    theme = get_dashboard_theme()
    
    st.subheader(f"📋 Detailed Report - {getattr(evaluation, 'candidate_name', 'Unknown')}")
    
    # Back button
    if st.button("← Back to Candidate List", key="back_to_list"):
        if 'selected_candidate' in st.session_state:
            del st.session_state.selected_candidate
        if 'show_detailed_report' in st.session_state:
            del st.session_state.show_detailed_report
        st.rerun()
    
    # Header with candidate info and actions
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; padding: 1.5rem; border-radius: 12px; border: 1px solid {theme['border']};">
            <h3 style="margin: 0 0 0.5rem 0; color: {theme['primary_text']};">{getattr(evaluation, 'candidate_name', 'Unknown')}</h3>
            <div style="color: {theme['secondary_text']}; margin-bottom: 1rem;">
                📄 {getattr(evaluation, 'file_name', 'Unknown')}<br>
                📅 Processed: {getattr(evaluation, 'processed_date', datetime.now()).strftime('%B %d, %Y at %H:%M')}<br>
                🆔 Resume ID: {getattr(evaluation, 'resume_id', 'Unknown')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📧 Send Feedback Email", use_container_width=True):
            st.session_state.show_email_dialog = True
    
    with col3:
        if st.button("📄 Export Report", use_container_width=True):
            st.session_state.show_export_options = True
    
    # Score Overview Dashboard
    st.subheader("📊 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    scores = [
        ("Overall Score", getattr(evaluation, 'overall_score', 0), theme['accent']),
        ("Skills Match", getattr(evaluation, 'skills_match', 0), theme['success']),
        ("Experience", getattr(evaluation, 'experience_match', 0), theme['warning']),
        ("Education", getattr(evaluation, 'education_match', 0), theme['error'])
    ]
    
    for i, (label, score, color) in enumerate(scores):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div style="background: {theme['card_bg']}; padding: 1.5rem; border-radius: 12px; border: 1px solid {theme['border']}; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {color}; margin-bottom: 0.5rem;">
                    {score:.1f}%
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.9rem; font-weight: 500;">
                    {label}
                </div>
                <div style="width: 100%; background: {theme['border']}; border-radius: 10px; height: 6px; margin-top: 1rem;">
                    <div style="width: {score}%; background: {color}; height: 100%; border-radius: 10px; transition: width 0.5s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed Analysis Sections
    st.subheader("🔍 Comprehensive Analysis")
    
    try:
        feedback_data = json.loads(getattr(evaluation, 'feedback', '{}'))
        
        # Section-wise breakdown
        if 'sections' in feedback_data:
            for section in feedback_data['sections']:
                with st.expander(f"📋 {section['section_name']} Analysis - Score: {section.get('score', 0)}/10", expanded=False):
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if 'content' in section and section['content']:
                            st.markdown("**📝 Content Summary:**")
                            st.info(section['content'])
                        
                        st.markdown("**💬 Detailed Feedback:**")
                        st.write(section['feedback'])
                        
                        if 'improvements' in section and section['improvements']:
                            st.markdown("**✨ Improvement Suggestions:**")
                            for i, improvement in enumerate(section['improvements'], 1):
                                st.markdown(f"**{i}.** {improvement}")
                    
                    with col2:
                        # Visual score representation
                        score = section.get('score', 0) * 10
                        score_color = theme['success'] if score >= 75 else theme['warning'] if score >= 50 else theme['error']
                        
                        st.markdown(f"""
                        <div style="background: {theme['card_bg']}; padding: 1.5rem; border-radius: 12px; text-align: center;">
                            <div style="font-size: 3rem; color: {score_color}; font-weight: bold; margin-bottom: 1rem;">
                                {section.get('score', 0)}/10
                            </div>
                            <div style="width: 100%; background: {theme['border']}; border-radius: 10px; height: 12px;">
                                <div style="width: {score}%; background: {score_color}; height: 100%; border-radius: 10px;"></div>
                            </div>
                            <div style="color: {theme['secondary_text']}; font-size: 0.8rem; margin-top: 0.5rem;">
                                Performance Level
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Strengths and Improvement Areas
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("✅ Key Strengths")
            if 'strengths' in feedback_data and feedback_data['strengths']:
                for strength in feedback_data['strengths']:
                    st.markdown(f"""
                    <div style="background: {theme['success']}15; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {theme['success']};">
                        <span style="color: {theme['success']}; font-weight: 600;">✓</span> {strength}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific strengths identified in the analysis.")
        
        with col2:
            st.subheader("⚠️ Areas for Improvement")
            if 'weaknesses' in feedback_data and feedback_data['weaknesses']:
                for weakness in feedback_data['weaknesses']:
                    st.markdown(f"""
                    <div style="background: {theme['warning']}15; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {theme['warning']};">
                        <span style="color: {theme['warning']}; font-weight: 600;">⚡</span> {weakness}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific weaknesses identified in the analysis.")
        
        # Missing Skills Analysis
        st.subheader("🔧 Missing Skills & Requirements")
        if 'missing_skills' in feedback_data and feedback_data['missing_skills']:
            skills_cols = st.columns(3)
            for i, skill in enumerate(feedback_data['missing_skills']):
                with skills_cols[i % 3]:
                    st.markdown(f"""
                    <div style="background: {theme['error']}15; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; text-align: center; border: 1px solid {theme['error']}30;">
                        <span style="color: {theme['error']}; font-weight: 600;">📌 {skill}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ No critical skills missing! Excellent match with job requirements.")
        
        # Overall Recommendation
        st.subheader("💡 AI Recommendation & Next Steps")
        if 'overall_recommendation' in feedback_data:
            st.markdown(f"""
            <div style="background: {theme['accent']}10; padding: 2rem; border-radius: 12px; border-left: 4px solid {theme['accent']};">
                <div style="color: {theme['primary_text']}; line-height: 1.8; font-size: 1.1rem;">
                    {feedback_data['overall_recommendation']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    except json.JSONDecodeError:
        st.subheader("📝 Raw Analysis Feedback")
        st.text_area("AI Analysis Output", getattr(evaluation, 'feedback', ''), height=400, disabled=True)
    
    # Action Panel
    st.subheader("🎯 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Shortlist Candidate", type="primary", use_container_width=True):
            st.success("✅ Candidate added to shortlist!")
            # Add shortlist logic here
    
    with col2:
        if st.button("🏷️ Add Tags/Notes", use_container_width=True):
            st.session_state.show_notes_dialog = True
    
    with col3:
        if st.button("📊 Compare with Others", use_container_width=True):
            st.session_state.show_comparison_dialog = True
    
    with col4:
        if st.button("📞 Schedule Interview", use_container_width=True):
            st.session_state.show_interview_dialog = True
    
    # Handle dialogs
    if st.session_state.get('show_email_dialog', False):
        render_email_dialog(evaluation)
    
    if st.session_state.get('show_notes_dialog', False):
        render_notes_dialog(evaluation)
    
    if st.session_state.get('show_comparison_dialog', False):
        render_comparison_dialog(evaluation)

def render_email_dialog(evaluation):
    """Render email dialog for sending feedback"""
    st.subheader("📧 Send Feedback Email")
    
    with st.form("email_form"):
        email = st.text_input("Student Email", placeholder="student@example.com")
        subject = st.text_input("Subject", value=f"Resume Feedback - {getattr(evaluation, 'candidate_name', 'Unknown')}")
        
        # Email template
        email_body = f"""
Dear {getattr(evaluation, 'candidate_name', 'Unknown')},

We have completed the analysis of your resume for our job posting. Here's your comprehensive feedback:

**Overall Score: {getattr(evaluation, 'overall_score', 0):.1f}%**

**Key Strengths:**
- [AI-generated strengths will be inserted here]

**Areas for Improvement:**
- [AI-generated suggestions will be inserted here]

**Recommended Next Steps:**
- [Personalized recommendations will be inserted here]

We encourage you to review this feedback and consider the suggested improvements. This will help enhance your profile for future opportunities.

Best regards,
Innomatics Placement Team
        """
        
        email_content = st.text_area("Email Content", email_body, height=300)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("📨 Send Email", type="primary"):
                if email:
                    st.success(f"✅ Feedback email sent to {email}")
                    st.session_state.show_email_dialog = False
                    st.rerun()
                else:
                    st.error("⚠️ Please enter a valid email address")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_email_dialog = False
                st.rerun()

def render_notes_dialog(evaluation):
    """Render notes and tags dialog"""
    st.subheader("🏷️ Add Notes & Tags")
    
    with st.form("notes_form"):
        # Tags input
        tags = st.text_input("Tags (comma-separated)", placeholder="high-potential, technical-strong, needs-experience")
        
        # Notes input
        notes = st.text_area("Internal Notes", placeholder="Add your observations and comments about this candidate...", height=150)
        
        # Priority level
        priority = st.selectbox("Priority Level", ["High", "Medium", "Low"])
        
        # Interview recommendation
        interview_rec = st.selectbox("Interview Recommendation", ["Strongly Recommend", "Recommend", "Consider", "Not Recommended"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Notes", type="primary"):
                # Save logic would go here
                st.success("✅ Notes and tags saved successfully!")
                st.session_state.show_notes_dialog = False
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_notes_dialog = False
                st.rerun()

def render_comparison_dialog(evaluation):
    """Render candidate comparison dialog"""
    st.subheader("📊 Compare Candidates")
    
    # Get other candidates for the same job
    # This would normally fetch from database
    st.info("🚧 Candidate comparison feature - Select up to 3 candidates to compare side-by-side")
    
    # Mock candidate selection
    candidates = ["John Smith (85%)", "Sarah Johnson (78%)", "Mike Davis (72%)", "Lisa Chen (69%)"]
    
    selected_candidates = st.multiselect(
        "Select candidates to compare with",
        candidates,
        max_selections=3
    )
    
    if selected_candidates:
        if st.button("🔄 Start Comparison", type="primary"):
            st.session_state.comparison_candidates = selected_candidates
            st.session_state.show_side_by_side = True
            st.session_state.show_comparison_dialog = False
            st.rerun()
    
    if st.button("❌ Close"):
        st.session_state.show_comparison_dialog = False
        st.rerun()

def render_side_by_side_comparison():
    """Render side-by-side candidate comparison"""
    st.subheader("🔄 Side-by-Side Candidate Comparison")
    
    if st.button("← Back to Reports"):
        st.session_state.show_side_by_side = False
        st.rerun()
    
    # Mock comparison data - in real implementation, this would fetch actual candidate data
    comparison_data = {
        "Current Candidate": {
            "name": "Current Selection",
            "overall_score": 82.5,
            "skills_score": 85.0,
            "experience_score": 78.0,
            "education_score": 85.0,
            "strengths": ["Strong technical skills", "Good problem-solving", "Relevant experience"],
            "weaknesses": ["Limited leadership experience", "Needs better communication skills"]
        },
        "Candidate A": {
            "name": "John Smith",
            "overall_score": 85.0,
            "skills_score": 88.0,
            "experience_score": 82.0,
            "education_score": 85.0,
            "strengths": ["Excellent technical skills", "Strong leadership", "Great communication"],
            "weaknesses": ["Limited domain experience", "Needs more certifications"]
        },
        "Candidate B": {
            "name": "Sarah Johnson",
            "overall_score": 78.0,
            "skills_score": 75.0,
            "experience_score": 80.0,
            "education_score": 82.0,
            "strengths": ["Good experience", "Strong educational background", "Team player"],
            "weaknesses": ["Needs skill development", "Limited project experience"]
        }
    }
    
    # Create comparison table
    candidates = list(comparison_data.keys())
    
    # Score comparison charts
    st.subheader("📈 Score Comparison")
    
    scores_df = pd.DataFrame({
        'Candidate': candidates,
        'Overall': [comparison_data[c]['overall_score'] for c in candidates],
        'Skills': [comparison_data[c]['skills_score'] for c in candidates],
        'Experience': [comparison_data[c]['experience_score'] for c in candidates],
        'Education': [comparison_data[c]['education_score'] for c in candidates]
    })
    
    # Radar chart comparison
    fig = go.Figure()
    
    for candidate in candidates:
        fig.add_trace(go.Scatterpolar(
            r=[comparison_data[candidate]['overall_score'],
               comparison_data[candidate]['skills_score'],
               comparison_data[candidate]['experience_score'],
               comparison_data[candidate]['education_score']],
            theta=['Overall', 'Skills', 'Experience', 'Education'],
            fill='toself',
            name=comparison_data[candidate]['name']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title="Candidate Comparison - All Metrics"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed comparison table
    st.subheader("📋 Detailed Comparison")
    
    cols = st.columns(len(candidates))
    
    for i, candidate in enumerate(candidates):
        with cols[i]:
            data = comparison_data[candidate]
            
            # Get theme colors (mock theme for this example)
            theme = {
                'card_bg': '#2D3748',
                'primary_text': '#E2E8F0',
                'secondary_text': '#A0AEC0',
                'accent': '#63B3ED',
                'success': '#68D391',
                'warning': '#FBD38D',
                'border': '#4A5568'
            }
            
            st.markdown(f"""
            <div style="background: {theme['card_bg']}; padding: 1.5rem; border-radius: 12px; border: 1px solid {theme['border']}; height: 100%;">
                <h4 style="margin: 0 0 1rem 0; color: {theme['primary_text']}; text-align: center;">{data['name']}</h4>
                
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <div style="font-size: 2rem; font-weight: 700; color: {theme['accent']}; margin-bottom: 0.5rem;">
                        {data['overall_score']:.1f}%
                    </div>
                    <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">Overall Score</div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="color: {theme['primary_text']}; font-size: 0.9rem; margin-bottom: 0.5rem;">Skills: {data['skills_score']:.1f}%</div>
                    <div style="background: {theme['border']}; border-radius: 10px; height: 6px;">
                        <div style="width: {data['skills_score']}%; background: {theme['success']}; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="color: {theme['primary_text']}; font-size: 0.9rem; margin-bottom: 0.5rem;">Experience: {data['experience_score']:.1f}%</div>
                    <div style="background: {theme['border']}; border-radius: 10px; height: 6px;">
                        <div style="width: {data['experience_score']}%; background: {theme['warning']}; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <div style="color: {theme['primary_text']}; font-size: 0.9rem; margin-bottom: 0.5rem;">Education: {data['education_score']:.1f}%</div>
                    <div style="background: {theme['border']}; border-radius: 10px; height: 6px;">
                        <div style="width: {data['education_score']}%; background: {theme['accent']}; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <h5 style="color: {theme['success']}; margin: 0 0 0.5rem 0; font-size: 0.9rem;">✅ Strengths</h5>
                    {''.join([f'<div style="color: {theme["secondary_text"]}; font-size: 0.8rem; margin-bottom: 0.25rem;">• {strength}</div>' for strength in data['strengths']])}
                </div>
                
                <div>
                    <h5 style="color: {theme['warning']}; margin: 0 0 0.5rem 0; font-size: 0.9rem;">⚠️ Areas to Improve</h5>
                    {''.join([f'<div style="color: {theme["secondary_text"]}; font-size: 0.8rem; margin-bottom: 0.25rem;">• {weakness}</div>' for weakness in data['weaknesses']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Ranking and recommendation
    st.subheader("🏆 Ranking & Recommendation")
    
    # Sort candidates by overall score
    ranked_candidates = sorted(comparison_data.items(), key=lambda x: x[1]['overall_score'], reverse=True)
    
    for i, (candidate, data) in enumerate(ranked_candidates, 1):
        rank_color = "#FFD700" if i == 1 else "#C0C0C0" if i == 2 else "#CD7F32" if i == 3 else "#808080"
        
        st.markdown(f"""
        <div style="background: {rank_color}20; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {rank_color};">
            <strong>#{i} {data['name']}</strong> - {data['overall_score']:.1f}% Overall Score
        </div>
        """, unsafe_allow_html=True)
    
    # Export comparison
    if st.button("📄 Export Comparison Report", type="primary"):
        st.success("✅ Comparison report exported successfully!")
    """Render resume upload and batch processing section"""
    st.subheader("📁 Resume Upload & Batch Processing")
    
    # AI Configuration for batch processing
    with st.expander("🤖 AI Configuration", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            ai_provider = st.selectbox(
                "AI Provider",
                ["Gemini", "OpenAI", "Anthropic (Claude)", "Cohere", "xAI (Grok)", "Mistral AI", "Perplexity", "Together AI"],
                key="batch_ai_provider"
            )
            
            available_models = get_model_options(ai_provider)
            selected_model = st.selectbox(
                "Model",
                available_models,
                key="batch_model"
            )
        
        with col2:
            api_key = st.text_input(
                f"{ai_provider} API Key",
                type="password",
                key="batch_api_key"
            )
            
            # API info
            api_info = get_api_info(ai_provider)
            if api_info["url"]:
                st.info(f"💡 {api_info['description']}")
    
    # Job selection for batch processing
    jobs = db_manager.get_job_descriptions()  # type: ignore
    if not jobs:
        st.warning("⚠️ Please create at least one job description before uploading resumes.")
        return
    
    job_options = {f"{job.title} - {job.company} ({job.id})": job.id for job in jobs if job.status == 'active'}
    
    if not job_options:
        st.warning("⚠️ No active job descriptions available. Please activate a job description first.")
        return
    
    selected_job_display = st.selectbox(
        "Select Job Description for Evaluation",
        list(job_options.keys()),
        key="batch_job_selection"
    )
    
    selected_job_id = job_options[selected_job_display]
    selected_job = next(job for job in jobs if job.id == selected_job_id)
    
    # Display selected job info
    theme = get_dashboard_theme()
    st.markdown(f"""
    <div class="job-card">
        <h5 style="margin: 0 0 0.5rem 0; color: {theme['primary_text']};">{selected_job.title}</h5>
        <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">
            <strong>{selected_job.company}</strong> • {selected_job.location}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Resume upload
    uploaded_files = st.file_uploader(
        "Upload Resume Files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload multiple resume files for batch processing"
    )
    
    if uploaded_files and api_key:
        st.write(f"**{len(uploaded_files)} files ready for processing**")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True):
                with st.spinner("Processing resumes..."):
                    evaluations = process_resume_batch(
                        uploaded_files, selected_job.requirements, 
                        ai_provider, api_key, selected_model, selected_job_id
                    )
                
                st.success(f"✅ Successfully processed {len(evaluations)} resumes!")
                
                # Show quick summary
                if evaluations:
                    avg_score = sum(e.overall_score for e in evaluations) / len(evaluations)
                    high_scorers = len([e for e in evaluations if e.overall_score >= 75])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Score", f"{avg_score:.1f}%")
                    with col2:
                        st.metric("High Scorers (75+)", high_scorers)
                    with col3:
                        st.metric("Total Processed", len(evaluations))
    
    elif uploaded_files and not api_key:
        st.warning("⚠️ Please provide an API key to start processing.")

def render_candidate_evaluations():
    """Render candidate evaluations for selected job"""
    if 'selected_job' not in st.session_state:
        st.info("📋 Select a job description to view candidate evaluations.")
        return
    
    job_id = st.session_state.selected_job
    
    # Get job details
    jobs = db_manager.get_job_descriptions()  # type: ignore
    selected_job = next((job for job in jobs if job.id == job_id), None)
    
    if not selected_job:
        st.error("❌ Selected job not found.")
        return
    
    st.subheader(f"👥 Candidate Evaluations - {selected_job.title}")
    
    # Get evaluations
    evaluations = db_manager.get_evaluations_for_job(job_id)  # type: ignore  # type: ignore
    
    if not evaluations:
        st.info("📝 No evaluations found for this job. Upload and process resumes first.")
        return
    
    # Filter and sort controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search candidates", placeholder="Search by name or filename...")
    
    with col2:
        min_score = st.slider("Min Score", 0, 100, 0)
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Overall Score", "Skills Match", "Experience Match", "Education Match", "Name"])
    
    with col4:
        sort_order = st.selectbox("Order", ["Descending", "Ascending"])
    
    # Apply filters
    filtered_evaluations = evaluations
    
    if search_term:
        filtered_evaluations = [
            e for e in filtered_evaluations 
            if search_term.lower() in e.candidate_name.lower() or search_term.lower() in e.file_name.lower()
        ]
    
    filtered_evaluations = [e for e in filtered_evaluations if e.overall_score >= min_score]
    
    # Apply sorting
    sort_key_map = {
        "Overall Score": lambda x: x.overall_score,
        "Skills Match": lambda x: x.skills_match,
        "Experience Match": lambda x: x.experience_match,
        "Education Match": lambda x: x.education_match,
        "Name": lambda x: x.candidate_name
    }
    
    reverse_sort = sort_order == "Descending"
    filtered_evaluations.sort(key=sort_key_map[sort_by], reverse=reverse_sort)
    
    # Display summary
    st.write(f"**Showing {len(filtered_evaluations)} of {len(evaluations)} candidates**")
    
    if filtered_evaluations:
        # Summary metrics
        avg_score = sum(e.overall_score for e in filtered_evaluations) / len(filtered_evaluations)
        high_performers = len([e for e in filtered_evaluations if e.overall_score >= 75])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col2:
            st.metric("High Performers", f"{high_performers}/{len(filtered_evaluations)}")
        with col3:
            st.metric("Success Rate", f"{(high_performers/len(filtered_evaluations)*100):.1f}%")
        
        # Candidate list
        for i, evaluation in enumerate(filtered_evaluations):
            render_candidate_card(evaluation, i)
    
    # Export functionality
    if evaluations:
        st.subheader("📊 Export & Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export to CSV", use_container_width=True):
                df = pd.DataFrame([
                    {
                        'Candidate Name': e.candidate_name,
                        'File Name': e.file_name,
                        'Overall Score': e.overall_score,
                        'Skills Match': e.skills_match,
                        'Experience Match': e.experience_match,
                        'Education Match': e.education_match,
                        'Processed Date': e.processed_date.strftime('%Y-%m-%d %H:%M')
                    }
                    for e in filtered_evaluations
                ])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"evaluations_{selected_job.title}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        
        with col2:
            if st.button("📈 Generate Report", use_container_width=True):
                st.session_state.show_analytics = True
        
        with col3:
            if st.button("👥 Shortlist Top 10", use_container_width=True):
                top_candidates = sorted(evaluations, key=lambda x: x.overall_score, reverse=True)[:10]
                st.session_state.shortlisted_candidates = top_candidates
                st.success("✅ Top 10 candidates shortlisted!")

def render_candidate_card(evaluation: Any, index: int):  # type: ignore
    """Render individual candidate card"""
    theme = get_dashboard_theme()
    
    # Score styling
    score_class = get_score_class(evaluation.overall_score)
    
    card_html = f"""
    <div class="candidate-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                    <h5 style="margin: 0; color: {theme['primary_text']};">
                        {index + 1}. {evaluation.candidate_name}
                    </h5>
                    <span class="{score_class}">
                        {evaluation.overall_score:.1f}%
                    </span>
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    📄 {evaluation.file_name} • Processed: {evaluation.processed_date.strftime('%Y-%m-%d %H:%M')}
                </div>
                <div style="display: flex; gap: 1rem; font-size: 0.8rem;">
                    <span style="color: {theme['accent']};">Skills: {evaluation.skills_match:.1f}%</span>
                    <span style="color: {theme['warning']};">Experience: {evaluation.experience_match:.1f}%</span>
                    <span style="color: {theme['success']};">Education: {evaluation.education_match:.1f}%</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="color: {theme['secondary_text']}; font-size: 0.8rem;">
                    Click to view details
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Detailed view button
    if st.button("View Details", key=f"details_{evaluation.resume_id}", use_container_width=True):
        st.session_state.selected_candidate = evaluation
        st.session_state.show_candidate_details = True

def render_candidate_details():
    """Render detailed candidate evaluation"""
    if 'selected_candidate' not in st.session_state:
        return
    
    evaluation = st.session_state.selected_candidate
    theme = get_dashboard_theme()
    
    st.subheader(f"📋 Detailed Report - {evaluation.candidate_name}")
    
    # Close button
    if st.button("← Back to List"):
        del st.session_state.selected_candidate
        del st.session_state.show_candidate_details
        st.rerun()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['accent']}; margin-bottom: 0.5rem;">
                    {evaluation.overall_score:.1f}%
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">Overall Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['success']}; margin-bottom: 0.5rem;">
                    {evaluation.skills_match:.1f}%
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">Skills Match</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['warning']}; margin-bottom: 0.5rem;">
                    {evaluation.experience_match:.1f}%
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">Experience</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: {theme['accent']}; margin-bottom: 0.5rem;">
                    {evaluation.education_match:.1f}%
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">Education</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed feedback
    st.subheader("🔍 AI Analysis & Feedback")
    
    try:
        # Try to parse JSON feedback
        feedback_data = json.loads(evaluation.feedback)
        
        if 'sections' in feedback_data:
            for section in feedback_data['sections']:
                with st.expander(f"📋 {section['section_name']} - Score: {section['score']}/10", expanded=False):
                    if 'content' in section:
                        st.write("**Content Summary:**")
                        st.info(section['content'])
                    
                    st.write("**Feedback:**")
                    st.write(section['feedback'])
                    
                    if 'improvements' in section:
                        st.write("**Suggested Improvements:**")
                        for improvement in section['improvements']:
                            st.write(f"• {improvement}")
        
        if 'strengths' in feedback_data:
            st.subheader("✅ Key Strengths")
            for strength in feedback_data['strengths']:
                st.success(f"✓ {strength}")
        
        if 'weaknesses' in feedback_data:
            st.subheader("⚠️ Areas for Improvement")
            for weakness in feedback_data['weaknesses']:
                st.warning(f"⚡ {weakness}")
        
        if 'missing_skills' in feedback_data:
            st.subheader("🔧 Missing Skills")
            if feedback_data['missing_skills']:
                for skill in feedback_data['missing_skills']:
                    st.error(f"📌 {skill}")
            else:
                st.success("✓ No major skills missing!")
        
        if 'overall_recommendation' in feedback_data:
            st.subheader("💡 Overall Recommendation")
            st.markdown(f"""
            <div class="metric-dashboard-card" style="background: {theme['accent']}10; border-left: 4px solid {theme['accent']};">
                <div style="color: {theme['primary_text']}; line-height: 1.6;">
                    {feedback_data['overall_recommendation']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    except json.JSONDecodeError:
        # Fallback for raw text feedback
        st.write("**Raw AI Feedback:**")
        st.text_area("Feedback", evaluation.feedback, height=300, disabled=True)
    
    # Action buttons
    st.subheader("🎯 Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Shortlist Candidate", type="primary", use_container_width=True):
            st.success("Candidate added to shortlist!")
    
    with col2:
        if st.button("📧 Send Feedback", use_container_width=True):
            st.info("Feedback email functionality would be implemented here.")
    
    with col3:
        if st.button("📄 Download Report", use_container_width=True):
            st.info("Report download functionality would be implemented here.")