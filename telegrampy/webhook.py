"""
Webhook server implementation for Telegram bots.
"""
import asyncio
import logging
import ssl
from typing import Optional, Callable, Dict, Any
from aiohttp import web
from .types import Update
from .dispatcher import Dispatcher

logger = logging.getLogger(__name__)

class WebhookServer:
    """
    Webhook server for receiving Telegram updates.
    
    Attributes:
        app (web.Application): aiohttp web application
        dispatcher (Dispatcher): Update dispatcher
        host (str): Server host
        port (int): Server port
        ssl_context (Optional[ssl.SSLContext]): SSL context
        secret_token (Optional[str]): Secret token for webhook security
    """
    
    def __init__(
        self,
        dispatcher: Dispatcher,
        host: str = "0.0.0.0",
        port: int = 8443,
        ssl_context: Optional[ssl.SSLContext] = None,
        secret_token: Optional[str] = None
    ):
        """
        Initialize the webhook server.
        
        Args:
            dispatcher (Dispatcher): Update dispatcher
            host (str): Server host
            port (int): Server port
            ssl_context (Optional[ssl.SSLContext]): SSL context
            secret_token (Optional[str]): Secret token for webhook security
        """
        self.app = web.Application()
        self.dispatcher = dispatcher
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.secret_token = secret_token
        
        # Setup routes
        self.app.router.add_post("/webhook", self._handle_webhook)
        
    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """
        Handle incoming webhook requests.
        
        Args:
            request (web.Request): Incoming request
            
        Returns:
            web.Response: Response to send
        """
        # Verify secret token if set
        if self.secret_token:
            if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != self.secret_token:
                return web.Response(status=403, text="Invalid secret token")
                
        try:
            # Parse update data
            data = await request.json()
            update = Update(**data)
            
            # Process update
            await self.dispatcher.process_update(update)
            
            return web.Response(status=200, text="OK")
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return web.Response(status=500, text=str(e))
            
    async def start(self) -> None:
        """Start the webhook server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            self.host,
            self.port,
            ssl_context=self.ssl_context
        )
        await site.start()
        logger.info(f"Webhook server started on {self.host}:{self.port}")
        
    async def stop(self) -> None:
        """Stop the webhook server."""
        await self.app.shutdown()
        logger.info("Webhook server stopped") 