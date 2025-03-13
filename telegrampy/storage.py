"""
Storage backends for FSM and other data.
"""
from typing import Any, Dict, Optional, Tuple, Union
import json
import aioredis
from .fsm import State

class BaseStorage:
    """
    Base class for storage backends.
    
    Attributes:
        prefix (str): Key prefix for storage
    """
    
    def __init__(self, prefix: str = "telegrampy"):
        """
        Initialize the storage.
        
        Args:
            prefix (str): Key prefix
        """
        self.prefix = prefix
        
    def _get_key(self, *parts: str) -> str:
        """
        Get a storage key.
        
        Args:
            *parts: Key parts
            
        Returns:
            str: Full key
        """
        return f"{self.prefix}:{':'.join(parts)}"
        
    async def get_state(
        self,
        user_id: int,
        chat_id: int
    ) -> Optional[Tuple[Optional[State], Dict[str, Any]]]:
        """
        Get FSM state and data.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
            
        Returns:
            Optional[Tuple[Optional[State], Dict[str, Any]]]: State and data
        """
        raise NotImplementedError
        
    async def set_state(
        self,
        user_id: int,
        chat_id: int,
        state: Optional[State]
    ) -> None:
        """
        Set FSM state.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
            state (Optional[State]): New state
        """
        raise NotImplementedError
        
    async def set_data(
        self,
        user_id: int,
        chat_id: int,
        data: Dict[str, Any]
    ) -> None:
        """
        Set FSM data.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
            data (Dict[str, Any]): New data
        """
        raise NotImplementedError
        
    async def clear(self, user_id: int, chat_id: int) -> None:
        """
        Clear FSM state and data.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
        """
        raise NotImplementedError

class RedisStorage(BaseStorage):
    """
    Redis storage backend.
    
    Attributes:
        redis (aioredis.Redis): Redis client
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost",
        prefix: str = "telegrampy"
    ):
        """
        Initialize Redis storage.
        
        Args:
            redis_url (str): Redis URL
            prefix (str): Key prefix
        """
        super().__init__(prefix)
        self.redis = aioredis.from_url(redis_url)
        
    async def get_state(
        self,
        user_id: int,
        chat_id: int
    ) -> Optional[Tuple[Optional[State], Dict[str, Any]]]:
        """
        Get FSM state and data from Redis.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
            
        Returns:
            Optional[Tuple[Optional[State], Dict[str, Any]]]: State and data
        """
        key = self._get_key("fsm", str(user_id), str(chat_id))
        data = await self.redis.get(key)
        if data:
            state_data = json.loads(data)
            state = State(state_data["state"]) if state_data["state"] else None
            return state, state_data["data"]
        return None
        
    async def set_state(
        self,
        user_id: int,
        chat_id: int,
        state: Optional[State]
    ) -> None:
        """
        Set FSM state in Redis.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
            state (Optional[State]): New state
        """
        key = self._get_key("fsm", str(user_id), str(chat_id))
        data = await self.redis.get(key)
        if data:
            state_data = json.loads(data)
            state_data["state"] = state.value if state else None
            await self.redis.set(key, json.dumps(state_data))
        else:
            await self.redis.set(
                key,
                json.dumps({"state": state.value if state else None, "data": {}})
            )
            
    async def set_data(
        self,
        user_id: int,
        chat_id: int,
        data: Dict[str, Any]
    ) -> None:
        """
        Set FSM data in Redis.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
            data (Dict[str, Any]): New data
        """
        key = self._get_key("fsm", str(user_id), str(chat_id))
        state_data = await self.redis.get(key)
        if state_data:
            state_data = json.loads(state_data)
            state_data["data"] = data
            await self.redis.set(key, json.dumps(state_data))
        else:
            await self.redis.set(
                key,
                json.dumps({"state": None, "data": data})
            )
            
    async def clear(self, user_id: int, chat_id: int) -> None:
        """
        Clear FSM state and data from Redis.
        
        Args:
            user_id (int): User ID
            chat_id (int): Chat ID
        """
        key = self._get_key("fsm", str(user_id), str(chat_id))
        await self.redis.delete(key)
        
    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close() 