import os
import sys
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file if it exists
load_dotenv()

def get_env_variable(var_name: str, required: bool = True, default: str = "") -> str:
    """
    Retrieve an environment variable.
    
    Args:
        var_name: The name of the environment variable.
        required: Whether the variable is mandatory.
        default: Default value if not required and not set.
        
    Returns:
        The value of the environment variable.
        
    Raises:
        ValueError: If a required variable is missing.
    """
    value = os.getenv(var_name, default)
    if required and not value:
        print(f"CRITICAL ERROR: Required environment variable '{var_name}' is missing.", file=sys.stderr)
        sys.exit(1)
    return value

class Config:
    """Centralized configuration management."""
    
    # URL Configuration
    ATTENDANCE_URL = get_env_variable("ATTENDANCE_URL", required=True)
    
    # Authentication (Google Sign-In)
    GOOGLE_EMAIL = get_env_variable("GOOGLE_EMAIL", required=True)
    GOOGLE_PASSWORD = get_env_variable("GOOGLE_PASSWORD", required=True)
    
    # Email Notification Settings
    SMTP_SERVER = get_env_variable("SMTP_SERVER", required=True)
    SMTP_PORT = int(get_env_variable("SMTP_PORT", required=False, default="465"))
    SMTP_USERNAME = get_env_variable("SMTP_USERNAME", required=True)
    SMTP_PASSWORD = get_env_variable("SMTP_PASSWORD", required=True)
    ALERT_EMAIL_RECIPIENT = get_env_variable("ALERT_EMAIL_RECIPIENT", required=True)

    # Directories and Files
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
    STATE_FILE = os.path.join(BASE_DIR, "storage_state.json")

# Ensure required directories exist
os.makedirs(Config.LOG_DIR, exist_ok=True)
os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
