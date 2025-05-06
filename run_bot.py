#!/usr/bin/env python3
"""
Persistent run script for the Telegram bot
"""
import os
import time
import signal
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Track the bot process
bot_process = None

def signal_handler(sig, frame):
    """Handle interrupt signals"""
    logger.info("Received signal to terminate, shutting down...")
    if bot_process:
        logger.info(f"Terminating bot process {bot_process.pid}")
        bot_process.terminate()
    sys.exit(0)

def run_bot():
    """Run the bot with automatic restart on failure"""
    global bot_process
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Telegram bot runner")
    
    retry_count = 0
    max_retries = 10
    
    while retry_count < max_retries:
        try:
            logger.info("Attempting to start the bot process...")
            
            # Run the bot process
            bot_process = subprocess.Popen(
                ["python", "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            logger.info(f"Bot started with PID {bot_process.pid}")
            
            # Monitor the process
            while bot_process.poll() is None:
                # Process is still running
                line = bot_process.stdout.readline()
                if line:
                    logger.info(f"BOT: {line.strip()}")
                time.sleep(0.1)
            
            # If we got here, the process has ended
            exit_code = bot_process.returncode
            logger.warning(f"Bot process exited with code {exit_code}")
            
            # Increment retry count
            retry_count += 1
            
            # Wait before retrying
            logger.info(f"Waiting 5 seconds before retry {retry_count}/{max_retries}...")
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            retry_count += 1
            time.sleep(5)
    
    logger.error(f"Bot failed to start after {max_retries} attempts, giving up.")

if __name__ == "__main__":
    run_bot()