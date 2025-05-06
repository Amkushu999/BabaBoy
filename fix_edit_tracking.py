#!/usr/bin/env python3
"""
Fix for edited posts not being properly tracked and updated.
This script directly modifies how message mappings are stored in the bot.py file.
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

def fix_message_mappings(content):
    """Fix all instances where message mappings should be stored but aren't"""
    # Pattern to find places where mappings aren't stored
    pattern = r'# No message mapping stored \(per user requirements\)\s+if not is_edit and source_channel_id and source_message_id and dest_message:\s+dest_msg_id = dest_message\.id\s+sent_destinations\[dest_channel\] = dest_msg_id\s+logger\.info\(f"Message from \(\{source_channel_id\}, \{source_message_id\}\) reposted to \{dest_channel\}"\)'

    # Replacement that adds message mapping
    replacement = """# Store message mapping for edit synchronization
                        if not is_edit and source_channel_id and source_message_id and dest_message:
                            dest_msg_id = dest_message.id
                            # Use memory-efficient mapping function
                            await add_message_mapping(source_channel_id, source_message_id, dest_channel, dest_msg_id)
                            sent_destinations[dest_channel] = dest_msg_id
                            logger.info(f"Message from ({source_channel_id}, {source_message_id}) reposted to {dest_channel} with mapping stored")"""

    # Replace all occurrences
    updated_content = re.sub(pattern, replacement, content)
    
    # Count replacements
    count = content.count("# No message mapping stored (per user requirements)") - updated_content.count("# No message mapping stored (per user requirements)")
    
    return updated_content, count

def main():
    """Main function to execute the fix"""
    bot_file = 'bot.py'
    
    print(f"Reading {bot_file}...")
    content = load_file(bot_file)
    
    # Create backup
    backup_file = f"{bot_file}.bak"
    print(f"Creating backup at {backup_file}...")
    save_file(backup_file, content)
    
    # Fix the message mappings
    print("Fixing message mappings for edit tracking...")
    updated_content, count = fix_message_mappings(content)
    
    # Save the updated file
    print(f"Saving updated file with {count} fixed mappings...")
    save_file(bot_file, updated_content)
    
    print(f"✅ Successfully updated {count} message mappings in {bot_file}")
    print("Please restart the bot for the changes to take effect.")

if __name__ == "__main__":
    main()