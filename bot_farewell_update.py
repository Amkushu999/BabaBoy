"""
Update the bot to send a GIF with audio when leaving a channel.

This script updates the bot's channel cleanup feature to send a randomly selected
GIF along with an audio file before leaving a channel.
"""

import os
import re
import sys
import json
import random

# Create necessary directories
os.makedirs("assets/farewell", exist_ok=True)

# Create constants.py file
constants_content = """
\"\"\"
Constants for farewell GIFs and audio when the bot leaves a channel.
\"\"\"

# List of GIF URLs to be used when leaving a channel
FAREWELL_GIFS = [
    # These will be replaced with the actual GIF links
    "Gif_2",
    "Gif_3",
    "Gif_4",
    "Gif_5",
    "Gif_6",
    "Gif_7",
    "Gif_8",
    "Gif_9",
    "Gif_10"
]

# Path to the audio file to play when leaving
FAREWELL_AUDIO = "assets/farewell/postNleft.mp3"
"""

with open("assets/farewell/constants.py", "w") as f:
    f.write(constants_content)

# Create __init__.py file
with open("assets/farewell/__init__.py", "w") as f:
    pass

# Update bot.py to use GIFs instead of stickers
bot_file = "bot.py"

with open(bot_file, "r") as f:
    content = f.read()

# Find the section where the farewell sticker is sent
sticker_section_pattern = r"# If all sticker attempts failed, try to send a text message[\s\S]+?if not sticker_success:[\s\S]+?try:[\s\S]+?await user_client\.send_message\([^)]+\)[\s\S]+?except Exception as text_error:"

# Prepare the replacement code
replacement_code = """# If all sticker attempts failed, try sending a GIF with audio
                            if not sticker_success:
                                try:
                                    # Import farewell GIFs and audio constants
                                    try:
                                        from assets.farewell.constants import FAREWELL_GIFS, FAREWELL_AUDIO
                                        logger.info(f"Loaded {len(FAREWELL_GIFS)} farewell GIFs")
                                    except ImportError:
                                        logger.error("Could not import farewell constants")
                                        FAREWELL_GIFS = []
                                        FAREWELL_AUDIO = None
                                    
                                    # Send a random GIF if available
                                    if FAREWELL_GIFS:
                                        # Select a random GIF
                                        random_gif = random.choice(FAREWELL_GIFS)
                                        logger.info(f"Selected farewell GIF: {random_gif}")
                                        
                                        # Check if the audio file exists
                                        audio_exists = FAREWELL_AUDIO and os.path.exists(FAREWELL_AUDIO)
                                        logger.info(f"Audio file exists: {audio_exists}, path: {FAREWELL_AUDIO}")
                                        
                                        if audio_exists:
                                            # Send audio file first
                                            await user_client.send_file(
                                                channel_entity,
                                                FAREWELL_AUDIO,
                                                voice_note=True  # Send as voice message
                                            )
                                            logger.info("Sent farewell audio")
                                        
                                        # Send the GIF
                                        await user_client.send_file(
                                            channel_entity,
                                            random_gif,
                                            caption="👋 Channel cleanup completed."
                                        )
                                        logger.info("Sent farewell GIF")
                                        sticker_success = True
                                    else:
                                        # Fallback to text message if no GIFs defined
                                        await user_client.send_message(
                                            channel_entity, 
                                            "👋 Goodbye! Channel cleanup completed."
                                        )
                                        logger.info("Sent text farewell message (fallback)")
                                        sticker_success = True  # We succeeded with the text message
                                except Exception as gif_error:
                                    logger.error(f"Error sending farewell GIF/audio: {str(gif_error)}")
                                    
                                    # Ultimate fallback to simple text message
                                    try:
                                        await user_client.send_message(
                                            channel_entity, 
                                            "👋 Goodbye! Channel cleanup completed."
                                        )
                                        logger.info("Sent text farewell message (ultimate fallback)")
                                        sticker_success = True
                                    except Exception as text_error:"""

# Replace the sticker section with the new GIF+audio code
modified_content = re.sub(sticker_section_pattern, replacement_code, content)

# Add the random import at the top of the file if not already present
if "import random" not in modified_content:
    modified_content = re.sub(
        r"import os",
        "import os\nimport random",
        modified_content
    )

# Write the modified content back to the file
with open(bot_file, "w") as f:
    f.write(modified_content)

print("✅ Bot updated to use GIFs and audio for farewells")
print("✅ Created assets/farewell/constants.py with placeholder GIF links")
print("✅ Created necessary directory structure")
print("\nNOTE: Update the GIF links in assets/farewell/constants.py with the actual GIF URLs")
print("      Place the audio file at assets/farewell/postNleft.mp3")