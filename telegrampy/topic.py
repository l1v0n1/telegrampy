"""
Topic management module for Telegram groups with forum topics.
"""
import logging
from typing import Optional, Dict, Any, List, Union

from .types import Message, Chat
from .keyboard import KeyboardBuilder

logger = logging.getLogger(__name__)

class TopicManager:
    """
    Manager for forum topics in Telegram groups.
    
    Attributes:
        max_topics_per_group (int): Maximum number of topics per group
        topic_cache (Dict[int, Dict[int, Dict[str, Any]]]): Cache for topic data
    """
    
    def __init__(
        self,
        max_topics_per_group: int = 100
    ):
        """
        Initialize the topic manager.
        
        Args:
            max_topics_per_group (int): Maximum number of topics per group
        """
        self.max_topics_per_group = max_topics_per_group
        self.topic_cache: Dict[int, Dict[int, Dict[str, Any]]] = {}
        
    async def create_topic(
        self,
        bot: Any,
        chat_id: int,
        name: str,
        icon_color: Optional[int] = None,
        icon_custom_emoji_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new forum topic.
        
        Args:
            bot (Bot): Bot instance
            chat_id (int): Chat ID
            name (str): Topic name
            icon_color (Optional[int]): Color of the topic icon
            icon_custom_emoji_id (Optional[str]): Custom emoji for topic icon
            
        Returns:
            Optional[Dict[str, Any]]: Created topic data
        """
        try:
            # Check if chat is a forum
            chat = await bot.get_chat(chat_id)
            if not chat.is_forum:
                logger.warning(f"Chat {chat_id} is not a forum")
                return None
                
            # Check topic limit
            if chat_id in self.topic_cache and len(self.topic_cache[chat_id]) >= self.max_topics_per_group:
                logger.warning(f"Group {chat_id} has reached topic limit")
                return None
                
            # Create topic
            params = {
                "chat_id": chat_id,
                "name": name
            }
            
            if icon_color:
                params["icon_color"] = icon_color
                
            if icon_custom_emoji_id:
                params["icon_custom_emoji_id"] = icon_custom_emoji_id
                
            result = await bot.create_forum_topic(**params)
            
            if result and "message_thread_id" in result:
                topic_data = {
                    "message_thread_id": result["message_thread_id"],
                    "name": name,
                    "created_at": result.get("created_at", None),
                    "icon_color": icon_color,
                    "icon_custom_emoji_id": icon_custom_emoji_id
                }
                
                # Add to cache
                if chat_id not in self.topic_cache:
                    self.topic_cache[chat_id] = {}
                    
                self.topic_cache[chat_id][result["message_thread_id"]] = topic_data
                
                logger.info(f"Topic '{name}' created in chat {chat_id}")
                return topic_data
            else:
                logger.error(f"Failed to create topic: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating topic: {e}")
            return None
            
    async def edit_topic(
        self,
        bot: Any,
        chat_id: int,
        message_thread_id: int,
        name: Optional[str] = None,
        icon_custom_emoji_id: Optional[str] = None
    ) -> bool:
        """
        Edit a forum topic.
        
        Args:
            bot (Bot): Bot instance
            chat_id (int): Chat ID
            message_thread_id (int): Message thread ID
            name (Optional[str]): New topic name
            icon_custom_emoji_id (Optional[str]): New custom emoji for topic icon
            
        Returns:
            bool: True if topic was edited
        """
        try:
            params = {
                "chat_id": chat_id,
                "message_thread_id": message_thread_id
            }
            
            if name:
                params["name"] = name
                
            if icon_custom_emoji_id:
                params["icon_custom_emoji_id"] = icon_custom_emoji_id
                
            result = await bot.edit_forum_topic(**params)
            
            if result:
                # Update cache
                if (chat_id in self.topic_cache and 
                    message_thread_id in self.topic_cache[chat_id]):
                    if name:
                        self.topic_cache[chat_id][message_thread_id]["name"] = name
                    if icon_custom_emoji_id:
                        self.topic_cache[chat_id][message_thread_id]["icon_custom_emoji_id"] = icon_custom_emoji_id
                
                logger.info(f"Topic {message_thread_id} edited in chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to edit topic: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error editing topic: {e}")
            return False
            
    async def close_topic(
        self,
        bot: Any,
        chat_id: int,
        message_thread_id: int
    ) -> bool:
        """
        Close a forum topic.
        
        Args:
            bot (Bot): Bot instance
            chat_id (int): Chat ID
            message_thread_id (int): Message thread ID
            
        Returns:
            bool: True if topic was closed
        """
        try:
            result = await bot.close_forum_topic(
                chat_id=chat_id,
                message_thread_id=message_thread_id
            )
            
            if result:
                # Update cache
                if (chat_id in self.topic_cache and 
                    message_thread_id in self.topic_cache[chat_id]):
                    self.topic_cache[chat_id][message_thread_id]["is_closed"] = True
                
                logger.info(f"Topic {message_thread_id} closed in chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to close topic: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing topic: {e}")
            return False
            
    async def reopen_topic(
        self,
        bot: Any,
        chat_id: int,
        message_thread_id: int
    ) -> bool:
        """
        Reopen a forum topic.
        
        Args:
            bot (Bot): Bot instance
            chat_id (int): Chat ID
            message_thread_id (int): Message thread ID
            
        Returns:
            bool: True if topic was reopened
        """
        try:
            result = await bot.reopen_forum_topic(
                chat_id=chat_id,
                message_thread_id=message_thread_id
            )
            
            if result:
                # Update cache
                if (chat_id in self.topic_cache and 
                    message_thread_id in self.topic_cache[chat_id]):
                    self.topic_cache[chat_id][message_thread_id]["is_closed"] = False
                
                logger.info(f"Topic {message_thread_id} reopened in chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to reopen topic: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error reopening topic: {e}")
            return False
            
    async def delete_topic(
        self,
        bot: Any,
        chat_id: int,
        message_thread_id: int
    ) -> bool:
        """
        Delete a forum topic.
        
        Args:
            bot (Bot): Bot instance
            chat_id (int): Chat ID
            message_thread_id (int): Message thread ID
            
        Returns:
            bool: True if topic was deleted
        """
        try:
            result = await bot.delete_forum_topic(
                chat_id=chat_id,
                message_thread_id=message_thread_id
            )
            
            if result:
                # Update cache
                if (chat_id in self.topic_cache and 
                    message_thread_id in self.topic_cache[chat_id]):
                    del self.topic_cache[chat_id][message_thread_id]
                
                logger.info(f"Topic {message_thread_id} deleted in chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to delete topic: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting topic: {e}")
            return False
            
    async def get_forum_topics(
        self,
        bot: Any,
        chat_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all forum topics in a chat.
        
        Args:
            bot (Bot): Bot instance
            chat_id (int): Chat ID
            
        Returns:
            List[Dict[str, Any]]: List of topics
        """
        try:
            result = await bot.get_forum_topics(chat_id=chat_id)
            
            if result and "topics" in result:
                # Update cache
                if chat_id not in self.topic_cache:
                    self.topic_cache[chat_id] = {}
                    
                for topic in result["topics"]:
                    if "message_thread_id" in topic:
                        self.topic_cache[chat_id][topic["message_thread_id"]] = topic
                
                return result["topics"]
            else:
                logger.error(f"Failed to get forum topics: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting forum topics: {e}")
            return []
            
    def create_topic_keyboard(
        self,
        chat_id: int,
        topics: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a keyboard for topic selection.
        
        Args:
            chat_id (int): Chat ID
            topics (Optional[List[Dict[str, Any]]]): List of topics
            
        Returns:
            Dict[str, Any]: Keyboard markup
        """
        builder = KeyboardBuilder()
        
        # Use provided topics or cached topics
        topic_list = topics
        if not topic_list and chat_id in self.topic_cache:
            topic_list = list(self.topic_cache[chat_id].values())
            
        if not topic_list:
            return builder.add_button(
                text="No topics available"
            ).build().to_dict()
            
        # Add topics to keyboard
        for topic in topic_list:
            if "message_thread_id" in topic and "name" in topic:
                builder.add_button(
                    text=topic["name"],
                    callback_data=f"topic_{chat_id}_{topic['message_thread_id']}"
                )
                builder.new_row()
                
        return builder.build().to_dict()
        
    def is_topic_message(self, message: Message) -> bool:
        """
        Check if a message is from a forum topic.
        
        Args:
            message (Message): Message to check
            
        Returns:
            bool: True if message is from a forum topic
        """
        return hasattr(message, "message_thread_id") and message.message_thread_id is not None 