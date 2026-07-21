import argparse
import sys
import traceback
import os
from playwright.sync_api import sync_playwright
from config import Config
from logger import logger
from auth import verify_session
from attendance import navigate_to_attendance, perform_attendance_action
from email_service import send_failure_email
from utils import AttendanceAutomationError, SessionExpiredError, take_screenshot

def main():
    """
    Main entry point for the Attendance Bot.
    """
    parser = argparse.ArgumentParser(description="Automate attendance actions.")
    parser.add_argument(
        "--action", 
        choices=["clockin", "clockout"], 
        required=True, 
        help="Action to perform: clockin or clockout"
    )
    args = parser.parse_args()
    
    action = args.action
    logger.info(f"Starting Attendance Bot for action: {action.upper()}")
    
    # We will use this to store the path of the latest screenshot in case of failure
    latest_screenshot = None
    
    if not os.path.exists(Config.STATE_FILE):
        logger.error(f"{Config.STATE_FILE} not found. You must run setup_login.py first.")
        error_msg = "Saved Google session has expired or is missing.\n\nPlease run:\npython setup_login.py\nto create a new authenticated session."
        send_failure_email(action, error_msg, "", None)
        sys.exit(1)
        
    try:
        with sync_playwright() as p:
            logger.info("Opening Browser...")
            # Run headless=True for GitHub Actions, headless=False for local debugging if desired
            browser = p.chromium.launch(headless=True)
            
            context_args = {
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # Load session state if it exists
            if os.path.exists(Config.STATE_FILE):
                logger.info(f"Loading persistent session from {Config.STATE_FILE}")
                context_args['storage_state'] = Config.STATE_FILE
                
            context = browser.new_context(**context_args)
            page = context.new_page()
            
            try:
                # 1. Verify Session
                verify_session(page)
                
                # 2. Navigate to Attendance Page
                navigate_to_attendance(page)
                
                # 3. Perform Action (Clock In / Clock Out)
                perform_attendance_action(page, action)
                
            except Exception as e:
                logger.error("An error occurred during the automation flow.")
                # Capture a final screenshot if something unexpected happened 
                # (although child functions also capture on their specific failures)
                latest_screenshot = take_screenshot(page, "fatal_error")
                raise e
            finally:
                logger.info("Closing Browser...")
                browser.close()
                
        logger.info(f"Attendance action '{action}' completed successfully. Exiting cleanly.")
        sys.exit(0)

    except SessionExpiredError as e:
        error_msg = "Saved Google session has expired.\n\nPlease run:\npython setup_login.py\nto create a new authenticated session."
        tb_str = traceback.format_exc()
        logger.error(f"Session Expired: {str(e)}")
        logger.debug(tb_str)
        send_failure_email(action, error_msg, tb_str, latest_screenshot)
        sys.exit(1)
        
    except AttendanceAutomationError as e:
        # Handled custom exceptions
        error_msg = str(e)
        tb_str = traceback.format_exc()
        logger.error(f"Automation failed: {error_msg}")
        logger.debug(tb_str)
        send_failure_email(action, error_msg, tb_str, latest_screenshot)
        sys.exit(1)
        
    except Exception as e:
        # Unexpected exceptions
        error_msg = f"Unexpected error: {str(e)}"
        tb_str = traceback.format_exc()
        logger.critical(error_msg)
        logger.debug(tb_str)
        send_failure_email(action, error_msg, tb_str, latest_screenshot)
        sys.exit(1)

if __name__ == "__main__":
    main()
