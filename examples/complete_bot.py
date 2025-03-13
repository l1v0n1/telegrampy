#!/usr/bin/env python3
"""
Complete example bot demonstrating all features of the TelegramPy framework.
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta

from telegrampy import (
    Bot, Dispatcher, Filter, FSMContext, State, BaseMiddleware,
    RedisStorage, WebhookServer, MediaHandler, KeyboardBuilder,
    KeyboardButton, InlineKeyboardButton, PaymentHandler,
    LocationHandler, VoiceChatHandler, StoryHandler
)
from telegrampy.types import Message, CallbackQuery, Update

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Redis URL for storage (optional)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# States for conversation
class UserStates:
    START = State("start")
    NAME = State("name")
    AGE = State("age")
    LOCATION = State("location")
    PAYMENT = State("payment")
    STORY = State("story")

# Custom middleware example
class LoggingMiddleware(BaseMiddleware):
    async def process_update(self, update: Update, data: dict):
        logger.info(f"Processing update: {update.update_id}")
        return True

# Initialize bot and dispatcher
async def main():
    # Initialize bot
    bot = Bot(token=BOT_TOKEN)
    
    # Initialize storage
    storage = RedisStorage(REDIS_URL)
    
    # Initialize dispatcher with storage
    dp = Dispatcher(bot, storage=storage)
    
    # Add middleware
    dp.add_middleware(LoggingMiddleware())
    
    # Initialize handlers
    media_handler = MediaHandler(bot)
    payment_handler = PaymentHandler(
        provider_token="your_provider_token",
        currency="USD"
    )
    location_handler = LocationHandler()
    voice_chat_handler = VoiceChatHandler()
    story_handler = StoryHandler()
    
    # Basic command handlers
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: Message, state: FSMContext):
        """Handle /start command."""
        # Create welcome keyboard
        keyboard = KeyboardBuilder()
        keyboard.add_button(text="📝 Register")
        keyboard.add_button(text="📍 Share Location")
        keyboard.new_row()
        keyboard.add_button(text="💳 Make Payment")
        keyboard.add_button(text="📱 Create Story")
        
        await message.reply(
            "Welcome to the TelegramPy Demo Bot!\n"
            "This bot demonstrates all features of the TelegramPy framework.",
            reply_markup=keyboard.build().to_dict()
        )
        await state.set_state(UserStates.START)
    
    @dp.message_handler(commands=["help"])
    async def cmd_help(message: Message):
        """Handle /help command."""
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/register - Start registration process\n"
            "/location - Share your location\n"
            "/payment - Make a payment\n"
            "/story - Create a story\n"
            "/media - Upload media\n"
            "/cancel - Cancel current operation"
        )
        await message.reply(help_text)
    
    @dp.message_handler(commands=["cancel"], state="*")
    async def cmd_cancel(message: Message, state: FSMContext):
        """Cancel current operation and reset state."""
        current_state = await state.get_state()
        if current_state is None:
            await message.reply("No active operation to cancel.")
            return
        
        await state.finish()
        await message.reply("Operation cancelled.")
    
    # Registration process with FSM
    @dp.message_handler(commands=["register"])
    async def cmd_register(message: Message, state: FSMContext):
        """Start registration process."""
        await message.reply("Let's start registration. What's your name?")
        await state.set_state(UserStates.NAME)
    
    @dp.message_handler(state=UserStates.NAME)
    async def process_name(message: Message, state: FSMContext):
        """Process user's name."""
        await state.update_data(name=message.text)
        await message.reply("Great! Now, how old are you?")
        await state.set_state(UserStates.AGE)
    
    @dp.message_handler(state=UserStates.AGE)
    async def process_age(message: Message, state: FSMContext):
        """Process user's age."""
        try:
            age = int(message.text)
            await state.update_data(age=age)
            
            # Create location keyboard
            keyboard = KeyboardBuilder()
            keyboard.add_button(
                text="📍 Share my location",
                request_location=True
            )
            
            await message.reply(
                "Thanks! Now, please share your location.",
                reply_markup=keyboard.build().to_dict()
            )
            await state.set_state(UserStates.LOCATION)
        except ValueError:
            await message.reply("Please enter a valid age (numbers only).")
    
    # Location handling
    @dp.message_handler(content_types=["location"], state=UserStates.LOCATION)
    async def process_location(message: Message, state: FSMContext):
        """Process user's location."""
        if not message.location:
            await message.reply("Please share your location using the button.")
            return
        
        # Get location data
        location = message.location
        await state.update_data(
            location={
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        )
        
        # Use location handler to format message
        nearby_message = location_handler.format_location_message({
            "latitude": location.latitude,
            "longitude": location.longitude
        })
        
        # Get user data
        user_data = await state.get_data()
        
        # Format confirmation message
        confirmation = (
            f"Registration complete!\n\n"
            f"Name: {user_data['name']}\n"
            f"Age: {user_data['age']}\n"
            f"Location: {location.latitude}, {location.longitude}\n\n"
            f"{nearby_message}"
        )
        
        await message.reply(confirmation)
        await state.finish()
    
    # Payment handling
    @dp.message_handler(commands=["payment"])
    async def cmd_payment(message: Message, state: FSMContext):
        """Handle payment command."""
        # Add prices to payment handler
        payment_handler.add_price(
            label="Demo Product",
            amount=500,  # $5.00
            description="A demo product for testing payments"
        )
        
        # Create invoice
        invoice = payment_handler.create_invoice(
            title="TelegramPy Demo Payment",
            description="This is a demo payment for testing the TelegramPy framework",
            payload="demo_payment",
            provider_token="your_provider_token",
            currency="USD",
            prices=payment_handler.prices
        )
        
        # Create payment button
        payment_button = payment_handler.create_payment_button(
            title="Pay Now",
            description="Click to pay",
            payload="demo_payment",
            currency="USD",
            prices=payment_handler.prices
        )
        
        await message.reply(
            "Please click the button below to make a payment:",
            reply_markup=payment_button.to_dict()
        )
        await state.set_state(UserStates.PAYMENT)
    
    @dp.pre_checkout_query_handler(state=UserStates.PAYMENT)
    async def process_pre_checkout_query(pre_checkout_query, state: FSMContext):
        """Process pre-checkout query."""
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )
    
    @dp.message_handler(content_types=["successful_payment"], state=UserStates.PAYMENT)
    async def process_successful_payment(message: Message, state: FSMContext):
        """Process successful payment."""
        await payment_handler.process_successful_payment(message.successful_payment)
        await message.reply("Thank you for your payment!")
        await state.finish()
    
    # Story handling
    @dp.message_handler(commands=["story"])
    async def cmd_story(message: Message, state: FSMContext):
        """Handle story command."""
        await message.reply(
            "Please send a photo or video to create a story.",
            reply_markup=KeyboardBuilder().add_button(
                text="Cancel"
            ).build().to_dict()
        )
        await state.set_state(UserStates.STORY)
    
    @dp.message_handler(content_types=["photo", "video"], state=UserStates.STORY)
    async def process_story_media(message: Message, state: FSMContext):
        """Process story media."""
        media_type = "photo" if message.photo else "video"
        media_data = message.photo[-1] if message.photo else message.video
        
        # Create story
        story = await story_handler.create_story(
            user_id=message.from_user.id,
            media_type=media_type,
            media_data=media_data.dict(),
            caption=message.caption
        )
        
        if story:
            # Create story keyboard
            keyboard = story_handler.create_story_keyboard(
                user_id=message.from_user.id,
                story_id=story.id
            )
            
            await message.reply(
                "Your story has been created!",
                reply_markup=keyboard
            )
        else:
            await message.reply("Failed to create story. Please try again.")
        
        await state.finish()
    
    # Media handling
    @dp.message_handler(commands=["media"])
    async def cmd_media(message: Message):
        """Handle media command."""
        await message.reply(
            "Please send any media file (photo, video, document, etc.)"
        )
    
    @dp.message_handler(content_types=["photo", "video", "document", "audio", "voice"])
    async def process_media(message: Message):
        """Process media files."""
        try:
            # Determine media type
            if message.photo:
                media_type = "photo"
                file_id = message.photo[-1].file_id
            elif message.video:
                media_type = "video"
                file_id = message.video.file_id
            elif message.document:
                media_type = "document"
                file_id = message.document.file_id
            elif message.audio:
                media_type = "audio"
                file_id = message.audio.file_id
            elif message.voice:
                media_type = "voice"
                file_id = message.voice.file_id
            else:
                await message.reply("Unsupported media type.")
                return
            
            # Download file
            file_path = await media_handler.download_file(file_id)
            
            if file_path:
                await message.reply(
                    f"File downloaded successfully!\n"
                    f"Type: {media_type}\n"
                    f"Path: {file_path}"
                )
            else:
                await message.reply("Failed to download file.")
        
        except Exception as e:
            logger.error(f"Error processing media: {e}")
            await message.reply(f"Error processing media: {e}")
    
    # Voice chat handling
    @dp.message_handler(content_types=["voice_chat_started"])
    async def handle_voice_chat_started(message: Message):
        """Handle voice chat started event."""
        await voice_chat_handler.handle_voice_chat_started(
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )
        await message.reply("Voice chat started. I'll help moderate it!")
    
    @dp.message_handler(content_types=["voice_chat_ended"])
    async def handle_voice_chat_ended(message: Message):
        """Handle voice chat ended event."""
        await voice_chat_handler.handle_voice_chat_ended(
            chat_id=message.chat.id
        )
        await message.reply("Voice chat ended.")
    
    # Callback query handling
    @dp.callback_query_handler(lambda c: c.data.startswith("view_story_"))
    async def process_view_story(callback_query: CallbackQuery):
        """Process view story callback."""
        _, user_id, story_id = callback_query.data.split("_", 2)
        story = story_handler.get_story(int(user_id), story_id)
        
        if story:
            # Format story message
            message = story_handler.format_story_message(story)
            await callback_query.message.reply(message)
        else:
            await callback_query.message.reply("Story not found or expired.")
        
        await callback_query.answer()
    
    # Start polling
    try:
        await dp.start_polling()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 