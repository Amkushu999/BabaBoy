#!/usr/bin/env python3
"""
Advanced fix for media edits causing reposts instead of updates.
This script implements a more comprehensive solution for handling media edits.
"""

import os
import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_file(filename):
    """Load the content of a file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(filename, content):
    """Save content to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def enhance_handle_edited_message(content):
    """Enhance the handle_edited_message function with better logging"""
    # Find the handle_edited_message function
    edit_handler_pattern = r"async def handle_edited_message\(event\):\s+\"\"\"Handle edited messages in source channels\"\"\"\s+await process_message_event\(event, is_edit=True\)"
    
    # Create improved handler with detailed logging
    improved_handler = """async def handle_edited_message(event):
    """Handle edited messages in source channels"""
    logger.info(f"=== EDIT EVENT RECEIVED ===")
    logger.info(f"From channel: {event.chat_id}")
    logger.info(f"Message ID: {event.message.id if hasattr(event, 'message') else 'Unknown'}")
    
    # Check if message has media
    has_media = False
    if hasattr(event, 'message') and hasattr(event.message, 'media'):
        has_media = event.message.media is not None
        logger.info(f"Edit contains media: {has_media}")
        
        # Log media type for debugging
        if has_media:
            media_type = "unknown"
            if hasattr(event.message.media, 'photo'):
                media_type = "photo"
            elif hasattr(event.message.media, 'document'):
                media_type = "document"
            elif hasattr(event.message.media, 'video'):
                media_type = "video"
            logger.info(f"Media type: {media_type}")
    
    await process_message_event(event, is_edit=True)"""
    
    # Replace the original with enhanced version
    updated_content = re.sub(edit_handler_pattern, improved_handler, content)
    
    return updated_content

def fix_media_edit_handling(content):
    """Fix the media edit handling section"""
    # Find the media section in process_message_event
    media_edit_pattern = r"if msg_data\[\"has_media\"\]:\s+# For media edits.*?# Let the regular flow below handle reposting the updated media"
    
    # Create an improved implementation
    improved_media_section = """if msg_data["has_media"]:
                            # For media edits, we need to handle carefully to avoid duplicates
                            logger.info(f"Media message edit detected in channel {dest_channel}, message {dest_msg_id}")
                            
                            # IMPORTANT: Always delete the old message first to avoid duplicates
                            try:
                                logger.info(f"Deleting old media message {dest_msg_id} in channel {dest_channel}")
                                await user_client.delete_messages(dest_channel, dest_msg_id)
                                logger.info(f"Successfully deleted old media message {dest_msg_id}")
                                
                                # We intentionally DON'T add this to sent_destinations
                                # This ensures the message will be reposted by the normal flow below
                                # and the mapping will be properly updated with the new message ID
                            except Exception as e:
                                logger.error(f"Error deleting old media message {dest_msg_id}: {e}")
                                # Even if deletion fails, we'll still try to repost below
                            
                            # Let the regular flow below handle reposting the updated media"""
    
    # Replace using regex with DOTALL flag to match across multiple lines
    updated_content = re.sub(media_edit_pattern, improved_media_section, content, flags=re.DOTALL)
    
    return updated_content

def update_message_mapping(content):
    """Enhance the message mapping function with better logging"""
    # Find the add_message_mapping function
    mapping_pattern = r"async def add_message_mapping.*?message_mapping\[key\]\[dest_channel\] = dest_msg_id"
    
    # Create improved implementation
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
    
    # Add or update the mapping
    previous_msg_id = message_mapping[key].get(dest_channel)
    message_mapping[key][dest_channel] = dest_msg_id
    
    if previous_msg_id and previous_msg_id != dest_msg_id:
        logger.info(f"Updated mapping for {key}: channel {dest_channel} from message {previous_msg_id} to {dest_msg_id}")
    else:
        logger.info(f"Added mapping for {key}: channel {dest_channel}, message {dest_msg_id}")
    
    # For debugging, display all current mappings
    logger.info(f"Current mappings count: {len(message_mapping)}")"""
    
    # Replace using regex with DOTALL flag to match across multiple lines
    updated_content = re.sub(mapping_pattern, improved_mapping, content, flags=re.DOTALL)
    
    return updated_content

def update_process_message_event(content):
    """Improve overall process_message_event function with better logging"""
    # Find where the function begins
    event_function_start = r"async def process_message_event\(event, is_edit=False\):"
    
    # Find the start of the function body
    function_start_match = re.search(event_function_start, content)
    
    if function_start_match:
        # Extract and modify the beginning of the function
        start_pos = function_start_match.start()
        
        # Find the position after the first few lines
        edit_logging_pos = content.find("# Get source channel and message ID", start_pos)
        
        if edit_logging_pos > start_pos:
            # Original beginning content
            original_beginning = content[start_pos:edit_logging_pos]
            
            # Enhanced beginning with better logging for edit detection
            enhanced_beginning = """async def process_message_event(event, is_edit=False):
    """Process message events (new or edited)"""
    # Check if reposting is active
    global reposting_active
    
    # Log edit status
    if is_edit:
        logger.info("Processing EDITED message event")
    else:
        logger.info("Processing NEW message event")
    
    # Initialize sent_destinations dictionary at the top level
    sent_destinations = {}
    
"""
            
            # Replace the beginning
            updated_content = content.replace(original_beginning, enhanced_beginning)
            return updated_content
    
    # If we couldn't find the right position, return original content
    return content

def main():
    """Main function to execute the fix"""
    print("Applying advanced fix for media edit handling...")
    
    # Fix bot.py
    bot_file = 'bot.py'
    print(f"\n1. Enhancing {bot_file} with advanced media edit fixes...")
    
    content = load_file(bot_file)
    
    # Create backup
    backup_file = f"{bot_file}.bak.advanced_edit_fix"
    print(f"   Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Apply all fixes
    print("   Enhancing handle_edited_message function...")
    updated_content = enhance_handle_edited_message(content)
    
    print("   Fixing media edit handling section...")
    updated_content = fix_media_edit_handling(updated_content)
    
    print("   Improving message mapping function...")
    updated_content = update_message_mapping(updated_content)
    
    print("   Enhancing process_message_event with better logging...")
    updated_content = update_process_message_event(updated_content)
    
    # Save the updated file
    if updated_content != content:
        print(f"   Saving updated {bot_file} with comprehensive improvements...")
        save_file(bot_file, updated_content)
        print(f"   ✅ Successfully enhanced media edit handling in {bot_file}")
    else:
        print(f"   ⚠️ No changes were made to {bot_file}. Pattern matching may have failed.")
    
    print("\n✅ Fix complete! Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()