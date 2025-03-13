"""
Finite State Machine implementation for conversation handling.
"""
from typing import Any, Dict, Optional, Type, TypeVar
from enum import Enum
from .storage import BaseStorage
from .types import Message

T = TypeVar("T")

class State(str, Enum):
    """Base class for FSM states."""
    pass

class FSMContext:
    """
    Context for managing FSM state and data.
    
    Attributes:
        storage (BaseStorage): Storage backend for FSM data
        user_id (int): User ID
        chat_id (int): Chat ID
        state (Optional[State]): Current state
        data (Dict[str, Any]): State data
    """
    
    def __init__(
        self,
        storage: BaseStorage,
        user_id: int,
        chat_id: int,
        state: Optional[State] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the FSM context.
        
        Args:
            storage (BaseStorage): Storage backend
            user_id (int): User ID
            chat_id (int): Chat ID
            state (Optional[State]): Initial state
            data (Optional[Dict[str, Any]]): Initial data
        """
        self.storage = storage
        self.user_id = user_id
        self.chat_id = chat_id
        self.state = state
        self.data = data or {}
        
    @classmethod
    async def get(
        cls,
        storage: BaseStorage,
        user_id: int,
        chat_id: int
    ) -> "FSMContext":
        """
        Get or create an FSM context.
        
        Args:
            storage (BaseStorage): Storage backend
            user_id (int): User ID
            chat_id (int): Chat ID
            
        Returns:
            FSMContext: The FSM context
        """
        data = await storage.get_state(user_id, chat_id)
        if data:
            state, context_data = data
            return cls(storage, user_id, chat_id, state, context_data)
        return cls(storage, user_id, chat_id)
        
    async def set_state(self, state: Optional[State]) -> None:
        """
        Set the current state.
        
        Args:
            state (Optional[State]): New state
        """
        self.state = state
        await self.storage.set_state(self.user_id, self.chat_id, state)
        
    async def update_data(self, **kwargs) -> None:
        """
        Update state data.
        
        Args:
            **kwargs: Data to update
        """
        self.data.update(kwargs)
        await self.storage.set_data(self.user_id, self.chat_id, self.data)
        
    async def get_data(self) -> Dict[str, Any]:
        """
        Get state data.
        
        Returns:
            Dict[str, Any]: State data
        """
        return self.data
        
    async def clear(self) -> None:
        """Clear state and data."""
        self.state = None
        self.data = {}
        await self.storage.clear(self.user_id, self.chat_id)
        
    async def set(self, key: str, value: Any) -> None:
        """
        Set a data value.
        
        Args:
            key (str): Data key
            value (Any): Data value
        """
        self.data[key] = value
        await self.storage.set_data(self.user_id, self.chat_id, self.data)
        
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a data value.
        
        Args:
            key (str): Data key
            default (Any): Default value
            
        Returns:
            Any: Data value
        """
        return self.data.get(key, default)
        
    async def finish(self) -> None:
        """Finish the FSM and clear all data."""
        await self.clear()

class StateGroup:
    """
    Group of related states.
    
    Attributes:
        states (Dict[str, State]): States in the group
    """
    
    def __init__(self, **states: State):
        """
        Initialize the state group.
        
        Args:
            **states: States to include
        """
        self.states = states
        
    def __getattr__(self, name: str) -> State:
        """
        Get a state by name.
        
        Args:
            name (str): State name
            
        Returns:
            State: The state
            
        Raises:
            AttributeError: If state not found
        """
        if name in self.states:
            return self.states[name]
        raise AttributeError(f"State {name} not found in group")
        
    def __iter__(self):
        """Iterate over states."""
        return iter(self.states.values())
        
    def __contains__(self, state: State) -> bool:
        """
        Check if state is in group.
        
        Args:
            state (State): State to check
            
        Returns:
            bool: True if state is in group
        """
        return state in self.states.values() 