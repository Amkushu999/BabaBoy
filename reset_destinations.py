#!/usr/bin/env python3
"""
Direct script to completely reset all destination channels in the bot configuration.
This script bypasses the normal bot UI and directly modifies the configuration.
"""

import os
import logging
import json
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

def reset_destinations():
    """Reset all destination channels to an empty list"""
    env = load_env()
    
    # Save current state for logging
    current_channel_config = env.get("CHANNEL_CONFIG", "{}")
    logger.info(f"Current CHANNEL_CONFIG: {current_channel_config}")
    
    try:
        # Parse the current config
        channel_config = json.loads(current_channel_config)
        
        # Handle both old and new configuration formats
        previous_destinations = channel_config.get("destinations", [])
        previous_destination = channel_config.get("destination")
        
        # Also check legacy format keys
        legacy_destinations = channel_config.get("destination_channels", [])
        legacy_destination = channel_config.get("destination_channel")
        
        logger.info(f"Previous destinations (new format): {previous_destinations}")
        logger.info(f"Previous primary destination (new format): {previous_destination}")
        logger.info(f"Previous destinations (legacy format): {legacy_destinations}")
        logger.info(f"Previous primary destination (legacy format): {legacy_destination}")
        
        # Reset all destination-related fields in both formats
        # New format
        channel_config["destinations"] = []
        channel_config["destination"] = None
        
        # Legacy format
        channel_config["destination_channels"] = []
        channel_config["destination_channel"] = None
        
        # Save the updated config
        updated_config = json.dumps(channel_config)
        save_to_env("CHANNEL_CONFIG", updated_config)
        
        logger.info("✅ All destinations have been reset")
        logger.info(f"Updated CHANNEL_CONFIG: {updated_config}")
        
        # Also check and update ACTIVE_CHANNELS if it exists
        active_channels_json = env.get("ACTIVE_CHANNELS", "{}")
        if active_channels_json:
            try:
                logger.info(f"Found ACTIVE_CHANNELS: {active_channels_json}")
                active_channels = json.loads(active_channels_json)
                
                # Reset destinations in active channels
                active_channels["destinations"] = []
                active_channels["destination"] = None
                
                # Save updated active channels
                updated_active_channels = json.dumps(active_channels)
                save_to_env("ACTIVE_CHANNELS", updated_active_channels)
                logger.info("✅ ACTIVE_CHANNELS have been reset")
                logger.info(f"Updated ACTIVE_CHANNELS: {updated_active_channels}")
            except Exception as e:
                logger.warning(f"Could not update ACTIVE_CHANNELS: {str(e)}")
        
        return True, "All destination channels have been successfully reset."
    except Exception as e:
        logger.error(f"❌ Error resetting destinations: {str(e)}")
        return False, f"Error: {str(e)}"

def main():
    """Main function to execute the reset"""
    print("Starting destination reset...")
    success, message = reset_destinations()
    print(message)
    if success:
        print("\n✅ DESTINATION RESET COMPLETE!")
        print("All destination channels have been removed from your configuration.")
        print("Please restart your bot for the changes to take effect.")
    else:
        print("\n❌ DESTINATION RESET FAILED!")
        print("Please check the error message above.")

if __name__ == "__main__":
    main()