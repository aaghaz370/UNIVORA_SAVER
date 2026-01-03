import asyncio
import time
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserNotParticipant, ChannelPrivate
from typing import Optional, Dict, Callable
import config
from database import db
from utils import (
    create_progress_message, 
    format_file_size, 
    sanitize_filename,
    apply_rename_format,
    apply_caption_format
)

class ContentExtractor:
    """Main content extraction handler"""
    
    def __init__(self):
        self.active_extractions: Dict[int, bool] = {}
        self.user_clients: Dict[int, Client] = {}
    
    async def get_user_client(self, user_id: int) -> Optional[Client]:
        """Get or create Pyrogram client for user"""
        if user_id in self.user_clients:
            return self.user_clients[user_id]
        
        # Get session from database
        session_data = await db.get_session(user_id)
        if not session_data:
            return None
        
        try:
            client = Client(
                f"user_{user_id}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=session_data['session_string']
            )
            await client.start()
            self.user_clients[user_id] = client
            return client
        except Exception as e:
            print(f"Error creating user client: {e}")
            return None
    
    async def extract_messages(
        self,
        user_id: int,
        chat_id: int | str,
        start_message_id: int,
        count: int,
        progress_callback: Callable,
        destination_chat_id: Optional[int] = None,
        settings: Optional[dict] = None
    ):
        """
        Extract and forward/download messages from a channel/group
        
        Args:
            user_id: User's Telegram ID
            chat_id: Source chat ID or username
            start_message_id: Starting message ID
            count: Number of messages to extract
            progress_callback: Async function to call with progress updates
            destination_chat_id: Where to forward messages (None = send to user)
            settings: User settings for caption, rename, etc.
        """
        try:
            # Get user client
            client = await self.get_user_client(user_id)
            if not client:
                await progress_callback("❌ Please login first using /login", None)
                return
            
            # Mark extraction as active
            self.active_extractions[user_id] = True
            
            # Get settings
            settings = settings or await db.get_settings(user_id)
            destination = destination_chat_id or settings.get('chat_id') or user_id
            
            # Create job in database
            job = await db.create_job(user_id, "batch_extraction", count)
            
            processed = 0
            errors = 0
            
            for i in range(count):
                # Check if cancelled
                if not self.active_extractions.get(user_id):
                    await progress_callback("❌ Extraction cancelled by user", job['_id'])
                    break
                
                message_id = start_message_id + i
                
                try:
                    # Get message
                    message = await client.get_messages(chat_id, message_id)
                    
                    if not message or message.empty:
                        errors += 1
                        continue
                    
                    # Process based on message type
                    if message.media:
                        await self._handle_media_message(
                            client, message, destination, user_id, settings, i
                        )
                    else:
                        # Forward text message
                        await client.forward_messages(
                            destination, chat_id, message_id
                        )
                    
                    processed += 1
                    
                    # Update progress
                    await db.update_job_progress(job['_id'], processed)
                    await progress_callback(
                        f"Processing: {processed}/{count}",
                        job['_id'],
                        processed,
                        count
                    )
                    
                    # Small delay to avoid flood
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    print(f"Error processing message {message_id}: {e}")
                    errors += 1
                    continue
            
            # Cleanup
            self.active_extractions[user_id] = False
            await db.increment_user_stat(user_id, "total_extractions")
            
            # Send completion message
            completion_msg = f"""✅ **Extraction Complete!**

📊 **Statistics:**
✔️ Processed: {processed}
❌ Failed: {errors}
📝 Total: {count}

**Powered by RATNA**"""
            
            await progress_callback(completion_msg, job['_id'], processed, count, True)
            
        except ChannelPrivate:
            await progress_callback("❌ This is a private channel. Please login first using /login", None)
        except UserNotParticipant:
            await progress_callback("❌ You are not a member of this channel/group", None)
        except Exception as e:
            print(f"Extraction error: {e}")
            await progress_callback(f"❌ Error: {str(e)}", None)
        finally:
            self.active_extractions[user_id] = False
    
    async def _handle_media_message(
        self,
        client: Client,
        message: Message,
        destination: int,
        user_id: int,
        settings: dict,
        index: int
    ):
        """Handle media message with custom settings"""
        try:
            # Get original filename
            if message.document:
                original_name = message.document.file_name or f"file_{index}"
            elif message.video:
                original_name = message.video.file_name or f"video_{index}.mp4"
            elif message.audio:
                original_name = message.audio.file_name or f"audio_{index}.mp3"
            elif message.photo:
                original_name = f"photo_{index}.jpg"
            else:
                # Just forward if no special handling needed
                await message.forward(destination)
                return
            
            # Apply rename format if set
            rename_format = settings.get('rename_format')
            if rename_format:
                file_name = apply_rename_format(original_name, rename_format, index)
            else:
                file_name = original_name
            
            # Apply custom caption if set
            custom_caption = settings.get('custom_caption')
            file_size = getattr(message.document or message.video or message.audio, 'file_size', 0)
            
            if custom_caption:
                caption = apply_caption_format(custom_caption, file_name, file_size, index)
            else:
                caption = message.caption
            
            # Get custom thumbnail if set
            thumb = settings.get('thumbnail')
            
            # Copy message with modifications
            await message.copy(
                destination,
                caption=caption,
                file_name=file_name
            )
            
        except Exception as e:
            print(f"Error handling media: {e}")
            # Fallback to simple forward
            await message.forward(destination)
    
    async def download_media(
        self,
        user_id: int,
        message_url: str,
        progress_callback: Callable,
        download_type: str = 'video'  # 'video' or 'audio'
    ):
        """Download media from message URL"""
        try:
            client = await self.get_user_client(user_id)
            if not client:
                await progress_callback("❌ Please login first using /login")
                return None
            
            # Parse message URL
            from utils import parse_telegram_link
            parsed = parse_telegram_link(message_url)
            if not parsed:
                await progress_callback("❌ Invalid Telegram link")
                return None
            
            chat_id, message_id, _ = parsed
            
            # Get message
            message = await client.get_messages(chat_id, message_id)
            if not message or not message.media:
                await progress_callback("❌ No media found in this message")
                return None
            
            # Progress tracking
            start_time = time.time()
            last_update = 0
            
            async def download_progress(current, total):
                nonlocal last_update
                now = time.time()
                
                # Update every 2 seconds
                if now - last_update < 2:
                    return
                
                last_update = now
                elapsed = now - start_time
                speed = current / elapsed if elapsed > 0 else 0
                eta = int((total - current) / speed) if speed > 0 else 0
                
                progress_msg = create_progress_message(
                    current, total, current, total, speed, eta
                )
                await progress_callback(progress_msg, current, total)
            
            # Download file
            file_path = await message.download(
                file_name=f"downloads/",
                progress=download_progress
            )
            
            await db.increment_user_stat(user_id, "total_downloads")
            
            return file_path
            
        except Exception as e:
            print(f"Download error: {e}")
            await progress_callback(f"❌ Download failed: {str(e)}")
            return None
    
    async def cancel_extraction(self, user_id: int):
        """Cancel active extraction for user"""
        self.active_extractions[user_id] = False
        job = await db.get_active_job(user_id)
        if job:
            await db.cancel_job(job['_id'])
    
    async def cleanup_user_client(self, user_id: int):
        """Stop and remove user client"""
        if user_id in self.user_clients:
            try:
                await self.user_clients[user_id].stop()
            except:
                pass
            del self.user_clients[user_id]

# Global extractor instance
extractor = ContentExtractor()
