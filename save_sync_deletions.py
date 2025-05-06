#!/usr/bin/env python3
"""
Script to directly set the sync_deletions flag in the .env file
"""
import os
import json
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file"""
    load_dotenv()

def save_to_env(key, value):
    """Save a value to both environment variables and .env file"""
    os.environ[key] = value
    
    try:
        # Read the current .env file
        env_lines = []
        try:
            with open(".env", "r") as f:
                env_lines = f.readlines()
        except FileNotFoundError:
            # Create new .env file if it doesn't exist
            env_lines = []
        
        # Check if the key already exists
        key_exists = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key}="):
                # Update the existing line
                env_lines[i] = f"{key}='{value}'\n"
                key_exists = True
                break
        
        # If the key doesn't exist, add it
        if not key_exists:
            env_lines.append(f"{key}='{value}'\n")
        
        # Write back to .env
        with open(".env", "w") as f:
            f.writelines(env_lines)
        
        print(f"✅ Successfully updated {key} in .env file")
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        print(f"Environment variable {key} updated in memory only")

def enforce_sync_deletions():
    """Enforce sync_deletions=true in BOT_CONFIG"""
    # Load environment variables
    load_env()
    
    # Get current BOT_CONFIG
    bot_config_str = os.environ.get("BOT_CONFIG", "{}")
    try:
        bot_config = json.loads(bot_config_str)
    except json.JSONDecodeError:
        print("Invalid BOT_CONFIG JSON, creating new config")
        bot_config = {}
    
    # Check if sync_deletions is already enabled
    current_value = bot_config.get("sync_deletions", False)
    if current_value:
        print("sync_deletions is already enabled in BOT_CONFIG")
        return
    
    # Enable sync_deletions
    bot_config["sync_deletions"] = True
    
    # Save updated config
    new_config_str = json.dumps(bot_config)
    save_to_env("BOT_CONFIG", new_config_str)
    
    print(f"Updated BOT_CONFIG: {new_config_str}")

def main():
    """Main function to execute the script"""
    print("Enforcing sync_deletions=true in BOT_CONFIG...")
    enforce_sync_deletions()
    print("Done! Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()