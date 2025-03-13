"""
Middleware system for processing updates.
"""
from typing import Any, Callable, Dict, Optional
from .types import Update

class BaseMiddleware:
    """
    Base class for all middlewares.
    
    Attributes:
        handler (Callable): The handler function
    """
    
    def __init__(self, handler: Callable):
        """
        Initialize the middleware.
        
        Args:
            handler (Callable): The handler function
        """
        self.handler = handler
        
    async def process_update(self, update: Update) -> None:
        """
        Process an update.
        
        Args:
            update (Update): The update to process
        """
        await self.handler(update)

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging updates."""
    
    async def process_update(self, update: Update) -> None:
        """
        Log the update before processing.
        
        Args:
            update (Update): The update to process
        """
        print(f"Processing update: {update}")
        await super().process_update(update)

class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for throttling updates.
    
    Attributes:
        rate_limit (float): Rate limit in seconds
        last_update (Dict[str, float]): Last update timestamps
    """
    
    def __init__(self, handler: Callable, rate_limit: float = 1.0):
        """
        Initialize the throttling middleware.
        
        Args:
            handler (Callable): The handler function
            rate_limit (float): Rate limit in seconds
        """
        super().__init__(handler)
        self.rate_limit = rate_limit
        self.last_update: Dict[str, float] = {}
        
    async def process_update(self, update: Update) -> None:
        """
        Process an update with rate limiting.
        
        Args:
            update (Update): The update to process
        """
        user_id = str(update.from_user.id) if update.from_user else "unknown"
        current_time = update.date
        
        if user_id in self.last_update:
            time_diff = current_time - self.last_update[user_id]
            if time_diff < self.rate_limit:
                return
                
        self.last_update[user_id] = current_time
        await super().process_update(update)

class AuthMiddleware(BaseMiddleware):
    """
    Middleware for user authentication.
    
    Attributes:
        allowed_users (set[int]): Set of allowed user IDs
    """
    
    def __init__(
        self,
        handler: Callable,
        allowed_users: Optional[set[int]] = None
    ):
        """
        Initialize the auth middleware.
        
        Args:
            handler (Callable): The handler function
            allowed_users (Optional[set[int]]): Set of allowed user IDs
        """
        super().__init__(handler)
        self.allowed_users = allowed_users or set()
        
    async def process_update(self, update: Update) -> None:
        """
        Process an update with authentication.
        
        Args:
            update (Update): The update to process
        """
        if not update.from_user:
            return
            
        if self.allowed_users and update.from_user.id not in self.allowed_users:
            return
            
        await super().process_update(update)

class ErrorHandlingMiddleware(BaseMiddleware):
    """Middleware for handling errors."""
    
    async def process_update(self, update: Update) -> None:
        """
        Process an update with error handling.
        
        Args:
            update (Update): The update to process
        """
        try:
            await super().process_update(update)
        except Exception as e:
            print(f"Error processing update: {e}")
            # Here you could implement error reporting or recovery

class MetricsMiddleware(BaseMiddleware):
    """
    Middleware for collecting metrics.
    
    Attributes:
        metrics (Dict[str, int]): Collected metrics
    """
    
    def __init__(self, handler: Callable):
        """
        Initialize the metrics middleware.
        
        Args:
            handler (Callable): The handler function
        """
        super().__init__(handler)
        self.metrics: Dict[str, int] = {
            "total_updates": 0,
            "messages": 0,
            "callback_queries": 0,
            "errors": 0
        }
        
    async def process_update(self, update: Update) -> None:
        """
        Process an update and collect metrics.
        
        Args:
            update (Update): The update to process
        """
        self.metrics["total_updates"] += 1
        
        if update.message:
            self.metrics["messages"] += 1
        if update.callback_query:
            self.metrics["callback_queries"] += 1
            
        try:
            await super().process_update(update)
        except Exception:
            self.metrics["errors"] += 1
            raise 