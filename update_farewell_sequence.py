"""
Update the farewell sequence in the bot to match the specified order:
1. Show "Bot by ªᴹᴷᵁˢᴴ" with hyperlink
2. Post random GIF (no caption)
3. Send audio file
4. Leave channel

For just deleting messages (without leaving), only show credits.
"""

import os
import re
import sys

# Get the full sticker section until the exit message
def extract_sticker_section(content):
    """Extract the farewell sticker section from the bot code"""
    pattern = r'# Try to send farewell stickers[\s\S]+?# Leave the channel'
    match = re.search(pattern, content)
    if match:
        return match.group(0)
    return None

# Create replacement code with the new sequence
def get_new_farewell_sequence():
    """Get the new farewell sequence code"""
    return """
                            # New farewell sequence as requested
                            await status_msg.edit_text(
                                "🗑️ Purge completed. Sending farewell sequence..."
                            )
                            
                            # Import the required constants first
                            try:
                                from assets.farewell.constants import FAREWELL_GIFS, FAREWELL_AUDIO
                                from assets.farewell.constants import CREATOR_NAME, CREATOR_USERNAME, CREATOR_LINK
                                logger.info(f"Loaded farewell constants: {len(FAREWELL_GIFS)} GIFs")
                            except ImportError as import_err:
                                logger.error(f"Could not import farewell constants: {str(import_err)}")
                                # Set defaults if import fails
                                FAREWELL_GIFS = []
                                FAREWELL_AUDIO = "assets/farewell/bye.mp3"
                                CREATOR_NAME = "ªᴹᴷᵁˢᴴ"
                                CREATOR_USERNAME = "@Amkushu"
                                CREATOR_LINK = "https://t.me/Amkushu"
                            
                            # 1. First send credits message with hyperlink
                            credit_message = f"Bot by <a href='{CREATOR_LINK}'>{CREATOR_NAME}</a>"
                            credit_sent = False
                            
                            try:
                                await user_client.send_message(
                                    channel_entity,
                                    credit_message,
                                    parse_mode='html'
                                )
                                logger.info("Sent credits message with hyperlink")
                                credit_sent = True
                            except Exception as cred_err:
                                logger.error(f"Failed to send credits with HTML formatting: {str(cred_err)}")
                                # Try plain text as fallback
                                try:
                                    await user_client.send_message(
                                        channel_entity,
                                        f"Bot by {CREATOR_NAME} ({CREATOR_USERNAME})"
                                    )
                                    logger.info("Sent plain text credits (fallback)")
                                    credit_sent = True
                                except Exception as plain_err:
                                    logger.error(f"Failed to send plain text credits: {str(plain_err)}")
                            
                            # Check if we should continue with the full farewell sequence
                            if purge_and_leave and credit_sent:
                                # 2. Send a random GIF (without caption)
                                gif_sent = False
                                if FAREWELL_GIFS:
                                    try:
                                        import random
                                        # Select a random GIF
                                        random_gif = random.choice(FAREWELL_GIFS)
                                        logger.info(f"Selected farewell GIF: {random_gif}")
                                        
                                        # Send the GIF without any caption
                                        await user_client.send_file(
                                            channel_entity,
                                            random_gif  # No caption parameter
                                        )
                                        logger.info("Sent farewell GIF without caption")
                                        gif_sent = True
                                    except Exception as gif_err:
                                        logger.error(f"Failed to send GIF: {str(gif_err)}")
                                else:
                                    logger.warning("No farewell GIFs available")
                                
                                # 3. Send the audio file
                                audio_sent = False
                                audio_path = FAREWELL_AUDIO
                                if os.path.exists(audio_path):
                                    try:
                                        await user_client.send_file(
                                            channel_entity,
                                            audio_path,
                                            voice_note=True
                                        )
                                        logger.info("Sent farewell audio")
                                        audio_sent = True
                                    except Exception as audio_err:
                                        logger.error(f"Failed to send audio: {str(audio_err)}")
                                else:
                                    logger.warning(f"Audio file not found: {audio_path}")
                                
                                # 4. Now prepare to leave the channel
                                await status_msg.edit_text(
                                    "👋 Leaving channel..."
                                )
                            else:
                                # For regular purge (not leaving), we only show credits
                                logger.info("Message purge completed without leaving")
                                
                            # Leave the channel"""

# Main update function
def update_bot_farewell_sequence():
    """Update the bot.py file to have the new farewell sequence"""
    bot_file = "bot.py"
    
    if not os.path.exists(bot_file):
        print(f"Error: {bot_file} does not exist")
        return False
    
    try:
        # Read the content of bot.py
        with open(bot_file, "r") as file:
            content = file.read()
        
        # Extract the original sticker section
        original_section = extract_sticker_section(content)
        if not original_section:
            print("Error: Could not locate the farewell sticker section in bot.py")
            return False
        
        # Get the new farewell sequence
        new_section = get_new_farewell_sequence()
        
        # Replace the original section with the new one
        new_content = content.replace(original_section, new_section)
        
        # Make sure "purge_and_leave" is properly handled
        if "purge_and_leave = (query.data == \"purge_leave_existing\")" in content:
            print("✓ 'purge_and_leave' variable already defined")
        else:
            print("! Warning: 'purge_and_leave' variable not found")
            # This won't happen in the current code as we've already found it
        
        # Write the updated content back to bot.py
        with open(bot_file, "w") as file:
            file.write(new_content)
        
        print(f"✅ Successfully updated farewell sequence in {bot_file}")
        return True
    
    except Exception as e:
        print(f"Error updating bot.py: {str(e)}")
        return False

# Also update the regular purge completion message to show credits
def update_regular_purge_message():
    """Update the regular purge completion message to show credits"""
    bot_file = "bot.py"
    
    try:
        with open(bot_file, "r") as file:
            content = file.read()
        
        # Find the regular purge completion section
        pattern = r'# Regular purge completion message[\s\S]+?await status_msg\.edit_text\(\s+f"[^"]+?"\s*,'
        match = re.search(pattern, content)
        
        if not match:
            print("Warning: Could not find regular purge completion message")
            return False
        
        # Get the matched text
        original_msg = match.group(0)
        
        # Create new message with credits notice
        new_msg = """# Regular purge completion message
                        await status_msg.edit_text(
                            f"✅ Channel purge completed!\\n\\n"
                            f"Successfully deleted {deleted_count} messages.\\n\\n"
                            f"A credits message has been posted in the channel.\\n\\n"
                            f"Return to menu to continue using the bot.","""
        
        # Replace it in the content
        new_content = content.replace(original_msg, new_msg)
        
        # Write the updated content back
        with open(bot_file, "w") as file:
            file.write(new_content)
        
        print("✅ Successfully updated regular purge completion message")
        return True
        
    except Exception as e:
        print(f"Error updating regular purge message: {str(e)}")
        return False

# Run both updates
if __name__ == "__main__":
    print("Updating farewell sequence...")
    if update_bot_farewell_sequence():
        update_regular_purge_message()
    print("Update complete!")