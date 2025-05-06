"""
Update the farewell GIF links in the constants file.

Usage:
    python update_farewell_gifs.py <gif_url_1> <gif_url_2> ... <gif_url_n>
"""

import os
import sys
import re

def update_farewell_gifs(gif_urls):
    """Update the farewell GIF links in the constants file."""
    constants_file = "assets/farewell/constants.py"
    
    # Check if constants file exists
    if not os.path.exists(constants_file):
        print(f"Error: {constants_file} does not exist")
        return False
    
    # Read the current content
    with open(constants_file, "r") as f:
        content = f.read()
    
    # Parse the current GIF list
    gif_pattern = r"FAREWELL_GIFS\s*=\s*\[([\s\S]*?)\]"
    gif_match = re.search(gif_pattern, content)
    
    if not gif_match:
        print(f"Error: Could not find FAREWELL_GIFS in {constants_file}")
        return False
    
    # Format the new GIF list
    new_gif_list = "\n    # These GIF URLs will be used randomly when leaving a channel\n"
    for url in gif_urls:
        new_gif_list += f'    "{url}",\n'
    
    # Replace the old GIF list with the new one
    new_content = re.sub(
        gif_pattern,
        f"FAREWELL_GIFS = [{new_gif_list}]",
        content
    )
    
    # Write the updated content back to the file
    with open(constants_file, "w") as f:
        f.write(new_content)
    
    print(f"✅ Updated {len(gif_urls)} GIF URLs in {constants_file}")
    return True

if __name__ == "__main__":
    # Check if there are any GIF URLs provided
    if len(sys.argv) < 2:
        print("Error: No GIF URLs provided")
        print(f"Usage: python {sys.argv[0]} <gif_url_1> <gif_url_2> ... <gif_url_n>")
        sys.exit(1)
    
    # Update the GIF URLs
    gif_urls = sys.argv[1:]
    update_farewell_gifs(gif_urls)