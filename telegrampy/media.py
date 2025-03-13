"""
Media handling module for Telegram bots.
"""
import os
import logging
from typing import Optional, Union, Dict, Any, List
from pathlib import Path
from .types import Message
from .bot import Bot

logger = logging.getLogger(__name__)

class MediaHandler:
    """
    Handler for processing and managing media files.
    
    Attributes:
        bot (Bot): Bot instance
        download_path (Path): Path for downloaded files
        max_file_size (int): Maximum file size in bytes
        allowed_types (List[str]): List of allowed media types
    """
    
    def __init__(
        self,
        bot: Bot,
        download_path: Union[str, Path] = "downloads",
        max_file_size: int = 50 * 1024 * 1024,  # 50MB
        allowed_types: Optional[List[str]] = None
    ):
        """
        Initialize the media handler.
        
        Args:
            bot (Bot): Bot instance
            download_path (Union[str, Path]): Path for downloaded files
            max_file_size (int): Maximum file size in bytes
            allowed_types (Optional[List[str]]): List of allowed media types
        """
        self.bot = bot
        self.download_path = Path(download_path)
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types or [
            "photo", "video", "document", "audio", "voice",
            "video_note", "sticker", "animation"
        ]
        
        # Create download directory
        self.download_path.mkdir(parents=True, exist_ok=True)
        
    async def download_file(
        self,
        file_id: str,
        file_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Download a file from Telegram.
        
        Args:
            file_id (str): Telegram file ID
            file_name (Optional[str]): Custom file name
            
        Returns:
            Optional[Path]: Path to downloaded file
        """
        try:
            # Get file info
            file_info = await self.bot.get_file(file_id)
            
            # Check file size
            if file_info.file_size > self.max_file_size:
                logger.warning(f"File too large: {file_info.file_size} bytes")
                return None
                
            # Generate file name if not provided
            if not file_name:
                file_name = file_info.file_path.split("/")[-1]
                
            # Download file
            file_path = self.download_path / file_name
            await self.bot.download_file(file_info.file_path, file_path)
            
            return file_path
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
            
    async def process_media_message(self, message: Message) -> Optional[Dict[str, Any]]:
        """
        Process a media message.
        
        Args:
            message (Message): Message containing media
            
        Returns:
            Optional[Dict[str, Any]]: Processed media information
        """
        media_info = {}
        
        # Check media type
        for media_type in self.allowed_types:
            if getattr(message, media_type):
                media_info["type"] = media_type
                media_info["file_id"] = getattr(message, media_type).file_id
                break
                
        if not media_info:
            return None
            
        # Download file
        file_path = await self.download_file(media_info["file_id"])
        if file_path:
            media_info["file_path"] = file_path
            
        return media_info
        
    async def send_media(
        self,
        chat_id: Union[int, str],
        media_type: str,
        file_path: Union[str, Path],
        **kwargs
    ) -> Optional[Message]:
        """
        Send a media file.
        
        Args:
            chat_id (Union[int, str]): Target chat ID
            media_type (str): Type of media to send
            file_path (Union[str, Path]): Path to media file
            **kwargs: Additional parameters
            
        Returns:
            Optional[Message]: Sent message
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
                
            # Prepare file for upload
            with open(file_path, "rb") as f:
                file_data = f.read()
                
            # Send media based on type
            if media_type == "photo":
                return await self.bot.send_photo(chat_id, file_data, **kwargs)
            elif media_type == "video":
                return await self.bot.send_video(chat_id, file_data, **kwargs)
            elif media_type == "document":
                return await self.bot.send_document(chat_id, file_data, **kwargs)
            elif media_type == "audio":
                return await self.bot.send_audio(chat_id, file_data, **kwargs)
            elif media_type == "voice":
                return await self.bot.send_voice(chat_id, file_data, **kwargs)
            elif media_type == "video_note":
                return await self.bot.send_video_note(chat_id, file_data, **kwargs)
            elif media_type == "sticker":
                return await self.bot.send_sticker(chat_id, file_data, **kwargs)
            elif media_type == "animation":
                return await self.bot.send_animation(chat_id, file_data, **kwargs)
            else:
                logger.error(f"Unsupported media type: {media_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending media: {e}")
            return None
            
    def cleanup_old_files(self, max_age_days: int = 7) -> None:
        """
        Clean up old downloaded files.
        
        Args:
            max_age_days (int): Maximum age of files in days
        """
        import time
        current_time = time.time()
        max_age = max_age_days * 24 * 60 * 60  # Convert to seconds
        
        for file_path in self.download_path.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age:
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}") 