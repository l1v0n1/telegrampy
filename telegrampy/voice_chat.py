"""
Voice chat moderation module for Telegram bots.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .types import Message, ChatMember
from .keyboard import KeyboardBuilder

logger = logging.getLogger(__name__)

class VoiceChatHandler:
    """
    Handler for voice chat moderation.
    
    Attributes:
        max_participants (int): Maximum number of participants
        mute_timeout (int): Timeout for temporary mutes in minutes
        warn_threshold (int): Number of warnings before action
        banned_words (List[str]): List of banned words
        moderators (List[int]): List of moderator user IDs
    """
    
    def __init__(
        self,
        max_participants: int = 100,
        mute_timeout: int = 5,
        warn_threshold: int = 3,
        banned_words: Optional[List[str]] = None,
        moderators: Optional[List[int]] = None
    ):
        """
        Initialize the voice chat handler.
        
        Args:
            max_participants (int): Maximum number of participants
            mute_timeout (int): Timeout for temporary mutes in minutes
            warn_threshold (int): Number of warnings before action
            banned_words (Optional[List[str]]): List of banned words
            moderators (Optional[List[int]]): List of moderator user IDs
        """
        self.max_participants = max_participants
        self.mute_timeout = mute_timeout
        self.warn_threshold = warn_threshold
        self.banned_words = banned_words or []
        self.moderators = moderators or []
        
        # State tracking
        self.active_chats: Dict[int, Dict[str, Any]] = {}
        self.user_warnings: Dict[int, Dict[int, int]] = {}
        self.muted_users: Dict[int, Dict[int, datetime]] = {}
        
    def is_moderator(self, user_id: int) -> bool:
        """
        Check if a user is a moderator.
        
        Args:
            user_id (int): User ID to check
            
        Returns:
            bool: True if user is a moderator
        """
        return user_id in self.moderators
        
    def add_moderator(self, user_id: int) -> None:
        """
        Add a user as a moderator.
        
        Args:
            user_id (int): User ID to add
        """
        if user_id not in self.moderators:
            self.moderators.append(user_id)
            
    def remove_moderator(self, user_id: int) -> None:
        """
        Remove a user from moderators.
        
        Args:
            user_id (int): User ID to remove
        """
        if user_id in self.moderators:
            self.moderators.remove(user_id)
            
    def add_banned_word(self, word: str) -> None:
        """
        Add a word to the banned words list.
        
        Args:
            word (str): Word to add
        """
        if word not in self.banned_words:
            self.banned_words.append(word.lower())
            
    def remove_banned_word(self, word: str) -> None:
        """
        Remove a word from the banned words list.
        
        Args:
            word (str): Word to remove
        """
        if word.lower() in self.banned_words:
            self.banned_words.remove(word.lower())
            
    def check_banned_words(self, text: str) -> bool:
        """
        Check if text contains banned words.
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if text contains banned words
        """
        text = text.lower()
        return any(word in text for word in self.banned_words)
        
    async def handle_voice_chat_started(
        self,
        message: Message
    ) -> None:
        """
        Handle voice chat started event.
        
        Args:
            message (Message): Message containing voice chat info
        """
        chat_id = message.chat.id
        self.active_chats[chat_id] = {
            "started_at": datetime.now(),
            "participants": set(),
            "is_active": True
        }
        logger.info(f"Voice chat started in chat {chat_id}")
        
    async def handle_voice_chat_ended(
        self,
        message: Message
    ) -> None:
        """
        Handle voice chat ended event.
        
        Args:
            message (Message): Message containing voice chat info
        """
        chat_id = message.chat.id
        if chat_id in self.active_chats:
            self.active_chats[chat_id]["is_active"] = False
            self.active_chats[chat_id]["ended_at"] = datetime.now()
            logger.info(f"Voice chat ended in chat {chat_id}")
            
    async def handle_participant_joined(
        self,
        message: Message,
        user_id: int
    ) -> None:
        """
        Handle participant joined event.
        
        Args:
            message (Message): Message containing participant info
            user_id (int): User ID of participant
        """
        chat_id = message.chat.id
        if chat_id in self.active_chats:
            self.active_chats[chat_id]["participants"].add(user_id)
            logger.info(f"User {user_id} joined voice chat in chat {chat_id}")
            
    async def handle_participant_left(
        self,
        message: Message,
        user_id: int
    ) -> None:
        """
        Handle participant left event.
        
        Args:
            message (Message): Message containing participant info
            user_id (int): User ID of participant
        """
        chat_id = message.chat.id
        if chat_id in self.active_chats:
            self.active_chats[chat_id]["participants"].discard(user_id)
            logger.info(f"User {user_id} left voice chat in chat {chat_id}")
            
    async def mute_user(
        self,
        chat_id: int,
        user_id: int,
        duration: Optional[int] = None
    ) -> bool:
        """
        Mute a user in voice chat.
        
        Args:
            chat_id (int): Chat ID
            user_id (int): User ID to mute
            duration (Optional[int]): Mute duration in minutes
            
        Returns:
            bool: True if user was muted
        """
        try:
            duration = duration or self.mute_timeout
            mute_until = datetime.now() + timedelta(minutes=duration)
            self.muted_users[chat_id] = self.muted_users.get(chat_id, {})
            self.muted_users[chat_id][user_id] = mute_until
            logger.info(f"User {user_id} muted in chat {chat_id} until {mute_until}")
            return True
        except Exception as e:
            logger.error(f"Error muting user: {e}")
            return False
            
    async def unmute_user(
        self,
        chat_id: int,
        user_id: int
    ) -> bool:
        """
        Unmute a user in voice chat.
        
        Args:
            chat_id (int): Chat ID
            user_id (int): User ID to unmute
            
        Returns:
            bool: True if user was unmuted
        """
        try:
            if chat_id in self.muted_users and user_id in self.muted_users[chat_id]:
                del self.muted_users[chat_id][user_id]
                logger.info(f"User {user_id} unmuted in chat {chat_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unmuting user: {e}")
            return False
            
    async def warn_user(
        self,
        chat_id: int,
        user_id: int
    ) -> int:
        """
        Warn a user.
        
        Args:
            chat_id (int): Chat ID
            user_id (int): User ID to warn
            
        Returns:
            int: Number of warnings
        """
        if chat_id not in self.user_warnings:
            self.user_warnings[chat_id] = {}
            
        self.user_warnings[chat_id][user_id] = self.user_warnings[chat_id].get(user_id, 0) + 1
        warnings = self.user_warnings[chat_id][user_id]
        
        logger.info(f"User {user_id} warned in chat {chat_id} ({warnings}/{self.warn_threshold})")
        return warnings
        
    async def clear_warnings(
        self,
        chat_id: int,
        user_id: int
    ) -> None:
        """
        Clear warnings for a user.
        
        Args:
            chat_id (int): Chat ID
            user_id (int): User ID to clear warnings for
        """
        if chat_id in self.user_warnings and user_id in self.user_warnings[chat_id]:
            del self.user_warnings[chat_id][user_id]
            logger.info(f"Warnings cleared for user {user_id} in chat {chat_id}")
            
    def create_moderation_keyboard(
        self,
        chat_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Create a moderation keyboard.
        
        Args:
            chat_id (int): Chat ID
            user_id (int): User ID to moderate
            
        Returns:
            Dict[str, Any]: Keyboard markup
        """
        builder = KeyboardBuilder()
        
        # Add mute button
        builder.add_button(
            text="🔇 Mute",
            callback_data=f"mute_{chat_id}_{user_id}"
        )
        
        # Add unmute button if user is muted
        if chat_id in self.muted_users and user_id in self.muted_users[chat_id]:
            builder.add_button(
                text="🔊 Unmute",
                callback_data=f"unmute_{chat_id}_{user_id}"
            )
            
        # Add warn button
        builder.add_button(
            text="⚠️ Warn",
            callback_data=f"warn_{chat_id}_{user_id}"
        )
        
        # Add clear warnings button if user has warnings
        if chat_id in self.user_warnings and user_id in self.user_warnings[chat_id]:
            builder.add_button(
                text="🗑 Clear Warnings",
                callback_data=f"clear_warnings_{chat_id}_{user_id}"
            )
            
        return builder.build().to_dict()
        
    def get_voice_chat_stats(
        self,
        chat_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get voice chat statistics.
        
        Args:
            chat_id (int): Chat ID
            
        Returns:
            Optional[Dict[str, Any]]: Voice chat statistics
        """
        if chat_id not in self.active_chats:
            return None
            
        chat_data = self.active_chats[chat_id]
        return {
            "is_active": chat_data["is_active"],
            "started_at": chat_data["started_at"],
            "ended_at": chat_data.get("ended_at"),
            "participants": len(chat_data["participants"]),
            "muted_users": len(self.muted_users.get(chat_id, {})),
            "warned_users": len(self.user_warnings.get(chat_id, {}))
        } 