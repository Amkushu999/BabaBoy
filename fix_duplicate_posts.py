#!/usr/bin/env python3
"""
Fix for duplicate posts being sent to destination channels.
This script implements a message deduplication mechanism to prevent
the same message from being posted multiple times.
"""

import os
import re

def load_file(filename):
    """Load the content of a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(filename, content):
    """Save content to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def add_recent_message_tracking(content):
    """Add a recently processed message tracking system to prevent duplicates"""
    
    # Add the message deduplication variables at the top of the file
    recent_messages_code = """
# Add message deduplication to prevent multiple reposts of the same message
# Store recently processed messages with timestamps to prevent duplicates
recent_messages = {}
# How long to keep messages in the deduplication cache (in seconds)
MESSAGE_DEDUP_TIME = 60  # 1 minute
"""
    
    # Find where to add the global variables - after sync_deletions
    first_part = content.split("sync_deletions = BOT_CONFIG.get(\"sync_deletions\", False)", 1)
    if len(first_part) != 2:
        print("Could not find proper position to insert global variables")
        return content
    
    updated_content = first_part[0] + "sync_deletions = BOT_CONFIG.get(\"sync_deletions\", False)" + recent_messages_code + first_part[1]
    
    # Now add the deduplication check in process_message_event function
    process_start = updated_content.find("async def process_message_event(event, is_edit=False):")
    if process_start == -1:
        print("Could not find process_message_event function")
        return updated_content
    
    # Find the position where source_message_id is set
    source_id_section = updated_content.find("source_message_id = event.message.id", process_start)
    if source_id_section == -1:
        print("Could not find position to add deduplication check")
        return updated_content
    
    # Find the end of that line
    line_end = updated_content.find("\n", source_id_section)
    if line_end == -1:
        print("Could not find end of source_message_id line")
        return updated_content
    
    # The deduplication check code to add
    dedup_check_code = """
        # Check for duplicate messages
        if not is_edit and source_channel_id and source_message_id:
            message_key = f"{source_channel_id}:{source_message_id}"
            current_time = asyncio.get_event_loop().time()
            
            # Check if we've seen this message recently
            if message_key in recent_messages:
                last_time = recent_messages[message_key]
                time_diff = current_time - last_time
                # If we've seen this message in the last minute, ignore it
                if time_diff < MESSAGE_DEDUP_TIME:
                    logger.warning(f"DUPLICATE MESSAGE DETECTED: {message_key} - ignoring (processed {time_diff:.2f} seconds ago)")
                    return
            
            # Update the time we last saw this message
            recent_messages[message_key] = current_time
            
            # Clean up old messages from the deduplication cache
            old_keys = [k for k, t in recent_messages.items() if current_time - t > MESSAGE_DEDUP_TIME]
            for k in old_keys:
                del recent_messages[k]"""
    
    # Insert the deduplication check after setting source_message_id
    updated_content = updated_content[:line_end+1] + dedup_check_code + updated_content[line_end+1:]
    
    return updated_content

def main():
    """Main function to execute the fix"""
    bot_file = 'bot.py'
    
    print(f"Reading {bot_file}...")
    content = load_file(bot_file)
    
    # Create backup
    backup_file = f"{bot_file}.bak.duplicate"
    print(f"Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Add message deduplication
    print("Adding message deduplication to prevent multiple reposts...")
    updated_content = add_recent_message_tracking(content)
    
    # Save the updated file
    print(f"Saving updated file with message deduplication...")
    save_file(bot_file, updated_content)
    
    print(f"✅ Successfully added message deduplication to {bot_file}")
    print("Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()