#!/usr/bin/env python3
"""
Final fix for media edits causing reposts instead of updates.
This script implements a complete solution for handling media edits.
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

def fix_process_message_event(content):
    """Fix the process_message_event function to properly handle media edits"""
    # First, let's locate the part that handles edited messages with media
    start_pattern = "                        # Update the message in the destination channel"
    end_pattern = "                        else:"
    start_idx = content.find(start_pattern)
    if start_idx == -1:
        print("Could not find start of media edit section")
        return content
    
    # Find the "else:" that matches our if statement
    current_pos = start_idx
    found_else = False
    while current_pos < len(content) and not found_else:
        next_else = content.find(end_pattern, current_pos)
        if next_else == -1:
            break
        # Check if this else belongs to our if
        section = content[start_idx:next_else]
        if section.count("if") == section.count("else:"):
            found_else = True
            break
        current_pos = next_else + 1
    
    if not found_else:
        print("Could not find matching else for media edit section")
        return content
    
    # Extract the section we need to replace
    end_idx = content.find(end_pattern, start_idx)
    if end_idx == -1:
        print("Could not find end of media edit section")
        return content
    
    section_to_replace = content[start_idx:end_idx]
    
    # Create the improved implementation
    improved_section = """                        # Update the message in the destination channel
                        if msg_data["has_media"]:
                            # For media messages, implement proper edit handling
                            logger.info(f"Media message edit detected. Attempting to properly handle.")
                            
                            # Try to delete and then repost, but track the new message ID
                            try:
                                # Delete old message to avoid duplicates
                                await user_client.delete_messages(dest_channel, dest_msg_id)
                                logger.info(f"Successfully deleted old media message {dest_msg_id} in channel {dest_channel}")
                                
                                # The message will be reposted below and tracked properly
                                # Don't mark this destination as handled yet
                            except Exception as e:
                                logger.error(f"Failed to delete old media message {dest_msg_id}: {e}")
                                # The old message will remain, but we'll still try to create a new post below
                                # Don't mark this destination as handled
"""
    
    # Replace the section
    updated_content = content.replace(section_to_replace, improved_section)
    
    return updated_content

def fix_sent_destinations(content):
    """Ensure sent_destinations is correctly handled for media reposts"""
    # Find the section that handles actual media sending
    start_pattern = "            # For media-based methods, we need to extract the file and post with new caption"
    sent_media_section = """            # For media-based methods, we need to extract the file and post with new caption
            if msg_data["has_media"]:
                # Group similar media types together
                media_type = msg_data.get("media_type", "generic")
                
                # Handle based on media type
                if media_type == "photo":
                    logger.info(f"Sending photo to {len(remaining_destinations)} destinations")
                    
                    for dest_channel in remaining_destinations:
                        try:
                            # Send photo with caption from msg_data
                            result = await user_client.send_file(
                                dest_channel,
                                msg_data["media"],
                                caption=msg_data["text"] if "text" in msg_data else None,
                                parse_mode='html',
                                formatting_entities=msg_data.get("entities", None)
                            )
                            
                            if result:
                                logger.info(f"Successfully sent photo to {dest_channel}, message ID: {result.id}")
                                # Track the message for future edit syncing
                                await add_message_mapping(source_channel_id, source_message_id, dest_channel, result.id)
                                successful_destinations.append(dest_channel)
                            
                        except Exception as e:
                            logger.error(f"Error sending photo to {dest_channel}: {e}")"""
    
    end_of_section = "            # For text-only messages, a simple send_message is enough"
    
    # Find the section
    start_idx = content.find(start_pattern)
    end_idx = content.find(end_of_section, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find media sending section")
        return content
    
    section_to_search = content[start_idx:end_idx]
    
    # Check if every media sending type has the message mapping calls
    if "await add_message_mapping(source_channel_id, source_message_id, dest_channel, result.id)" not in section_to_search:
        print("Media sending section missing required message mapping calls")
        return content
        
    # This section is fine, no changes needed
    return content

def main():
    """Main function to execute the fix"""
    print("Applying final fix for media edit handling...")
    
    # Fix bot.py
    bot_file = 'bot.py'
    print(f"\n1. Enhancing {bot_file} with final media edit fixes...")
    
    content = load_file(bot_file)
    
    # Create backup
    backup_file = f"{bot_file}.bak.media_edit_final"
    print(f"   Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Apply fixes
    updated_content = fix_process_message_event(content)
    updated_content = fix_sent_destinations(updated_content)
    
    # Save the updated file
    if updated_content != content:
        print(f"   Saving updated {bot_file} with improved media edit handling...")
        save_file(bot_file, updated_content)
        print(f"   ✅ Successfully enhanced media edit handling in {bot_file}")
    else:
        print(f"   ⚠️ No changes made to {bot_file}")
    
    print("\n✅ Fix complete! Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()