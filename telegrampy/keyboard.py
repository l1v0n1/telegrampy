"""
Keyboard builder module for creating custom keyboards.
"""
from typing import List, Dict, Any, Optional, Union
from .types import Message

class KeyboardButton:
    """
    Base class for keyboard buttons.
    
    Attributes:
        text (str): Button text
        **kwargs: Additional button parameters
    """
    
    def __init__(self, text: str, **kwargs):
        """
        Initialize the button.
        
        Args:
            text (str): Button text
            **kwargs: Additional button parameters
        """
        self.text = text
        self.params = kwargs
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert button to dictionary.
        
        Returns:
            Dict[str, Any]: Button data
        """
        data = {"text": self.text}
        data.update(self.params)
        return data

class InlineKeyboardButton(KeyboardButton):
    """Button for inline keyboards."""
    
    def __init__(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        web_app: Optional[Dict[str, Any]] = None,
        login_url: Optional[Dict[str, Any]] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        callback_game: Optional[Dict[str, Any]] = None,
        pay: bool = False
    ):
        """
        Initialize the inline button.
        
        Args:
            text (str): Button text
            callback_data (Optional[str]): Callback data
            url (Optional[str]): URL to open
            web_app (Optional[Dict[str, Any]]): Web app data
            login_url (Optional[Dict[str, Any]]): Login URL data
            switch_inline_query (Optional[str]): Inline query to switch to
            switch_inline_query_current_chat (Optional[str]): Inline query for current chat
            callback_game (Optional[Dict[str, Any]]): Callback game data
            pay (bool): Whether this is a pay button
        """
        params = {}
        if callback_data:
            params["callback_data"] = callback_data
        if url:
            params["url"] = url
        if web_app:
            params["web_app"] = web_app
        if login_url:
            params["login_url"] = login_url
        if switch_inline_query:
            params["switch_inline_query"] = switch_inline_query
        if switch_inline_query_current_chat:
            params["switch_inline_query_current_chat"] = switch_inline_query_current_chat
        if callback_game:
            params["callback_game"] = callback_game
        if pay:
            params["pay"] = pay
            
        super().__init__(text, **params)

class KeyboardMarkup:
    """Base class for keyboard markups."""
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert markup to dictionary.
        
        Returns:
            Dict[str, Any]: Markup data
        """
        raise NotImplementedError

class ReplyKeyboardMarkup(KeyboardMarkup):
    """
    Reply keyboard markup.
    
    Attributes:
        keyboard (List[List[KeyboardButton]]): Keyboard buttons
        resize_keyboard (bool): Whether to resize keyboard
        one_time_keyboard (bool): Whether keyboard should be hidden after use
        selective (bool): Whether keyboard is selective
        input_field_placeholder (Optional[str]): Placeholder for input field
    """
    
    def __init__(
        self,
        keyboard: List[List[KeyboardButton]],
        resize_keyboard: bool = False,
        one_time_keyboard: bool = False,
        selective: bool = False,
        input_field_placeholder: Optional[str] = None
    ):
        """
        Initialize the reply keyboard markup.
        
        Args:
            keyboard (List[List[KeyboardButton]]): Keyboard buttons
            resize_keyboard (bool): Whether to resize keyboard
            one_time_keyboard (bool): Whether keyboard should be hidden after use
            selective (bool): Whether keyboard is selective
            input_field_placeholder (Optional[str]): Placeholder for input field
        """
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective
        self.input_field_placeholder = input_field_placeholder
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert markup to dictionary.
        
        Returns:
            Dict[str, Any]: Markup data
        """
        data = {
            "keyboard": [[btn.to_dict() for btn in row] for row in self.keyboard],
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard,
            "selective": self.selective
        }
        if self.input_field_placeholder:
            data["input_field_placeholder"] = self.input_field_placeholder
        return data

class InlineKeyboardMarkup(KeyboardMarkup):
    """
    Inline keyboard markup.
    
    Attributes:
        inline_keyboard (List[List[InlineKeyboardButton]]): Inline keyboard buttons
    """
    
    def __init__(self, inline_keyboard: List[List[InlineKeyboardButton]]):
        """
        Initialize the inline keyboard markup.
        
        Args:
            inline_keyboard (List[List[InlineKeyboardButton]]): Inline keyboard buttons
        """
        self.inline_keyboard = inline_keyboard
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert markup to dictionary.
        
        Returns:
            Dict[str, Any]: Markup data
        """
        return {
            "inline_keyboard": [[btn.to_dict() for btn in row] for row in self.inline_keyboard]
        }

class KeyboardBuilder:
    """
    Builder for creating keyboard markups.
    
    Attributes:
        keyboard (List[List[KeyboardButton]]): Current keyboard buttons
        inline_keyboard (List[List[InlineKeyboardButton]]): Current inline keyboard buttons
    """
    
    def __init__(self):
        """Initialize the keyboard builder."""
        self.keyboard: List[List[KeyboardButton]] = []
        self.inline_keyboard: List[List[InlineKeyboardButton]] = []
        
    def add_button(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs
    ) -> "KeyboardBuilder":
        """
        Add a button to the current row.
        
        Args:
            text (str): Button text
            callback_data (Optional[str]): Callback data
            url (Optional[str]): URL to open
            **kwargs: Additional button parameters
            
        Returns:
            KeyboardBuilder: Self for chaining
        """
        if callback_data or url:
            button = InlineKeyboardButton(text, callback_data, url, **kwargs)
            if not self.inline_keyboard:
                self.inline_keyboard.append([])
            self.inline_keyboard[-1].append(button)
        else:
            button = KeyboardButton(text, **kwargs)
            if not self.keyboard:
                self.keyboard.append([])
            self.keyboard[-1].append(button)
        return self
        
    def row(self) -> "KeyboardBuilder":
        """
        Start a new row.
        
        Returns:
            KeyboardBuilder: Self for chaining
        """
        self.keyboard.append([])
        self.inline_keyboard.append([])
        return self
        
    def build(self) -> Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]:
        """
        Build the keyboard markup.
        
        Returns:
            Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]: Built markup
        """
        if self.inline_keyboard:
            return InlineKeyboardMarkup(self.inline_keyboard)
        return ReplyKeyboardMarkup(self.keyboard)
        
    @classmethod
    def create_inline(
        cls,
        *buttons: List[InlineKeyboardButton]
    ) -> InlineKeyboardMarkup:
        """
        Create an inline keyboard markup.
        
        Args:
            *buttons: Button rows
            
        Returns:
            InlineKeyboardMarkup: Created markup
        """
        return InlineKeyboardMarkup(list(buttons))
        
    @classmethod
    def create_reply(
        cls,
        *buttons: List[KeyboardButton]
    ) -> ReplyKeyboardMarkup:
        """
        Create a reply keyboard markup.
        
        Args:
            *buttons: Button rows
            
        Returns:
            ReplyKeyboardMarkup: Created markup
        """
        return ReplyKeyboardMarkup(list(buttons)) 