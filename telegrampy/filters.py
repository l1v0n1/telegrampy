"""
Filter system for message and callback query handling.
"""
from typing import Any, Callable, Optional, Union, Pattern
import re
from .types import Message, CallbackQuery

class Filter:
    """
    Base class for all filters.
    
    Attributes:
        func (Callable): The filter function
    """
    
    def __init__(self, func: Callable):
        """
        Initialize the filter with a function.
        
        Args:
            func (Callable): The filter function
        """
        self.func = func
        
    async def check(self, update: Union[Message, CallbackQuery]) -> bool:
        """
        Check if the update matches the filter.
        
        Args:
            update (Union[Message, CallbackQuery]): The update to check
            
        Returns:
            bool: True if the update matches the filter
        """
        return await self.func(update)

class Command(Filter):
    """Filter for command messages."""
    
    def __init__(self, command: Union[str, list[str]]):
        """
        Initialize the command filter.
        
        Args:
            command (Union[str, list[str]]): Command or list of commands to match
        """
        if isinstance(command, str):
            command = [command]
            
        async def check_command(update: Message) -> bool:
            if not update.text or not update.text.startswith("/"):
                return False
                
            cmd = update.text[1:].split()[0].lower()
            return cmd in [c.lower() for c in command]
            
        super().__init__(check_command)

class Text(Filter):
    """Filter for text messages."""
    
    def __init__(self, text: Union[str, Pattern[str]]):
        """
        Initialize the text filter.
        
        Args:
            text (Union[str, Pattern[str]]): Text or regex pattern to match
        """
        if isinstance(text, str):
            pattern = re.compile(f"^{text}$")
        else:
            pattern = text
            
        async def check_text(update: Message) -> bool:
            if not update.text:
                return False
            return bool(pattern.match(update.text))
            
        super().__init__(check_text)

class CallbackData(Filter):
    """Filter for callback queries with specific data."""
    
    def __init__(self, data: Union[str, Pattern[str]]):
        """
        Initialize the callback data filter.
        
        Args:
            data (Union[str, Pattern[str]]): Data or regex pattern to match
        """
        if isinstance(data, str):
            pattern = re.compile(f"^{data}$")
        else:
            pattern = data
            
        async def check_callback(update: CallbackQuery) -> bool:
            if not update.data:
                return False
            return bool(pattern.match(update.data))
            
        super().__init__(check_callback)

class State(Filter):
    """Filter for specific FSM states."""
    
    def __init__(self, state: str):
        """
        Initialize the state filter.
        
        Args:
            state (str): The state to match
        """
        self.state = state
        
        async def check_state(update: Message) -> bool:
            # This will be implemented in the FSM context
            return True
            
        super().__init__(check_state)

class ChatType(Filter):
    """Filter for specific chat types."""
    
    def __init__(self, chat_type: Union[str, list[str]]):
        """
        Initialize the chat type filter.
        
        Args:
            chat_type (Union[str, list[str]]): Chat type or list of types to match
        """
        if isinstance(chat_type, str):
            chat_type = [chat_type]
            
        async def check_chat_type(update: Message) -> bool:
            return update.chat.type in chat_type
            
        super().__init__(check_chat_type)

class UserID(Filter):
    """Filter for specific user IDs."""
    
    def __init__(self, user_id: Union[int, list[int]]):
        """
        Initialize the user ID filter.
        
        Args:
            user_id (Union[int, list[int]]): User ID or list of IDs to match
        """
        if isinstance(user_id, int):
            user_id = [user_id]
            
        async def check_user_id(update: Message) -> bool:
            if not update.from_user:
                return False
            return update.from_user.id in user_id
            
        super().__init__(check_user_id)

class ChatID(Filter):
    """Filter for specific chat IDs."""
    
    def __init__(self, chat_id: Union[int, list[int]]):
        """
        Initialize the chat ID filter.
        
        Args:
            chat_id (Union[int, list[int]]): Chat ID or list of IDs to match
        """
        if isinstance(chat_id, int):
            chat_id = [chat_id]
            
        async def check_chat_id(update: Message) -> bool:
            return update.chat.id in chat_id
            
        super().__init__(check_chat_id)

class MediaType(Filter):
    """Filter for specific media types."""
    
    def __init__(self, media_type: Union[str, list[str]]):
        """
        Initialize the media type filter.
        
        Args:
            media_type (Union[str, list[str]]): Media type or list of types to match
        """
        if isinstance(media_type, str):
            media_type = [media_type]
            
        async def check_media_type(update: Message) -> bool:
            for mt in media_type:
                if getattr(update, mt):
                    return True
            return False
            
        super().__init__(check_media_type) 