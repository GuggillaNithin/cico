import sys
from playwright.sync_api import sync_playwright
from config import Config
from logger import logger

def main():
    """
    Launches a visible browser allowing the user to manually log in.
    Once the user reaches the dashboard (valid session), the state is saved.
    """
    logger.info("Starting manual login setup...")
    print("\n" + "="*60)
    print("MANUAL LOGIN SETUP")
    print("A browser window will open.")
    print("Please manually log in using Google Sign-In and complete 2FA.")
    print("Do not close the browser! It will close automatically once the dashboard is detected.")
    print("="*60 + "\n")
    
    with sync_playwright() as p:
        # Launch headed browser so the user can interact
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        logger.info(f"Navigating to {Config.ATTENDANCE_URL}")
        page.goto(Config.ATTENDANCE_URL)
        
        logger.info("Waiting for you to complete manual login...")
        logger.info("Detecting dashboard elements (Attendance menu or Logout button)...")
        
        try:
            # Wait up to 5 minutes for the user to complete Google 2FA and get back to the app
            attendance_menu = page.locator("a:has-text('Attendance'), button:has-text('Attendance'), li:has-text('Attendance'), :has-text('Logout')").first
            attendance_menu.wait_for(state="visible", timeout=300000)
            
            logger.info("Dashboard detected! Login successful.")
            
            # Save the authenticated state
            logger.info(f"Saving authenticated session to {Config.STATE_FILE}...")
            context.storage_state(path=Config.STATE_FILE)
            logger.info("Session saved successfully!")
            
            print("\n" + "="*60)
            print("SUCCESS! Your session has been saved.")
            print("You can now run automated tasks using: python main.py --action clockin")
            print("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Failed to detect successful login within 5 minutes: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    main()
