import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
import mimetypes
from config import Config
from logger import logger

def send_failure_email(action_attempted: str, error_message: str, traceback_str: str, screenshot_path: str = None) -> None:
    """
    Sends an email notification on failure with traceback and screenshot.
    
    Args:
        action_attempted: What the bot was trying to do (e.g., 'Clock In').
        error_message: The main exception message.
        traceback_str: Full traceback string.
        screenshot_path: Path to the latest screenshot, if available.
    """
    logger.info("Preparing failure notification email...")
    
    msg = EmailMessage()
    msg['Subject'] = f"❌ Attendance Bot Failure: {action_attempted}"
    msg['From'] = Config.SMTP_USERNAME
    msg['To'] = Config.ALERT_EMAIL_RECIPIENT
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    body = f"""
    Attendance Bot Automation Failed.
    
    Action Attempted: {action_attempted}
    Timestamp: {timestamp}
    
    Error Message:
    {error_message}
    
    Traceback:
    {traceback_str}
    """
    msg.set_content(body)
    
    # Attach log file
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(Config.LOG_DIR, f"attendance_bot_{date_str}.log")
    
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'rb') as f:
                log_data = f.read()
            msg.add_attachment(log_data, maintype='text', subtype='plain', filename=f"bot_log_{date_str}.txt")
        except Exception as e:
            logger.error(f"Failed to attach log file: {e}")

    # Attach screenshot if provided
    if screenshot_path and os.path.exists(screenshot_path):
        try:
            mime_type, _ = mimetypes.guess_type(screenshot_path)
            mime_type = mime_type or 'application/octet-stream'
            maintype, subtype = mime_type.split('/', 1)
            
            with open(screenshot_path, 'rb') as f:
                img_data = f.read()
            filename = os.path.basename(screenshot_path)
            msg.add_attachment(img_data, maintype=maintype, subtype=subtype, filename=filename)
        except Exception as e:
            logger.error(f"Failed to attach screenshot: {e}")

    # Send the email
    try:
        # Assuming SSL for standard port 465, or TLS for 587
        if Config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT)
        else:
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Failure notification email sent successfully to {Config.ALERT_EMAIL_RECIPIENT}.")
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
