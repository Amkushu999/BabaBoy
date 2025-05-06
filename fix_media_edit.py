#!/usr/bin/env python3
"""
Fix for media edits causing reposts instead of updates.
This script modifies the edited message handler to properly update
media posts in destination channels instead of deleting and reposting them.
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

def fix_media_edit_handling(content):
    """Fix the media edit handling to properly update instead of repost"""
    # Find the section where media edits are handled
    media_edit_pattern = r"""                        # Update the message in the destination channel
                        if msg_data\["has_media"\]:
                            # For media messages, we can't edit directly
                            # We'll need to delete and repost
                            logger\.info\(f"Can't directly edit media message\. Will delete and repost\."\)
                            
                            try:
                                # Try to delete the old message
                                await user_client\.delete_messages\(dest_channel, dest_msg_id\)
                                logger\.info\(f"Deleted old message {dest_msg_id} in channel {dest_channel}"\)
                            except Exception as e:
                                logger\.error\(f"Error deleting message {dest_msg_id} in channel {dest_channel}: {e}"\)
                                
                            # Let the regular flow repost the message
                            # We'll continue below with the normal posting mechanism"""
    
    # New improved code for handling media edits
    improved_media_edit_code = """                        # Update the message in the destination channel
                        if msg_data["has_media"]:
                            # For media messages with captions, we can still edit the caption
                            logger.info(f"Attempting to edit media message caption")
                            
                            try:
                                # Try to edit the caption/text of the media message
                                await user_client.edit_message(
                                    dest_channel,
                                    dest_msg_id,
                                    msg_data["text"] if "text" in msg_data and msg_data["text"] else "",
                                    parse_mode='html',
                                    link_preview=msg_data.get("link_preview", True)
                                )
                                logger.info(f"Successfully updated caption for media message {dest_msg_id} in channel {dest_channel}")
                                
                                # Flag this destination as already handled
                                sent_destinations[dest_channel] = dest_msg_id
                                continue  # Skip to next destination 
                            except Exception as e:
                                logger.error(f"Error updating media caption: {e}")
                                logger.info(f"Falling back to delete and repost method for media")
                                
                                try:
                                    # Try to delete the old message as fallback
                                    await user_client.delete_messages(dest_channel, dest_msg_id)
                                    logger.info(f"Deleted old message {dest_msg_id} in channel {dest_channel}")
                                except Exception as e:
                                    logger.error(f"Error deleting message {dest_msg_id} in channel {dest_channel}: {e}")
                                    
                                # Let the regular flow repost the message in case of failure
                                # We'll continue below with the normal posting mechanism"""
    
    # Replace the old code with the new implementation
    updated_content = re.sub(media_edit_pattern, improved_media_edit_code, content)
    
    return updated_content

def main():
    """Main function to execute the fix"""
    print("Fixing media edit handling to properly update media posts...")
    
    # Fix bot.py
    bot_file = 'bot.py'
    print(f"\n1. Modifying {bot_file}...")
    
    content = load_file(bot_file)
    
    # Create backup
    backup_file = f"{bot_file}.bak.media_edit"
    print(f"   Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Add media edit fix
    updated_content = fix_media_edit_handling(content)
    
    # Save the updated file
    if updated_content != content:
        print(f"   Saving updated {bot_file} with media edit handling improvements...")
        save_file(bot_file, updated_content)
        print(f"   ✅ Successfully improved media edit handling in {bot_file}")
    else:
        print(f"   ⚠️ No changes made to {bot_file}. Pattern might not have been found.")
    
    print("\n✅ Fix complete! Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()