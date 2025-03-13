#!/usr/bin/env python3
"""
Simple example bot demonstrating basic usage of the TelegramPy framework.
"""
import asyncio
import os

from telegrampy import Bot, Dispatcher
from telegrampy.types import Message

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    
    # Register message handlers
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: Message):
        """Handle /start command."""
        await message.reply("Hello! I'm a simple TelegramPy bot.")
    
    @dp.message_handler(commands=["help"])
    async def cmd_help(message: Message):
        """Handle /help command."""
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message"
        )
        await message.reply(help_text)
    
    @dp.message_handler()
    async def echo(message: Message):
        """Echo all messages."""
        await message.reply(f"You said: {message.text}")
    
    # Start polling
    try:
        await dp.start_polling()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 