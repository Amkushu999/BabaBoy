
"""
Constants for farewell GIFs and audio when the bot leaves a channel.
"""

# List of GIF URLs to be used when leaving a channel
FAREWELL_GIFS = [
    # These GIF URLs will be used randomly when leaving a channel
    # Using direct media URLs (not webpage URLs)
    "https://media.giphy.com/media/ySEd2yk70L4Fz70tyn/giphy.gif",
    "https://media.giphy.com/media/BcBwiPAP8cZiqErls6/giphy.gif",
    "https://media.giphy.com/media/tNZ9Y9Na9oPWzCjvaK/giphy.gif",
    "https://media.giphy.com/media/X5bgxAHH2WbPTBdaR7/giphy.gif",
    "https://media.giphy.com/media/3BFvBCDk902GSq2l3y/giphy.gif",
    "https://media.giphy.com/media/03RkbQb84ZWtAjN7X0/giphy.gif",
]

# List of audio files to rotate through when leaving
FAREWELL_AUDIO_FILES = [
    "assets/farewell/laugh_or_cry.m4a",  # Simpler filename for better reliability
    "assets/farewell/piercing_light.mp3"  # Simpler filename for better reliability
]

# For backward compatibility (will be chosen randomly from FAREWELL_AUDIO_FILES)
FAREWELL_AUDIO = FAREWELL_AUDIO_FILES[0]

# Creator information for credits
CREATOR_NAME = "ªᴹᴷᵁˢᴴ"
CREATOR_USERNAME = "@Amkushu"
CREATOR_LINK = f"https://t.me/{CREATOR_USERNAME.replace('@', '')}"
