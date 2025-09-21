# Configuration Management for CV Ranking System
import os
import logging
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration management class"""
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "placement_system.db")
    
    # AI Provider Configuration
    DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "Gemini")
    
    # API Keys (should be set as environment variables)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    XAI_API_KEY = os.getenv("XAI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    
    # Application Settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_FILE_TYPES = ["pdf", "docx", "txt"]
    
    # Analysis Settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "3000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "cv_ranking.log")
    
    # Security Settings
    SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    
    @classmethod
    def get_api_key(cls, provider: str) -> str:
        """Get API key for specific provider"""
        key_mapping = {
            "Gemini": cls.GEMINI_API_KEY,
            "OpenAI": cls.OPENAI_API_KEY,
            "Anthropic (Claude)": cls.ANTHROPIC_API_KEY,
            "Cohere": cls.COHERE_API_KEY,
            "xAI (Grok)": cls.XAI_API_KEY,
            "Mistral AI": cls.MISTRAL_API_KEY,
            "Perplexity": cls.PERPLEXITY_API_KEY,
            "Together AI": cls.TOGETHER_API_KEY,
        }
        return key_mapping.get(provider, "")
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration settings"""
        validation_results = {
            "database_writable": cls._check_database_writable(),
            "log_directory_exists": cls._check_log_directory(),
            "file_size_valid": cls.MAX_FILE_SIZE_MB > 0,
            "temperature_valid": 0 <= cls.TEMPERATURE <= 2,
            "max_tokens_valid": cls.MAX_TOKENS > 0,
        }
        return validation_results
    
    @classmethod
    def _check_database_writable(cls) -> bool:
        """Check if database directory is writable"""
        try:
            db_path = Path(cls.DATABASE_PATH)
            db_dir = db_path.parent
            return db_dir.exists() and os.access(db_dir, os.W_OK)
        except Exception:
            return False
    
    @classmethod
    def _check_log_directory(cls) -> bool:
        """Check if log directory exists and is writable"""
        try:
            log_path = Path(cls.LOG_FILE)
            log_dir = log_path.parent
            if not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)
            return os.access(log_dir, os.W_OK)
        except Exception:
            return False

def setup_logging():
    """Setup logging configuration"""
    config = Config()
    
    # Create logs directory if it doesn't exist
    log_path = Path(config.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Create logger for the application
    logger = logging.getLogger('cv_ranking_system')
    logger.info("Logging system initialized")
    
    return logger

# Input validation functions
def validate_file_upload(uploaded_file) -> Dict[str, Any]:
    """Validate uploaded file"""
    config = Config()
    
    validation_result = {
        "valid": True,
        "errors": [],
        "file_info": {}
    }
    
    if uploaded_file is None:
        validation_result["valid"] = False
        validation_result["errors"].append("No file uploaded")
        return validation_result
    
    # Check file type
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in config.ALLOWED_FILE_TYPES:
        validation_result["valid"] = False
        validation_result["errors"].append(f"File type '{file_extension}' not allowed. Allowed types: {', '.join(config.ALLOWED_FILE_TYPES)}")
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > config.MAX_FILE_SIZE_MB:
        validation_result["valid"] = False
        validation_result["errors"].append(f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({config.MAX_FILE_SIZE_MB}MB)")
    
    # Store file info
    validation_result["file_info"] = {
        "name": uploaded_file.name,
        "size_mb": file_size_mb,
        "type": file_extension
    }
    
    return validation_result

def validate_job_description(job_description: str) -> Dict[str, Any]:
    """Validate job description"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not job_description or not job_description.strip():
        validation_result["valid"] = False
        validation_result["errors"].append("Job description cannot be empty")
        return validation_result
    
    # Check minimum length
    if len(job_description.strip()) < 50:
        validation_result["warnings"].append("Job description is quite short. Consider adding more details for better analysis.")
    
    # Check for key components
    key_components = ["skill", "experience", "requirement", "responsibility"]
    found_components = sum(1 for component in key_components if component in job_description.lower())
    
    if found_components < 2:
        validation_result["warnings"].append("Job description might be missing key components (skills, experience, requirements, responsibilities)")
    
    return validation_result

def validate_api_key(provider: str, api_key: str) -> Dict[str, Any]:
    """Validate API key format"""
    validation_result = {
        "valid": True,
        "errors": []
    }
    
    if not api_key or not api_key.strip():
        validation_result["valid"] = False
        validation_result["errors"].append(f"API key for {provider} cannot be empty")
        return validation_result
    
    # Basic format validation for different providers
    if provider == "Gemini" and not api_key.startswith("AI"):
        validation_result["errors"].append("Gemini API keys typically start with 'AI'")
    elif provider == "OpenAI" and not api_key.startswith("sk-"):
        validation_result["errors"].append("OpenAI API keys typically start with 'sk-'")
    elif provider == "Anthropic (Claude)" and not api_key.startswith("sk-ant-"):
        validation_result["errors"].append("Anthropic API keys typically start with 'sk-ant-'")
    
    # Check minimum length
    if len(api_key) < 20:
        validation_result["errors"].append("API key seems too short")
    
    if validation_result["errors"]:
        validation_result["valid"] = False
    
    return validation_result