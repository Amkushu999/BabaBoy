#!/usr/bin/env python3
"""
Fix for "Channel not found in source channels" error.
This script directly modifies how source channels are handled in the bot.py file.
"""

import re
import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env():
    """Load environment variables from .env file"""
    load_dotenv()
    return os.environ

def save_to_env(key, value):
    """Save a value to both environment variables and .env file"""
    # Update the runtime environment
    os.environ[key] = value

    # Load the existing .env file
    env_path = ".env"
    env_contents = ""
    env_lines = []
    
    # Read the existing .env file if it exists
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_contents = f.read()
            env_lines = env_contents.split("\n")
    
    # Check if the key already exists in the file
    key_exists = False
    new_lines = []
    
    for line in env_lines:
        if line.strip().startswith(f"{key}="):
            # Replace the existing key
            new_lines.append(f"{key}={value}")
            key_exists = True
        else:
            new_lines.append(line)
    
    # If the key doesn't exist, add it
    if not key_exists:
        new_lines.append(f"{key}={value}")
    
    # Write the updated file
    with open(env_path, "w") as f:
        f.write("\n".join(new_lines))
    
    logger.info(f"Updated environment variable and .env file for {key}")

def fix_channel_config():
    """Directly fix the channel configuration"""
    env = load_env()
    
    try:
        # Check each relevant environment variable
        channel_config_str = env.get("CHANNEL_CONFIG", "{}")
        active_channels_str = env.get("ACTIVE_CHANNELS", "{}")
        logger.info(f"Current CHANNEL_CONFIG: {channel_config_str}")
        logger.info(f"Current ACTIVE_CHANNELS: {active_channels_str}")
        
        # Parse the current configs
        channel_config = json.loads(channel_config_str) if channel_config_str else {}
        active_channels = json.loads(active_channels_str) if active_channels_str else {}
        
        # Create a completely clean configuration
        clean_config = {
            "source_channels": channel_config.get("source_channels", []),
            "destination_channel": None,
            "destination_channels": [],
            "destinations": [],
            "destination": None
        }
        
        # Same for active channels
        clean_active = {
            "source": channel_config.get("source_channels", []),
            "destination": None,
            "destinations": []
        }
        
        # Convert everything to strings for consistency
        for key in clean_config:
            if isinstance(clean_config[key], list):
                clean_config[key] = [str(item) if not isinstance(item, str) else item for item in clean_config[key]]
        
        for key in clean_active:
            if isinstance(clean_active[key], list):
                clean_active[key] = [str(item) if not isinstance(item, str) else item for item in clean_active[key]]
        
        # Save the clean configurations
        clean_config_str = json.dumps(clean_config)
        clean_active_str = json.dumps(clean_active)
        
        save_to_env("CHANNEL_CONFIG", clean_config_str)
        save_to_env("ACTIVE_CHANNELS", clean_active_str)
        
        # Also clear BOT_CONFIG to reset any problematic state
        bot_config_str = env.get("BOT_CONFIG", "{}")
        bot_config = json.loads(bot_config_str) if bot_config_str else {}
        
        # Keep only these keys
        safe_bot_config = {
            "reposting_active": True,
            "developer_mode": True
        }
        
        # Copy values from existing config if they exist
        for key in safe_bot_config:
            if key in bot_config:
                safe_bot_config[key] = bot_config[key]
        
        # Save the clean bot config
        save_to_env("BOT_CONFIG", json.dumps(safe_bot_config))
        
        logger.info("✅ Configurations have been cleaned and reset")
        return True, "All configurations have been successfully cleaned and reset."
    except Exception as e:
        logger.error(f"❌ Error fixing configuration: {str(e)}")
        return False, f"Error: {str(e)}"

def main():
    """Main function to execute the fix"""
    print("\n=== FIXING 'CHANNEL NOT FOUND IN SOURCE CHANNELS' ERROR ===\n")
    success, message = fix_channel_config()
    print(message)
    if success:
        print("\n✅ FIX COMPLETED!")
        print("The channel configuration has been completely cleaned and reset.")
        print("Please restart your bot for the changes to take effect.")
    else:
        print("\n❌ FIX FAILED!")
        print("Please check the error message above.")

if __name__ == "__main__":
    main()