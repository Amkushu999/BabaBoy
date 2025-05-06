#!/usr/bin/env python3
"""
Comprehensive fix for media edits causing reposts instead of updates.
This script implements a more robust solution for handling media edits.
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

def fix_message_mapping(content):
    """Fix the message mapping system to ensure it's properly tracking media messages"""
    # Find the add_message_mapping function
    mapping_regex = r"async def add_message_mapping\(source_channel_id, source_message_id, dest_channel, dest_msg_id\):.*?message_mapping\[key\]\[dest_channel\] = dest_msg_id\n"
    
    # Original implementation
    original_implementation = re.search(mapping_regex, content, re.DOTALL)
    if not original_implementation:
        print("Could not find add_message_mapping function")
        return content
    
    # Improved implementation with more debug logging
    improved_mapping = """async def add_message_mapping(source_channel_id, source_message_id, dest_channel, dest_msg_id):
    """Add a message mapping with limited storage (50 messages max)
    
    This function stores only the absolute minimum needed for edit synchronization
    while keeping a reasonably small memory footprint. Increased from 3 to 50
    to improve synchronization of recently edited messages.
    """
    key = (source_channel_id, source_message_id)
    
    # Check if mapping exists
    if key not in message_mapping:
        message_mapping[key] = {}
        # Add to order tracking
        message_mapping_order.append(key)
        logger.info(f"Added new mapping for source ({source_channel_id}, {source_message_id})")
        
        # If we've exceeded the message limit, remove oldest entries
        while len(message_mapping_order) > MAX_RECENT_MESSAGES:
            oldest_key = message_mapping_order.pop(0)  # Remove oldest entry
            logger.info(f"Removing oldest mapping: {oldest_key}")
            message_mapping.pop(oldest_key, None)
    
    # Add the mapping
    message_mapping[key][dest_channel] = dest_msg_id
    logger.info(f"Mapped {key} to channel {dest_channel}, message {dest_msg_id}")
    logger.info(f"Current mappings: {message_mapping}")
"""
    
    # Replace the original with the improved version
    updated_content = content.replace(original_implementation.group(0), improved_mapping)
    
    return updated_content

def fix_process_message_event(content):
    """Fix the process_message_event function to better handle media edits"""
    # Find the portion that handles media edits
    media_edits_section = r"""                        # Update the message in the destination channel
                        if msg_data\["has_media"\]:.*?# We'll continue below with the normal posting mechanism"""
    
    # Search for the section that needs to be replaced
    found_section = re.search(media_edits_section, content, re.DOTALL)
    if not found_section:
        print("Could not find media edits handling section")
        return content
    
    # Improved section for handling media edits
    improved_section = """                        # Update the message in the destination channel
                        if msg_data["has_media"]:
                            # For media messages, we need special handling for edits
                            logger.info(f"Media message edit detected. Attempting to handle properly.")
                            
                            # First try: Update just the caption if media hasn't changed
                            caption_update_successful = False
                            try:
                                # Only try to edit caption if the message actually has text
                                if "text" in msg_data and msg_data["text"]:
                                    # Try to edit just the caption
                                    await user_client.edit_message(
                                        entity=dest_channel,
                                        message=dest_msg_id, 
                                        text=msg_data["text"],
                                        parse_mode='html',
                                        link_preview=msg_data.get("link_preview", True)
                                    )
                                    logger.info(f"Successfully updated caption for media message {dest_msg_id}")
                                    caption_update_successful = True
                                    
                                    # Flag this destination as already handled
                                    sent_destinations[dest_channel] = dest_msg_id
                                else:
                                    logger.info(f"Media message has no caption to update")
                            except Exception as e:
                                logger.error(f"Error updating media caption: {e}")
                            
                            # If caption update failed, try delete and repost
                            if not caption_update_successful:
                                logger.info(f"Caption update failed or the media itself changed. Using delete-and-repost method.")
                                
                                # Only delete if we haven't already handled this destination
                                if dest_channel not in sent_destinations:
                                    try:
                                        # Try to delete the old message
                                        await user_client.delete_messages(dest_channel, dest_msg_id)
                                        logger.info(f"Deleted old media message {dest_msg_id} in {dest_channel}")
                                    except Exception as e:
                                        logger.error(f"Error deleting message {dest_msg_id}: {e}")
                                    
                                    # We'll continue to the reposting flow below since this destination
                                    # wasn't added to sent_destinations
                            else:
                                # Skip to next destination if caption update was successful
                                continue
"""
    
    # Replace the original with the improved version
    updated_content = re.sub(media_edits_section, improved_section, content, flags=re.DOTALL)
    
    return updated_content

def update_handle_edited_message(content):
    """Enhance the handle_edited_message function with better logging"""
    # Find the handle_edited_message function
    edit_handler_regex = r"async def handle_edited_message\(event\):.*?await process_message_event\(event, is_edit=True\)"
    
    found_handler = re.search(edit_handler_regex, content, re.DOTALL)
    if not found_handler:
        print("Could not find handle_edited_message function")
        return content
    
    # Enhanced edit handler with better logging
    enhanced_handler = """async def handle_edited_message(event):
    """Handle edited messages in source channels"""
    logger.info(f"=== EDIT EVENT RECEIVED ===")
    logger.info(f"From channel: {event.chat_id}")
    logger.info(f"Message ID: {event.message.id if hasattr(event, 'message') else 'Unknown'}")
    
    # Check if message has media
    has_media = False
    if hasattr(event, 'message') and hasattr(event.message, 'media'):
        has_media = event.message.media is not None
        logger.info(f"Edit contains media: {has_media}")
    
    await process_message_event(event, is_edit=True)"""
    
    # Replace the original with the enhanced version
    updated_content = content.replace(found_handler.group(0), enhanced_handler)
    
    return updated_content

def main():
    """Main function to execute the comprehensive fix"""
    print("Applying comprehensive fix for media edit handling...")
    
    # Fix bot.py
    bot_file = 'bot.py'
    print(f"\n1. Enhancing {bot_file} with comprehensive media edit fixes...")
    
    content = load_file(bot_file)
    
    # Create backup
    backup_file = f"{bot_file}.bak.media_edit_comprehensive"
    print(f"   Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Apply all fixes
    updated_content = fix_message_mapping(content)
    updated_content = fix_process_message_event(updated_content)
    updated_content = update_handle_edited_message(updated_content)
    
    # Save the updated file
    if updated_content != content:
        print(f"   Saving updated {bot_file} with comprehensive media edit improvements...")
        save_file(bot_file, updated_content)
        print(f"   ✅ Successfully enhanced media edit handling in {bot_file}")
    else:
        print(f"   ⚠️ No changes made to {bot_file}. Patterns might not have been found.")
    
    print("\n✅ Fix complete! Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()