"""
Story interaction module for Telegram bots.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .types import Message, Story
from .keyboard import KeyboardBuilder

logger = logging.getLogger(__name__)

class StoryHandler:
    """
    Handler for story interactions.
    
    Attributes:
        max_stories_per_user (int): Maximum number of stories per user
        story_duration (int): Story duration in seconds
        allowed_media_types (List[str]): List of allowed media types
        story_cache (Dict[int, Dict[str, Any]]): Cache for story data
    """
    
    def __init__(
        self,
        max_stories_per_user: int = 10,
        story_duration: int = 86400,  # 24 hours
        allowed_media_types: Optional[List[str]] = None
    ):
        """
        Initialize the story handler.
        
        Args:
            max_stories_per_user (int): Maximum number of stories per user
            story_duration (int): Story duration in seconds
            allowed_media_types (Optional[List[str]]): List of allowed media types
        """
        self.max_stories_per_user = max_stories_per_user
        self.story_duration = story_duration
        self.allowed_media_types = allowed_media_types or [
            "photo", "video", "animation"
        ]
        self.story_cache: Dict[int, Dict[str, Any]] = {}
        
    def is_allowed_media_type(self, media_type: str) -> bool:
        """
        Check if a media type is allowed.
        
        Args:
            media_type (str): Media type to check
            
        Returns:
            bool: True if media type is allowed
        """
        return media_type in self.allowed_media_types
        
    async def create_story(
        self,
        user_id: int,
        media_type: str,
        media_data: Dict[str, Any],
        caption: Optional[str] = None
    ) -> Optional[Story]:
        """
        Create a new story.
        
        Args:
            user_id (int): User ID
            media_type (str): Type of media
            media_data (Dict[str, Any]): Media data
            caption (Optional[str]): Story caption
            
        Returns:
            Optional[Story]: Created story
        """
        try:
            if not self.is_allowed_media_type(media_type):
                logger.warning(f"Unsupported media type: {media_type}")
                return None
                
            # Check user's story limit
            user_stories = self.get_user_stories(user_id)
            if len(user_stories) >= self.max_stories_per_user:
                logger.warning(f"User {user_id} has reached story limit")
                return None
                
            # Create story
            story = Story(
                user_id=user_id,
                media_type=media_type,
                media_data=media_data,
                caption=caption,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=self.story_duration)
            )
            
            # Add to cache
            if user_id not in self.story_cache:
                self.story_cache[user_id] = []
            self.story_cache[user_id].append(story)
            
            logger.info(f"Story created for user {user_id}")
            return story
            
        except Exception as e:
            logger.error(f"Error creating story: {e}")
            return None
            
    def get_user_stories(self, user_id: int) -> List[Story]:
        """
        Get all stories for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            List[Story]: List of user's stories
        """
        stories = self.story_cache.get(user_id, [])
        return [s for s in stories if s.expires_at > datetime.now()]
        
    def get_story(self, user_id: int, story_id: str) -> Optional[Story]:
        """
        Get a specific story.
        
        Args:
            user_id (int): User ID
            story_id (str): Story ID
            
        Returns:
            Optional[Story]: Story if found
        """
        stories = self.get_user_stories(user_id)
        for story in stories:
            if story.id == story_id:
                return story
        return None
        
    async def delete_story(
        self,
        user_id: int,
        story_id: str
    ) -> bool:
        """
        Delete a story.
        
        Args:
            user_id (int): User ID
            story_id (str): Story ID
            
        Returns:
            bool: True if story was deleted
        """
        try:
            if user_id in self.story_cache:
                self.story_cache[user_id] = [
                    s for s in self.story_cache[user_id]
                    if s.id != story_id
                ]
                logger.info(f"Story {story_id} deleted for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting story: {e}")
            return False
            
    def create_story_keyboard(
        self,
        user_id: int,
        story_id: str
    ) -> Dict[str, Any]:
        """
        Create a keyboard for story interactions.
        
        Args:
            user_id (int): User ID
            story_id (str): Story ID
            
        Returns:
            Dict[str, Any]: Keyboard markup
        """
        builder = KeyboardBuilder()
        
        # Add view button
        builder.add_button(
            text="👁 View Story",
            callback_data=f"view_story_{user_id}_{story_id}"
        )
        
        # Add like button
        builder.add_button(
            text="❤️ Like",
            callback_data=f"like_story_{user_id}_{story_id}"
        )
        
        # Add share button
        builder.add_button(
            text="🔄 Share",
            callback_data=f"share_story_{user_id}_{story_id}"
        )
        
        # Add delete button if user owns the story
        if user_id == story_id.split("_")[0]:
            builder.add_button(
                text="🗑 Delete",
                callback_data=f"delete_story_{user_id}_{story_id}"
            )
            
        return builder.build().to_dict()
        
    def get_story_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get story statistics for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict[str, Any]: Story statistics
        """
        stories = self.get_user_stories(user_id)
        return {
            "total_stories": len(stories),
            "active_stories": len([s for s in stories if s.expires_at > datetime.now()]),
            "expired_stories": len([s for s in stories if s.expires_at <= datetime.now()]),
            "media_types": {
                mt: len([s for s in stories if s.media_type == mt])
                for mt in self.allowed_media_types
            }
        }
        
    def cleanup_expired_stories(self) -> None:
        """Clean up expired stories from cache."""
        for user_id in list(self.story_cache.keys()):
            self.story_cache[user_id] = [
                s for s in self.story_cache[user_id]
                if s.expires_at > datetime.now()
            ]
            if not self.story_cache[user_id]:
                del self.story_cache[user_id]
                
    def format_story_message(
        self,
        story: Story
    ) -> str:
        """
        Format a story message.
        
        Args:
            story (Story): Story to format
            
        Returns:
            str: Formatted message
        """
        message = f"📱 Story by {story.user_id}\n"
        message += f"Type: {story.media_type}\n"
        message += f"Created: {story.created_at}\n"
        message += f"Expires: {story.expires_at}\n"
        
        if story.caption:
            message += f"\nCaption: {story.caption}"
            
        return message 