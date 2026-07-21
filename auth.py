import os
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config
from logger import logger
from utils import SessionExpiredError, take_screenshot

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True
)
def verify_session(page: Page) -> None:
    """
    Checks if the loaded storage_state.json provides a valid authenticated session.
    It navigates to the application and looks for dashboard elements.
    If the session is invalid or missing, it raises SessionExpiredError.
    
    Args:
        page: Playwright Page object (already loaded with context state).
        
    Raises:
        SessionExpiredError: If the dashboard cannot be reached.
    """
    logger.info("Checking session validity...")
    
    if not os.path.exists(Config.STATE_FILE):
        raise SessionExpiredError("storage_state.json not found.")
        
    try:
        logger.info(f"Navigating to {Config.ATTENDANCE_URL} to verify session...")
        page.goto(Config.ATTENDANCE_URL, wait_until="networkidle", timeout=30000)
        
        # Give it a moment to see if it auto-redirects from /login to dashboard
        try:
            page.wait_for_url("**/login", timeout=5000)
        except PlaywrightTimeoutError:
            pass
            
        logger.info("Detecting dashboard elements (Attendance menu or Logout button)...")
        # Check if we see attendance menus or logout which indicates we are logged in
        dashboard_elements = page.locator("a:has-text('Attendance'), button:has-text('Attendance'), li:has-text('Attendance'), :has-text('Logout')")
        
        if dashboard_elements.count() > 0:
            # Wait for at least one element to be explicitly visible
            dashboard_elements.first.wait_for(state="visible", timeout=10000)
            logger.info("Session valid. Dashboard detected.")
            return
        else:
            logger.error("Dashboard elements not found. Session appears invalid or expired.")
            take_screenshot(page, "session_expired")
            raise SessionExpiredError("Saved Google session has expired or is invalid.")
            
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout while verifying session: {e}")
        take_screenshot(page, "session_timeout")
        raise SessionExpiredError(f"Session verification timed out: {e}") from e
    except SessionExpiredError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during session verification: {e}")
        take_screenshot(page, "session_verification_error")
        raise SessionExpiredError(f"Unexpected error verifying session: {str(e)}") from e
