#!/usr/bin/env python3
"""
Example bot demonstrating topic management with the TelegramPy framework.
"""
import asyncio
import logging
import os
from typing import Dict, Any

from telegrampy import Bot, Dispatcher, TopicManager
from telegrampy.types import Message, CallbackQuery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    
    # Initialize topic manager
    topic_manager = TopicManager()
    
    # Command handlers
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: Message):
        """Handle /start command."""
        await message.reply(
            "Welcome to the TelegramPy Topic Management Demo Bot!\n"
            "This bot demonstrates topic management functionality in forum groups.\n\n"
            "Available commands:\n"
            "/start - Show this message\n"
            "/help - Show help message\n"
            "/topics - List all topics in this group\n"
            "/create_topic <name> - Create a new topic\n"
            "/close_topic <thread_id> - Close a topic\n"
            "/reopen_topic <thread_id> - Reopen a topic\n"
            "/delete_topic <thread_id> - Delete a topic"
        )
    
    @dp.message_handler(commands=["help"])
    async def cmd_help(message: Message):
        """Handle /help command."""
        help_text = (
            "This bot helps you manage forum topics in your group.\n\n"
            "To use this bot, you need to:\n"
            "1. Add this bot to a group\n"
            "2. Make the group a forum (in group settings)\n"
            "3. Give the bot admin privileges\n\n"
            "Then you can use the commands to manage topics."
        )
        await message.reply(help_text)
    
    @dp.message_handler(commands=["topics"])
    async def cmd_topics(message: Message):
        """List all topics in the group."""
        # Check if message is from a group
        if message.chat.type not in ["group", "supergroup"]:
            await message.reply("This command can only be used in groups.")
            return
        
        # Get topics
        topics = await topic_manager.get_forum_topics(bot, message.chat.id)
        
        if not topics:
            await message.reply(
                "No topics found in this group. Use /create_topic <name> to create one."
            )
            return
        
        # Format topics list
        topics_text = "Topics in this group:\n\n"
        for topic in topics:
            status = "🔒 Closed" if topic.get("is_closed", False) else "🔓 Open"
            topics_text += f"ID: {topic['message_thread_id']}\n"
            topics_text += f"Name: {topic['name']}\n"
            topics_text += f"Status: {status}\n\n"
        
        # Create keyboard for topic selection
        keyboard = topic_manager.create_topic_keyboard(message.chat.id, topics)
        
        await message.reply(
            topics_text,
            reply_markup=keyboard
        )
    
    @dp.message_handler(commands=["create_topic"])
    async def cmd_create_topic(message: Message):
        """Create a new topic."""
        # Check if message is from a group
        if message.chat.type not in ["group", "supergroup"]:
            await message.reply("This command can only be used in groups.")
            return
        
        # Get topic name from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide a topic name: /create_topic <name>")
            return
        
        topic_name = command_parts[1].strip()
        if len(topic_name) < 1 or len(topic_name) > 128:
            await message.reply("Topic name must be between 1 and 128 characters.")
            return
        
        # Create topic
        topic = await topic_manager.create_topic(
            bot=bot,
            chat_id=message.chat.id,
            name=topic_name
        )
        
        if topic:
            await message.reply(
                f"Topic '{topic_name}' created successfully!\n"
                f"Thread ID: {topic['message_thread_id']}"
            )
        else:
            await message.reply(
                "Failed to create topic. Make sure this is a forum group and the bot has admin privileges."
            )
    
    @dp.message_handler(commands=["close_topic"])
    async def cmd_close_topic(message: Message):
        """Close a topic."""
        # Check if message is from a group
        if message.chat.type not in ["group", "supergroup"]:
            await message.reply("This command can only be used in groups.")
            return
        
        # Get thread ID from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide a thread ID: /close_topic <thread_id>")
            return
        
        try:
            thread_id = int(command_parts[1].strip())
        except ValueError:
            await message.reply("Thread ID must be a number.")
            return
        
        # Close topic
        success = await topic_manager.close_topic(
            bot=bot,
            chat_id=message.chat.id,
            message_thread_id=thread_id
        )
        
        if success:
            await message.reply(f"Topic with thread ID {thread_id} closed successfully.")
        else:
            await message.reply(
                "Failed to close topic. Make sure the thread ID is correct and the bot has admin privileges."
            )
    
    @dp.message_handler(commands=["reopen_topic"])
    async def cmd_reopen_topic(message: Message):
        """Reopen a topic."""
        # Check if message is from a group
        if message.chat.type not in ["group", "supergroup"]:
            await message.reply("This command can only be used in groups.")
            return
        
        # Get thread ID from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide a thread ID: /reopen_topic <thread_id>")
            return
        
        try:
            thread_id = int(command_parts[1].strip())
        except ValueError:
            await message.reply("Thread ID must be a number.")
            return
        
        # Reopen topic
        success = await topic_manager.reopen_topic(
            bot=bot,
            chat_id=message.chat.id,
            message_thread_id=thread_id
        )
        
        if success:
            await message.reply(f"Topic with thread ID {thread_id} reopened successfully.")
        else:
            await message.reply(
                "Failed to reopen topic. Make sure the thread ID is correct and the bot has admin privileges."
            )
    
    @dp.message_handler(commands=["delete_topic"])
    async def cmd_delete_topic(message: Message):
        """Delete a topic."""
        # Check if message is from a group
        if message.chat.type not in ["group", "supergroup"]:
            await message.reply("This command can only be used in groups.")
            return
        
        # Get thread ID from command
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.reply("Please provide a thread ID: /delete_topic <thread_id>")
            return
        
        try:
            thread_id = int(command_parts[1].strip())
        except ValueError:
            await message.reply("Thread ID must be a number.")
            return
        
        # Delete topic
        success = await topic_manager.delete_topic(
            bot=bot,
            chat_id=message.chat.id,
            message_thread_id=thread_id
        )
        
        if success:
            await message.reply(f"Topic with thread ID {thread_id} deleted successfully.")
        else:
            await message.reply(
                "Failed to delete topic. Make sure the thread ID is correct and the bot has admin privileges."
            )
    
    # Callback query handler for topic selection
    @dp.callback_query_handler(lambda c: c.data.startswith("topic_"))
    async def process_topic_selection(callback_query: CallbackQuery):
        """Process topic selection."""
        # Parse callback data
        _, chat_id, thread_id = callback_query.data.split("_")
        chat_id = int(chat_id)
        thread_id = int(thread_id)
        
        # Get topic from cache
        topic = None
        if (chat_id in topic_manager.topic_cache and 
            thread_id in topic_manager.topic_cache[chat_id]):
            topic = topic_manager.topic_cache[chat_id][thread_id]
        
        if not topic:
            await callback_query.answer("Topic not found.")
            return
        
        # Create topic management keyboard
        from telegrampy.keyboard import KeyboardBuilder
        
        keyboard = KeyboardBuilder()
        keyboard.add_button(
            text="✏️ Edit",
            callback_data=f"edit_topic_{chat_id}_{thread_id}"
        )
        
        if topic.get("is_closed", False):
            keyboard.add_button(
                text="🔓 Reopen",
                callback_data=f"reopen_topic_{chat_id}_{thread_id}"
            )
        else:
            keyboard.add_button(
                text="🔒 Close",
                callback_data=f"close_topic_{chat_id}_{thread_id}"
            )
        
        keyboard.new_row()
        keyboard.add_button(
            text="🗑 Delete",
            callback_data=f"delete_topic_{chat_id}_{thread_id}"
        )
        keyboard.add_button(
            text="❌ Cancel",
            callback_data="cancel_topic_action"
        )
        
        await callback_query.message.reply(
            f"Topic: {topic['name']}\n"
            f"Thread ID: {thread_id}\n"
            f"Status: {'🔒 Closed' if topic.get('is_closed', False) else '🔓 Open'}\n\n"
            "Select an action:",
            reply_markup=keyboard.build().to_dict()
        )
        
        await callback_query.answer()
    
    # Callback query handlers for topic actions
    @dp.callback_query_handler(lambda c: c.data.startswith("close_topic_"))
    async def process_close_topic(callback_query: CallbackQuery):
        """Process close topic action."""
        # Parse callback data
        _, chat_id, thread_id = callback_query.data.split("_")
        chat_id = int(chat_id)
        thread_id = int(thread_id)
        
        # Close topic
        success = await topic_manager.close_topic(
            bot=bot,
            chat_id=chat_id,
            message_thread_id=thread_id
        )
        
        if success:
            await callback_query.message.reply("Topic closed successfully.")
        else:
            await callback_query.message.reply("Failed to close topic.")
        
        await callback_query.answer()
    
    @dp.callback_query_handler(lambda c: c.data.startswith("reopen_topic_"))
    async def process_reopen_topic(callback_query: CallbackQuery):
        """Process reopen topic action."""
        # Parse callback data
        _, chat_id, thread_id = callback_query.data.split("_")
        chat_id = int(chat_id)
        thread_id = int(thread_id)
        
        # Reopen topic
        success = await topic_manager.reopen_topic(
            bot=bot,
            chat_id=chat_id,
            message_thread_id=thread_id
        )
        
        if success:
            await callback_query.message.reply("Topic reopened successfully.")
        else:
            await callback_query.message.reply("Failed to reopen topic.")
        
        await callback_query.answer()
    
    @dp.callback_query_handler(lambda c: c.data.startswith("delete_topic_"))
    async def process_delete_topic(callback_query: CallbackQuery):
        """Process delete topic action."""
        # Parse callback data
        _, chat_id, thread_id = callback_query.data.split("_")
        chat_id = int(chat_id)
        thread_id = int(thread_id)
        
        # Delete topic
        success = await topic_manager.delete_topic(
            bot=bot,
            chat_id=chat_id,
            message_thread_id=thread_id
        )
        
        if success:
            await callback_query.message.reply("Topic deleted successfully.")
        else:
            await callback_query.message.reply("Failed to delete topic.")
        
        await callback_query.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "cancel_topic_action")
    async def process_cancel_topic_action(callback_query: CallbackQuery):
        """Process cancel topic action."""
        await callback_query.message.reply("Action cancelled.")
        await callback_query.answer()
    
    # Start polling
    try:
        await dp.start_polling()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 