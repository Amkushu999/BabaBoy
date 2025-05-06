#!/usr/bin/env python3
"""
Health check and automatic restart for the Telegram bot
"""
import os
import subprocess
import time
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("healthcheck.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_bot_running():
    """Check if the bot process is running"""
    try:
        # Look for Python processes running main.py
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Check if main.py is in the output
        return "python main.py" in result.stdout
    except Exception as e:
        logger.error(f"Error checking bot status: {str(e)}")
        return False

def start_bot():
    """Start the bot if it's not running"""
    try:
        # First try to kill any zombie processes
        subprocess.run(["python", "kill_bots.py"], check=True)
        logger.info("Killed any existing bot processes")
        
        # Start the bot in background
        subprocess.Popen(
            ["nohup", "python", "main.py", ">", "bot.log", "2>&1", "&"],
            shell=True
        )
        
        logger.info("Bot started")
        return True
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        return False

def health_check():
    """Run a health check and restart the bot if needed"""
    logger.info("Running health check...")
    
    if not is_bot_running():
        logger.warning("Bot is not running, restarting...")
        start_bot()
    else:
        logger.info("Bot is running")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Just run a single health check
        health_check()
    else:
        # Run continuous monitoring
        logger.info("Starting continuous health check monitoring")
        
        try:
            while True:
                health_check()
                # Wait 5 minutes before next check
                time.sleep(300)
        except KeyboardInterrupt:
            logger.info("Health check monitoring stopped by user")