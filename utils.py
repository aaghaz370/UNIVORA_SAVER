import re
from typing import Optional, Tuple

def parse_telegram_link(link: str) -> Optional[Tuple[str, int, int]]:
    """
    Parse Telegram link and extract channel/chat info
    Supports:
    - t.me/c/CHANNEL_ID/MESSAGE_ID
    - t.me/CHANNEL_USERNAME/MESSAGE_ID
    - https://t.me/c/CHANNEL_ID/MESSAGE_ID
    
    Returns: (chat_identifier, start_message_id, chat_type)
    chat_type: 'private' or 'public'
    """
    # Remove any whitespace
    link = link.strip()
    
    # Pattern for private channel: t.me/c/123456789/100
    private_pattern = r't\.me/c/(\d+)/(\d+)'
    # Pattern for public channel: t.me/username/100
    public_pattern = r't\.me/([a-zA-Z0-9_]+)/(\d+)'
    
    private_match = re.search(private_pattern, link)
    if private_match:
        chat_id = int(f"-100{private_match.group(1)}")
        message_id = int(private_match.group(2))
        return (chat_id, message_id, 'private')
    
    public_match = re.search(public_pattern, link)
    if public_match:
        username = public_match.group(1)
        message_id = int(public_match.group(2))
        return (username, message_id, 'public')
    
    return None

def format_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a visual progress bar"""
    filled = int(length * current / total) if total > 0 else 0
    bar = "◆" * filled + "◇" * (length - filled)
    return bar

def format_file_size(bytes_size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m, {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h, {minutes}m"

def calculate_percentage(current: int, total: int) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (current / total) * 100

def create_progress_message(current: int, total: int, downloaded_bytes: int, 
                           total_bytes: int, speed: float, eta: int) -> str:
    """
    Create beautiful progress message like the reference bot
    """
    progress_bar = format_progress_bar(current, total, 10)
    percentage = calculate_percentage(downloaded_bytes, total_bytes)
    
    message = f"""╭─────────────────────╮
│      Downloading...
├─────────────────────
│ {progress_bar}

│ Completed: {format_file_size(downloaded_bytes)}/{format_file_size(total_bytes)}
│ Bytes: {percentage:.2f}%
│ Speed: {format_file_size(int(speed))}/s
│ ETA: {format_time(eta)}
╰─────────────────────╯"""
    
    return message

def create_batch_progress_message(current: int, total: int) -> str:
    """Create batch process progress message"""
    return f"""**Batch process started ⚡**
Processing: {current}/{total}

**Powered by RATNA**"""

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + '.' + ext if ext else name[:200]
    return filename

def apply_rename_format(original_name: str, rename_format: str, index: int = 0) -> str:
    """
    Apply custom rename format
    Variables: {index}, {name}, {ext}
    """
    if not rename_format:
        return original_name
    
    # Split name and extension
    if '.' in original_name:
        name, ext = original_name.rsplit('.', 1)
    else:
        name, ext = original_name, ''
    
    # Replace variables
    new_name = rename_format.replace('{index}', str(index))
    new_name = new_name.replace('{name}', name)
    new_name = new_name.replace('{ext}', ext)
    
    return sanitize_filename(new_name)

def apply_caption_format(caption_template: str, file_name: str, file_size: int, 
                        index: int = 0) -> str:
    """
    Apply custom caption format
    Variables: {filename}, {size}, {index}
    """
    if not caption_template:
        return None
    
    caption = caption_template.replace('{filename}', file_name)
    caption = caption.replace('{size}', format_file_size(file_size))
    caption = caption.replace('{index}', str(index))
    
    return caption

def validate_chat_id(chat_id: str) -> Optional[int]:
    """Validate and convert chat ID"""
    try:
        # Remove -100 prefix if exists
        if chat_id.startswith('-100'):
            return int(chat_id)
        else:
            return int(f"-100{chat_id}")
    except:
        return None

def is_owner(user_id: int) -> bool:
    """Check if user is owner"""
    from config import OWNER_ID, ADMIN_IDS
    return user_id == OWNER_ID or user_id in ADMIN_IDS

async def check_user_limit(user_id: int, is_premium: bool) -> int:
    """Get max batch limit for user"""
    from config import PREMIUM_MAX_BATCH, FREE_MAX_BATCH
    return PREMIUM_MAX_BATCH if is_premium else FREE_MAX_BATCH

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
