import os
from datetime import datetime
from config import Config
from playwright.sync_api import Page
from logger import logger

class AttendanceAutomationError(Exception):
    """Base exception for all attendance automation errors."""
    pass

class LoginFailedError(AttendanceAutomationError):
    """Raised when login fails."""
    pass

class SessionExpiredError(AttendanceAutomationError):
    """Raised when the saved session has expired or is invalid."""
    pass

class ElementNotFoundError(AttendanceAutomationError):
    """Raised when a required element cannot be found."""
    pass

class VerificationFailedError(AttendanceAutomationError):
    """Raised when verifying the success of an action fails."""
    pass

def take_screenshot(page: Page, action_name: str) -> str:
    """
    Takes a full-page screenshot and saves it to the screenshots directory.
    
    Args:
        page: Playwright Page object.
        action_name: Descriptor for the filename (e.g., 'before_login', 'after_clockin').
        
    Returns:
        str: The absolute path to the saved screenshot file, or empty string if failed.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{action_name}.png"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        
        page.screenshot(path=filepath, full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to capture screenshot '{action_name}': {e}")
        return ""
