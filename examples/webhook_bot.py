#!/usr/bin/env python3
"""
Example bot demonstrating webhook usage with the TelegramPy framework.
"""
import asyncio
import logging
import os
import ssl
from aiohttp import web

from telegrampy import Bot, Dispatcher, WebhookServer
from telegrampy.types import Message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Webhook settings
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "example.com")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT", "cert.pem")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV", "privkey.pem")
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}/webhook"

# Secret token to validate webhook requests
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_token")

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    
    # Register message handlers
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: Message):
        """Handle /start command."""
        await message.reply(
            "Welcome to the TelegramPy Webhook Demo Bot!\n"
            "This bot demonstrates webhook functionality of the TelegramPy framework."
        )
    
    @dp.message_handler(commands=["help"])
    async def cmd_help(message: Message):
        """Handle /help command."""
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/webhook - Get webhook info"
        )
        await message.reply(help_text)
    
    @dp.message_handler(commands=["webhook"])
    async def cmd_webhook(message: Message):
        """Handle /webhook command."""
        webhook_info = await bot.get_webhook_info()
        await message.reply(
            f"Webhook information:\n"
            f"URL: {webhook_info.get('url', 'Not set')}\n"
            f"Has custom certificate: {webhook_info.get('has_custom_certificate', False)}\n"
            f"Pending update count: {webhook_info.get('pending_update_count', 0)}"
        )
    
    # Setup SSL context
    ssl_context = None
    if os.path.exists(WEBHOOK_SSL_CERT) and os.path.exists(WEBHOOK_SSL_PRIV):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
        logger.info("SSL context created successfully")
    else:
        logger.warning("SSL certificates not found, running without SSL")
    
    # Set webhook
    await bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=open(WEBHOOK_SSL_CERT, 'rb') if os.path.exists(WEBHOOK_SSL_CERT) else None,
        secret_token=WEBHOOK_SECRET
    )
    logger.info(f"Webhook set to {WEBHOOK_URL}")
    
    # Initialize webhook server
    webhook_server = WebhookServer(
        dispatcher=dp,
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT,
        ssl_context=ssl_context,
        secret_token=WEBHOOK_SECRET
    )
    
    # Start webhook server
    try:
        logger.info(f"Starting webhook server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
        await webhook_server.start()
    finally:
        # Cleanup
        await bot.delete_webhook()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 