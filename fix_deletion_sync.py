#!/usr/bin/env python3
"""
Fix for deletion synchronization not working properly.
This script adds registration for the deleted messages handler
and ensures the sync_deletions setting is properly enabled.
"""

import os
import json
import re

def load_file(filename):
    """Load the content of a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(filename, content):
    """Save content to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                env_vars[key] = value.strip("'\"")
    except Exception as e:
        print(f"Error loading .env file: {e}")
    return env_vars

def save_to_env(key, value):
    """Save a value to both environment variables and .env file"""
    os.environ[key] = value
    
    try:
        # Read the current .env file
        env_lines = []
        try:
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        except FileNotFoundError:
            # If .env doesn't exist, create an empty list
            env_lines = []
        
        # Check if the key already exists
        key_exists = False
        for i, line in enumerate(env_lines):
            if line.strip().startswith(f"{key}="):
                # Replace the existing line
                env_lines[i] = f"{key}='{value}'\n"
                key_exists = True
                break
        
        # If key doesn't exist, add it
        if not key_exists:
            env_lines.append(f"{key}='{value}'\n")
        
        # Write back to the .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        print(f"✅ Successfully updated {key} in .env file")
    except Exception as e:
        print(f"Error updating .env file: {e}")

def enable_sync_deletions():
    """Enable the sync_deletions flag in BOT_CONFIG"""
    env_vars = load_env()
    
    # Get current BOT_CONFIG
    bot_config = {}
    try:
        if 'BOT_CONFIG' in env_vars:
            bot_config = json.loads(env_vars['BOT_CONFIG'])
    except json.JSONDecodeError:
        print("Error: Invalid BOT_CONFIG format in .env file")
        bot_config = {}
    
    # Update sync_deletions flag
    bot_config['sync_deletions'] = True
    
    # Save updated config
    save_to_env('BOT_CONFIG', json.dumps(bot_config))
    print(f"Updated BOT_CONFIG: {json.dumps(bot_config)}")

def register_deletion_handler(content):
    """Add registration for the deletion message handler in standalone_bot.py"""
    # Find the section where we register edit message handler
    edit_handler_section = content.find("# Do the same for edited messages handler")
    if edit_handler_section == -1:
        print("Could not find edit handler registration section")
        return content
        
    # Find the end of the edit handler registration
    section_end = content.find("logger.info(f\"Re-registered handle_edited_message", edit_handler_section)
    if section_end == -1:
        print("Could not find end of edit handler registration section")
        return content
        
    # Find the end of that line
    line_end = content.find("\n", section_end)
    if line_end == -1:
        print("Could not find end of log line")
        return content
    
    # The code to add for registering deletion handler
    deletion_handler_code = """
                            # Register deletion message handler
                            for builder in builders:
                                if builder[1].__name__ == 'handle_deleted_message':
                                    try:
                                        bot.user_client.remove_event_handler(builder[1], builder[0])
                                        logger.info("Removed existing handle_deleted_message handler")
                                    except Exception as e:
                                        logger.error(f"Error removing handler: {e}")
                                        
                            # Register our deletion message handler
                            bot.user_client.add_event_handler(
                                bot.handle_deleted_message,
                                events.MessageDeleted(chats=source_channels)
                            )
                            logger.info(f"Re-registered handle_deleted_message for source channels: {source_channels}")"""
    
    # Insert the deletion handler registration after the edited message registration
    updated_content = content[:line_end+1] + deletion_handler_code + content[line_end+1:]
    
    return updated_content

def main():
    """Main function to execute the fix"""
    print("Fixing deletion synchronization issues...")
    
    # Enable sync_deletions flag
    print("\n1. Enabling sync_deletions flag in BOT_CONFIG...")
    enable_sync_deletions()
    
    # Register deletion handler
    print("\n2. Adding registration for deletion message handler...")
    standalone_bot_file = 'standalone_bot.py'
    content = load_file(standalone_bot_file)
    
    # Create backup
    backup_file = f"{standalone_bot_file}.bak.deletion"
    print(f"   Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Add deletion handler registration
    updated_content = register_deletion_handler(content)
    
    # Save the updated file
    if updated_content != content:
        print(f"   Saving updated {standalone_bot_file} with deletion handler registration...")
        save_file(standalone_bot_file, updated_content)
        print(f"   ✅ Successfully added deletion handler registration to {standalone_bot_file}")
    else:
        print(f"   No changes made to {standalone_bot_file}")
    
    print("\n✅ Fix complete! Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()