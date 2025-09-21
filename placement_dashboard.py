import streamlit as st
import pandas as pd
import json
import io
import time
import zipfile
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Tuple, Any
import re
from dataclasses import dataclass
from enum import Enum
import sqlite3
import hashlib
from pathlib import Path
import logging

# Import configuration and utilities
try:
    from config import Config, setup_logging
    logger = setup_logging()
except ImportError:
    # Fallback logging setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Import the CV analysis functions from the main app
from cv_ranking_app import (
    extract_text_from_pdf, extract_text_from_docx, 
    analyze_cv_with_ai, parse_analysis_response,
    get_model_options, get_api_info
)

# Page Configuration
st.set_page_config(
    page_title="Innomatics Placement Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data Models
@dataclass
class JobDescription:
    id: str
    title: str
    company: str
    location: str
    requirements: str
    created_date: datetime
    status: str
    priority: str

@dataclass
class ResumeEvaluation:
    resume_id: str
    job_id: str
    candidate_name: str
    overall_score: float
    skills_match: float
    experience_match: float
    education_match: float
    feedback: str
    processed_date: datetime
    file_name: str

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Database Management
class DatabaseManager:
    def __init__(self, db_path="placement_system.db"):
        self.db_path = db_path
        self.init_database()
        logger.info(f"Database manager initialized with path: {db_path}")
    
    def get_connection(self):
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise Exception(f"Database connection failed: {str(e)}")
    
    def init_database(self):
        """Initialize database tables with improved error handling"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Job descriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    requirements TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    priority TEXT DEFAULT 'medium'
                )
            """)
            
            # Resume evaluations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_evaluations (
                    id TEXT PRIMARY KEY,
                    resume_id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    candidate_name TEXT,
                    overall_score REAL,
                    skills_match REAL,
                    experience_match REAL,
                    education_match REAL,
                    feedback TEXT,
                    processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_name TEXT,
                    FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
                )
            """)
            
            # Processing queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_queue (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    total_resumes INTEGER,
                    processed_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
                )
            """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise Exception(f"Database initialization failed: {str(e)}")
        finally:
            if conn is not None:
                conn.close()
    
    def save_job_description(self, job: JobDescription):
        """Save job description to database with improved error handling"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO job_descriptions 
                (id, title, company, location, requirements, created_date, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (job.id, job.title, job.company, job.location, 
                  job.requirements, job.created_date, job.status, job.priority))
            
            conn.commit()
            logger.info(f"Job description saved successfully: {job.id}")
        except sqlite3.Error as e:
            logger.error(f"Error saving job description {job.id}: {str(e)}")
            raise Exception(f"Failed to save job description: {str(e)}")
        finally:
            if conn is not None:
                conn.close()
    
    def get_job_descriptions(self) -> List[JobDescription]:
        """Get all job descriptions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM job_descriptions ORDER BY created_date DESC")
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append(JobDescription(
                id=row[0], title=row[1], company=row[2], location=row[3],
                requirements=row[4], created_date=datetime.fromisoformat(row[5]),
                status=row[6], priority=row[7]
            ))
        return jobs
    
    def save_resume_evaluation(self, evaluation: ResumeEvaluation):
        """Save resume evaluation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        eval_id = hashlib.md5(f"{evaluation.resume_id}_{evaluation.job_id}".encode()).hexdigest()
        
        cursor.execute("""
            INSERT OR REPLACE INTO resume_evaluations 
            (id, resume_id, job_id, candidate_name, overall_score, skills_match, 
             experience_match, education_match, feedback, processed_date, file_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (eval_id, evaluation.resume_id, evaluation.job_id, evaluation.candidate_name,
              evaluation.overall_score, evaluation.skills_match, evaluation.experience_match,
              evaluation.education_match, evaluation.feedback, evaluation.processed_date, evaluation.file_name))
        
        conn.commit()
        conn.close()
    
    def get_evaluations_for_job(self, job_id: str) -> List[ResumeEvaluation]:
        """Get all evaluations for a specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT resume_id, job_id, candidate_name, overall_score, skills_match,
                   experience_match, education_match, feedback, processed_date, file_name
            FROM resume_evaluations 
            WHERE job_id = ? 
            ORDER BY overall_score DESC
        """, (job_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        evaluations = []
        for row in rows:
            evaluations.append(ResumeEvaluation(
                resume_id=row[0], job_id=row[1], candidate_name=row[2],
                overall_score=row[3], skills_match=row[4], experience_match=row[5],
                education_match=row[6], feedback=row[7], 
                processed_date=datetime.fromisoformat(row[8]), file_name=row[9]
            ))
        return evaluations

# Additional Dashboard Components (simplified version)

# Dashboard Components
def render_dashboard_header():
    """Render the main dashboard header"""
    theme = get_dashboard_theme()
    
    st.markdown(f"""
    <div class="dashboard-header fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; color: {theme['primary_text']}; font-size: 2rem; font-weight: 700;">
                    🎯 Innomatics Placement Dashboard
                </h1>
                <p style="margin: 0.5rem 0 0 0; color: {theme['secondary_text']}; font-size: 1.1rem;">
                    AI-Powered Resume Relevance Check System
                </p>
            </div>
            <div style="text-align: right;">
                <div style="color: {theme['accent']}; font-size: 0.9rem; font-weight: 500;">
                    {datetime.now().strftime('%B %d, %Y')}
                </div>
                <div style="color: {theme['secondary_text']}; font-size: 0.8rem;">
                    Multi-Location Operations
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics_overview():
    """Render key metrics overview"""
    theme = get_dashboard_theme()
    
    # Get statistics from database
    conn = sqlite3.connect(db_manager.db_path)
    
    # Active jobs count
    active_jobs = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM job_descriptions WHERE status = 'active'", conn
    ).iloc[0]['count']
    
    # Total evaluations today
    today = datetime.now().date()
    evaluations_today = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM resume_evaluations WHERE DATE(processed_date) = ?", 
        conn, params=[today.strftime('%Y-%m-%d')]
    ).iloc[0]['count']
    
    # Average score
    avg_score_result = pd.read_sql_query(
        "SELECT AVG(overall_score) as avg_score FROM resume_evaluations WHERE DATE(processed_date) = ?",
        conn, params=[today.strftime('%Y-%m-%d')]
    ).iloc[0]['avg_score']
    avg_score = round(avg_score_result, 1) if avg_score_result else 0.0
    
    # Processing queue status
    pending_jobs = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM processing_queue WHERE status = 'pending'", conn
    ).iloc[0]['count']
    
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2rem; font-weight: 700; color: {theme['accent']}; margin-bottom: 0.5rem;">
                        {active_jobs}
                    </div>
                    <div style="color: {theme['secondary_text']}; font-size: 0.9rem; font-weight: 500;">
                        Active Job Postings
                    </div>
                </div>
                <div style="font-size: 2rem; color: {theme['accent']}30;">
                    💼
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2rem; font-weight: 700; color: {theme['success']}; margin-bottom: 0.5rem;">
                        {evaluations_today}
                    </div>
                    <div style="color: {theme['secondary_text']}; font-size: 0.9rem; font-weight: 500;">
                        Resumes Processed Today
                    </div>
                </div>
                <div style="font-size: 2rem; color: {theme['success']}30;">
                    📄
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2rem; font-weight: 700; color: {theme['warning']}; margin-bottom: 0.5rem;">
                        {avg_score}%
                    </div>
                    <div style="color: {theme['secondary_text']}; font-size: 0.9rem; font-weight: 500;">
                        Average Relevance Score
                    </div>
                </div>
                <div style="font-size: 2rem; color: {theme['warning']}30;">
                    📊
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status_color = theme['error'] if pending_jobs > 0 else theme['success']
        status_icon = "⏳" if pending_jobs > 0 else "✓"
        
        st.markdown(f"""
        <div class="metric-dashboard-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2rem; font-weight: 700; color: {status_color}; margin-bottom: 0.5rem;">
                        {pending_jobs}
                    </div>
                    <div style="color: {theme['secondary_text']}; font-size: 0.9rem; font-weight: 500;">
                        Pending Batches
                    </div>
                </div>
                <div style="font-size: 2rem; color: {status_color}30;">
                    {status_icon}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_job_management():
    """Render job description management section"""
    st.subheader("💼 Job Description Management")
    
    # Job creation form
    with st.expander("➕ Create New Job Description", expanded=False):
        with st.form("new_job_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                job_title = st.text_input("Job Title", placeholder="e.g., Senior Data Scientist")
                company_name = st.text_input("Company Name", placeholder="e.g., TechCorp Inc.")
                location = st.selectbox("Location", [
                    "Hyderabad", "Bangalore", "Pune", "Delhi NCR", "Mumbai", "Chennai", "Remote", "Other"
                ])
            
            with col2:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                status = st.selectbox("Status", ["Active", "Draft", "Closed"])
            
            job_requirements = st.text_area(
                "Job Requirements & Description",
                height=200,
                placeholder="Enter detailed job description including required skills, experience, qualifications..."
            )
            
            if st.form_submit_button("🚀 Create Job Description", type="primary"):
                if job_title and company_name and job_requirements:
                    job = JobDescription(
                        id=generate_job_id(job_title, company_name),
                        title=job_title,
                        company=company_name,
                        location=location,
                        requirements=job_requirements,
                        created_date=datetime.now(),
                        status=status.lower(),
                        priority=priority.lower()
                    )
                    
                    db_manager.save_job_description(job)
                    st.success(f"✓ Job description created successfully! ID: {job.id}")
                    st.rerun()
                else:
                    st.error("⚠️ Please fill in all required fields")
    
    # Display existing jobs
    jobs = db_manager.get_job_descriptions()
    
    if jobs:
        st.write(f"**Active Job Descriptions ({len(jobs)})**")
        
        for job in jobs:
            theme = get_dashboard_theme()
            
            # Priority indicator
            priority_colors = {
                'high': theme['error'],
                'medium': theme['warning'],
                'low': theme['success']
            }
            priority_color = priority_colors.get(job.priority, theme['secondary_text'])
            
            st.markdown(f"""
            <div class="job-card">
                <div>
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: {theme['primary_text']};">{job.title}</h4>
                        <span style="background: {priority_color}20; color: {priority_color}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                            {job.priority.upper()}
                        </span>
                        <span style="background: {theme['accent']}20; color: {theme['accent']}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                            {job.status.upper()}
                        </span>
                    </div>
                    <div style="color: {theme['secondary_text']}; margin-bottom: 0.5rem;">
                        <strong>{job.company}</strong> • {job.location} • Created: {job.created_date.strftime('%Y-%m-%d')}
                    </div>
                    <div style="color: {theme['secondary_text']}; font-size: 0.9rem;">
                        ID: {job.id}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📁 No job descriptions created yet. Create your first job description above.")

# Main Application
def main():
    # Apply custom CSS
    apply_dashboard_css()
    
    # Initialize session state
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'dashboard'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Theme toggle
        current_theme = st.session_state.dashboard_theme
        theme_icon = "🌙" if current_theme == 'light' else "☀️"
        
        if st.button(f"{theme_icon} Toggle Theme", use_container_width=True):
            st.session_state.dashboard_theme = 'light' if current_theme == 'dark' else 'dark'
            st.rerun()
        
        st.divider()
        
        # Navigation menu
        st.subheader("📈 Navigation")
        
        nav_options = {
            "🏠 Dashboard Overview": "dashboard",
            "💼 Job Management": "jobs", 
            "📁 Resume Upload": "upload",
            "📅 Schedule & Queue": "schedule",
            "📈 Analytics": "analytics"
        }
        
        for label, mode in nav_options.items():
            if st.button(label, key=f"nav_{mode}", use_container_width=True):
                st.session_state.view_mode = mode
                st.rerun()
        
        st.divider()
        
        # Quick stats in sidebar
        st.subheader("📊 Quick Stats")
        
        # Get quick metrics
        conn = sqlite3.connect(db_manager.db_path)
        total_jobs = pd.read_sql_query("SELECT COUNT(*) as count FROM job_descriptions", conn).iloc[0]['count']
        total_evaluations = pd.read_sql_query("SELECT COUNT(*) as count FROM resume_evaluations", conn).iloc[0]['count']
        conn.close()
        
        st.metric("Total Jobs", total_jobs)
        st.metric("Total Evaluations", total_evaluations)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    render_dashboard_header()
    
    # Route to different views
    if st.session_state.view_mode == 'dashboard':
        render_metrics_overview()
        st.subheader("🕒 Recent Activity")
        st.info("📄 Recent evaluations will be displayed here. Start by creating job descriptions and uploading resumes!")
        
    elif st.session_state.view_mode == 'jobs':
        render_job_management()
        
    elif st.session_state.view_mode == 'upload':
        st.subheader("📁 Resume Upload & Batch Processing")
        st.info("🚧 Resume upload functionality coming soon! This will support batch processing of multiple resumes.")
        
    elif st.session_state.view_mode == 'analytics':
        st.subheader("📈 Analytics Dashboard")
        st.info("🚧 Advanced analytics coming soon! This will include score distributions, trend analysis, and performance metrics.")
        
    elif st.session_state.view_mode == 'schedule':
        st.subheader("📅 Processing Schedule & Queue")
        st.info("🚧 Queue management and scheduling features coming soon!")
    
    # Footer
    st.divider()
    theme = get_dashboard_theme()
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem; background: {theme['card_bg']}; border-radius: 12px; margin-top: 2rem;'>
        <h4 style='color: {theme['accent']}; margin-bottom: 1rem;'>Innomatics Research Labs</h4>
        <p style='color: {theme['secondary_text']}; margin-bottom: 0;'>AI-Powered Placement Dashboard • Multi-Location Operations • Scalable Resume Processing</p>
        <div style='margin-top: 1rem; display: flex; justify-content: center; gap: 2rem;'>
            <span style='color: {theme['success']}; font-weight: 600;'>✓ Hyderabad</span>
            <span style='color: {theme['success']}; font-weight: 600;'>✓ Bangalore</span>
            <span style='color: {theme['success']}; font-weight: 600;'>✓ Pune</span>
            <span style='color: {theme['success']}; font-weight: 600;'>✓ Delhi NCR</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# Initialize database
db_manager = DatabaseManager()

# Theme Configuration (Enhanced for Placement Dashboard)
def get_dashboard_theme():
    """Get dashboard-specific theme configuration"""
    if 'dashboard_theme' not in st.session_state:
        st.session_state.dashboard_theme = 'dark'  # Default to dark theme for professional look
    
    themes = {
        'dark': {
            'primary_bg': '#0f1419',
            'secondary_bg': '#1e2a3a',
            'card_bg': '#2a3441',
            'primary_text': '#e2e8f0',
            'secondary_text': '#94a3b8',
            'accent': '#3b82f6',
            'accent_hover': '#1d4ed8',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'border': '#374151',
            'shadow': 'rgba(0, 0, 0, 0.25)'
        },
        'light': {
            'primary_bg': '#ffffff',
            'secondary_bg': '#f8fafc',
            'card_bg': '#ffffff',
            'primary_text': '#1e293b',
            'secondary_text': '#64748b',
            'accent': '#2563eb',
            'accent_hover': '#1d4ed8',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'border': '#e2e8f0',
            'shadow': 'rgba(0, 0, 0, 0.1)'
        }
    }
    return themes[st.session_state.dashboard_theme]

def apply_dashboard_css():
    """Apply dashboard-specific CSS styling"""
    theme = get_dashboard_theme()
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Dashboard Styling */
    .stApp {{
        background: linear-gradient(135deg, {theme['primary_bg']} 0%, {theme['secondary_bg']} 100%) !important;
        color: {theme['primary_text']} !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Dashboard Header */
    .dashboard-header {{
        background: {theme['card_bg']} !important;
        padding: 1.5rem 2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px {theme['shadow']} !important;
        border: 1px solid {theme['border']} !important;
        margin-bottom: 2rem !important;
    }}
    
    /* Metrics Cards */
    .metric-dashboard-card {{
        background: {theme['card_bg']} !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border: 1px solid {theme['border']} !important;
        box-shadow: 0 2px 4px {theme['shadow']} !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
    }}
    
    .metric-dashboard-card:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px {theme['shadow']} !important;
    }}
    
    /* Job Cards */
    .job-card {{
        background: {theme['card_bg']} !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border: 1px solid {theme['border']} !important;
        box-shadow: 0 2px 4px {theme['shadow']} !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .job-card:hover {{
        border-color: {theme['accent']} !important;
        box-shadow: 0 4px 12px {theme['shadow']} !important;
    }}
    
    /* Candidate Cards */
    .candidate-card {{
        background: {theme['card_bg']} !important;
        padding: 1rem 1.5rem !important;
        border-radius: 8px !important;
        border: 1px solid {theme['border']} !important;
        margin-bottom: 0.5rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .candidate-card:hover {{
        background: {theme['secondary_bg']} !important;
        cursor: pointer !important;
    }}
    
    /* Score Indicators */
    .score-excellent {{
        color: {theme['success']} !important;
        background: {theme['success']}20 !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }}
    
    .score-good {{
        color: {theme['warning']} !important;
        background: {theme['warning']}20 !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }}
    
    .score-poor {{
        color: {theme['error']} !important;
        background: {theme['error']}20 !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }}
    
    /* Processing Status */
    .status-processing {{
        color: {theme['accent']} !important;
        background: {theme['accent']}20 !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        animation: pulse 2s infinite !important;
    }}
    
    .status-completed {{
        color: {theme['success']} !important;
        background: {theme['success']}20 !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
    }}
    
    /* Progress Bars */
    .progress-container {{
        background: {theme['border']} !important;
        border-radius: 10px !important;
        height: 8px !important;
        overflow: hidden !important;
    }}
    
    .progress-bar {{
        background: linear-gradient(90deg, {theme['accent']}, {theme['success']}) !important;
        height: 100% !important;
        border-radius: 10px !important;
        transition: width 0.5s ease !important;
    }}
    
    /* Sidebar Enhancement */
    .css-1d391kg {{
        background: {theme['card_bg']} !important;
        border-right: 1px solid {theme['border']} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {theme['accent']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        background: {theme['accent_hover']} !important;
        transform: translateY(-1px) !important;
    }}
    
    /* File Uploader */
    .stFileUploader {{
        background: {theme['card_bg']} !important;
        border: 2px dashed {theme['border']} !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }}
    
    /* Data Tables */
    .dataframe {{
        background: {theme['card_bg']} !important;
        color: {theme['primary_text']} !important;
        border-radius: 8px !important;
    }}
    
    /* Animations */
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease-in !important;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# Utility Functions
def generate_job_id(title: str, company: str) -> str:
    """Generate unique job ID"""
    return hashlib.md5(f"{title}_{company}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]

def extract_candidate_name_from_resume(resume_text: str) -> str:
    """Extract candidate name from resume text using simple heuristics"""
    lines = resume_text.split('\n')[:10]  # Check first 10 lines
    
    name_patterns = [
        r'^([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
        r'^([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)',  # First M. Last
        r'^([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)',  # First Middle Last
    ]
    
    for line in lines:
        line = line.strip()
        for pattern in name_patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1)
    
    return "Unknown Candidate"

def calculate_component_scores(analysis_data: Dict) -> Tuple[float, float, float]:
    """Calculate component scores from analysis data"""
    skills_score = 0.0
    experience_score = 0.0
    education_score = 0.0
    
    if 'sections' in analysis_data:
        for section in analysis_data['sections']:
            section_name = section.get('section_name', '').lower()
            score = section.get('score', 0) * 10  # Convert to 0-100 scale
            
            if 'skill' in section_name:
                skills_score = score
            elif 'experience' in section_name or 'work' in section_name:
                experience_score = score
            elif 'education' in section_name:
                education_score = score
    
    return skills_score, experience_score, education_score

def get_score_class(score: float) -> str:
    """Get CSS class for score display"""
    if score >= 75:
        return "score-excellent"
    elif score >= 50:
        return "score-good"
    else:
        return "score-poor"

def process_resume_batch(uploaded_files, job_description: str, ai_provider: str, 
                        api_key: str, model_name: str, job_id: str) -> List[ResumeEvaluation]:
    """Process a batch of resumes against a job description"""
    evaluations = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{total_files})")
            
            # Extract text from resume
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_text_from_docx(uploaded_file)
            else:
                resume_text = str(uploaded_file.read(), "utf-8")
            
            # Generate unique resume ID
            resume_id = hashlib.md5(f"{uploaded_file.name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
            
            # Extract candidate name
            candidate_name = extract_candidate_name_from_resume(resume_text)
            
            # Analyze resume with AI
            analysis_response = analyze_cv_with_ai(
                ai_provider, api_key, model_name, resume_text, job_description
            )
            
            parsed_analysis = parse_analysis_response(analysis_response)
            
            if parsed_analysis:
                overall_score = parsed_analysis.get('overall_score', 0)
                skills_score, experience_score, education_score = calculate_component_scores(parsed_analysis)
                feedback = json.dumps(parsed_analysis)  # Store full analysis
            else:
                overall_score = 0
                skills_score = experience_score = education_score = 0
                feedback = analysis_response  # Store raw response
            
            # Create evaluation record
            evaluation = ResumeEvaluation(
                resume_id=resume_id,
                job_id=job_id,
                candidate_name=candidate_name,
                overall_score=overall_score,
                skills_match=skills_score,
                experience_match=experience_score,
                education_match=education_score,
                feedback=feedback or "",
                processed_date=datetime.now(),
                file_name=uploaded_file.name
            )
            
            evaluations.append(evaluation)
            
            # Save to database
            db_manager.save_resume_evaluation(evaluation)
            
            # Update progress
            progress_bar.progress((i + 1) / total_files)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            continue
    
    status_text.text("Processing completed!")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    
    return evaluations