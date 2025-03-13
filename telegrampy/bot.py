"""
Core Bot class for handling Telegram API interactions.
"""
from typing import Optional, Dict, Any, Union
import aiohttp
import logging
from .types import Update, Message, CallbackQuery
from .storage import BaseStorage

logger = logging.getLogger(__name__)

class Bot:
    """
    Main bot class for handling Telegram API interactions.
    
    Attributes:
        token (str): The bot's authentication token
        session (aiohttp.ClientSession): The aiohttp session for making requests
        storage (BaseStorage): Storage backend for bot data
    """
    
    def __init__(
        self,
        token: str,
        storage: Optional[BaseStorage] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the bot with the given token and optional storage.
        
        Args:
            token (str): The bot's authentication token
            storage (Optional[BaseStorage]): Storage backend for bot data
            session (Optional[aiohttp.ClientSession]): Custom aiohttp session
        """
        self.token = token
        self.storage = storage
        self._session = session
        self._base_url = f"https://api.telegram.org/bot{token}"
        
    async def __aenter__(self):
        """Async context manager entry."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            
    async def _request(
        self,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Telegram API.
        
        Args:
            method (str): API method name
            data (Optional[Dict[str, Any]]): Request data
            files (Optional[Dict[str, Any]]): Files to upload
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            aiohttp.ClientError: If the request fails
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
            
        url = f"{self._base_url}/{method}"
        async with self._session.post(url, data=data, files=files) as response:
            response.raise_for_status()
            return await response.json()
            
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information."""
        return await self._request("getMe")
        
    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        **kwargs
    ) -> Message:
        """
        Send a message to a chat.
        
        Args:
            chat_id (Union[int, str]): Target chat ID
            text (str): Message text
            **kwargs: Additional message parameters
            
        Returns:
            Message: The sent message
        """
        data = {"chat_id": chat_id, "text": text, **kwargs}
        response = await self._request("sendMessage", data=data)
        return Message(**response["result"])
        
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Answer a callback query.
        
        Args:
            callback_query_id (str): ID of the callback query
            text (Optional[str]): Answer text
            **kwargs: Additional answer parameters
            
        Returns:
            bool: True if successful
        """
        data = {"callback_query_id": callback_query_id}
        if text:
            data["text"] = text
        data.update(kwargs)
        response = await self._request("answerCallbackQuery", data=data)
        return response["result"]
        
    async def set_webhook(
        self,
        url: str,
        **kwargs
    ) -> bool:
        """
        Set webhook for receiving updates.
        
        Args:
            url (str): Webhook URL
            **kwargs: Additional webhook parameters
            
        Returns:
            bool: True if successful
        """
        data = {"url": url, **kwargs}
        response = await self._request("setWebhook", data=data)
        return response["result"]
        
    async def delete_webhook(self) -> bool:
        """
        Delete the webhook.
        
        Returns:
            bool: True if successful
        """
        response = await self._request("deleteWebhook")
        return response["result"] 