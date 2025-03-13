"""
Dispatcher class for handling message routing and processing.
"""
from typing import Dict, List, Any, Callable, Optional, Union
import asyncio
import logging
from .bot import Bot
from .types import Update, Message, CallbackQuery
from .filters import Filter
from .middleware import BaseMiddleware
from .fsm import FSMContext, State

logger = logging.getLogger(__name__)

class Dispatcher:
    """
    Dispatcher class for handling message routing and processing.
    
    Attributes:
        bot (Bot): The bot instance
        handlers (Dict[str, List[Dict[str, Any]]]): Registered message handlers
        middlewares (List[BaseMiddleware]): Registered middlewares
        fsm_contexts (Dict[str, FSMContext]): Active FSM contexts
    """
    
    def __init__(self, bot: Bot):
        """
        Initialize the dispatcher with a bot instance.
        
        Args:
            bot (Bot): The bot instance
        """
        self.bot = bot
        self.handlers: Dict[str, List[Dict[str, Any]]] = {}
        self.middlewares: List[BaseMiddleware] = []
        self.fsm_contexts: Dict[str, FSMContext] = {}
        
    def register_handler(
        self,
        handler: Callable,
        filters: Optional[Filter] = None,
        state: Optional[State] = None
    ) -> None:
        """
        Register a message handler.
        
        Args:
            handler (Callable): The handler function
            filters (Optional[Filter]): Message filters
            state (Optional[State]): Required state for the handler
        """
        handler_type = "message"
        if not self.handlers.get(handler_type):
            self.handlers[handler_type] = []
            
        self.handlers[handler_type].append({
            "handler": handler,
            "filters": filters,
            "state": state
        })
        
    def register_callback_handler(
        self,
        handler: Callable,
        filters: Optional[Filter] = None
    ) -> None:
        """
        Register a callback query handler.
        
        Args:
            handler (Callable): The handler function
            filters (Optional[Filter]): Callback query filters
        """
        handler_type = "callback_query"
        if not self.handlers.get(handler_type):
            self.handlers[handler_type] = []
            
        self.handlers[handler_type].append({
            "handler": handler,
            "filters": filters
        })
        
    def register_middleware(self, middleware: BaseMiddleware) -> None:
        """
        Register a middleware.
        
        Args:
            middleware (BaseMiddleware): The middleware to register
        """
        self.middlewares.append(middleware)
        
    async def process_update(self, update: Update) -> None:
        """
        Process an incoming update.
        
        Args:
            update (Update): The update to process
        """
        # Process through middlewares
        for middleware in self.middlewares:
            await middleware.process_update(update)
            
        # Handle message updates
        if update.message:
            await self._process_message(update.message)
            
        # Handle callback queries
        if update.callback_query:
            await self._process_callback_query(update.callback_query)
            
    async def _process_message(self, message: Message) -> None:
        """
        Process a message update.
        
        Args:
            message (Message): The message to process
        """
        handlers = self.handlers.get("message", [])
        for handler_data in handlers:
            handler = handler_data["handler"]
            filters = handler_data["filters"]
            state = handler_data["state"]
            
            # Check filters
            if filters and not await filters.check(message):
                continue
                
            # Check state
            if state:
                fsm_context = self.fsm_contexts.get(message.from_user.id)
                if not fsm_context or fsm_context.state != state:
                    continue
                    
            # Execute handler
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                
    async def _process_callback_query(self, callback_query: CallbackQuery) -> None:
        """
        Process a callback query update.
        
        Args:
            callback_query (CallbackQuery): The callback query to process
        """
        handlers = self.handlers.get("callback_query", [])
        for handler_data in handlers:
            handler = handler_data["handler"]
            filters = handler_data["filters"]
            
            # Check filters
            if filters and not await filters.check(callback_query):
                continue
                
            # Execute handler
            try:
                await handler(callback_query)
            except Exception as e:
                logger.error(f"Error in callback query handler: {e}")
                
    async def start_polling(self) -> None:
        """Start polling for updates."""
        while True:
            try:
                updates = await self.bot.get_updates()
                for update in updates:
                    await self.process_update(Update(**update))
            except Exception as e:
                logger.error(f"Error in polling: {e}")
            await asyncio.sleep(1) 