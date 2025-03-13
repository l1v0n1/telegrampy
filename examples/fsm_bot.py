#!/usr/bin/env python3
"""
Example bot demonstrating FSM (Finite State Machine) usage with the TelegramPy framework.
"""
import asyncio
import logging
import os
from typing import Dict, Any

from telegrampy import Bot, Dispatcher, FSMContext, State, RedisStorage
from telegrampy.types import Message, CallbackQuery

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

# Define states for the survey
class SurveyStates:
    START = State("start")
    NAME = State("name")
    AGE = State("age")
    GENDER = State("gender")
    EDUCATION = State("education")
    INTERESTS = State("interests")
    CONFIRMATION = State("confirmation")

async def main():
    # Initialize bot
    bot = Bot(token=BOT_TOKEN)
    
    # Initialize storage
    storage = RedisStorage(REDIS_URL)
    
    # Initialize dispatcher with storage
    dp = Dispatcher(bot, storage=storage)
    
    # Command handlers
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: Message):
        """Handle /start command."""
        await message.reply(
            "Welcome to the TelegramPy FSM Demo Bot!\n"
            "This bot demonstrates FSM functionality for multi-step conversations.\n\n"
            "Type /survey to start a new survey."
        )
    
    @dp.message_handler(commands=["help"])
    async def cmd_help(message: Message):
        """Handle /help command."""
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/survey - Start a new survey\n"
            "/cancel - Cancel the current survey"
        )
        await message.reply(help_text)
    
    @dp.message_handler(commands=["cancel"], state="*")
    async def cmd_cancel(message: Message, state: FSMContext):
        """Cancel the current survey."""
        current_state = await state.get_state()
        if current_state is None:
            await message.reply("No active survey to cancel.")
            return
        
        await state.finish()
        await message.reply("Survey cancelled. Type /survey to start a new one.")
    
    # Survey handlers
    @dp.message_handler(commands=["survey"])
    async def cmd_survey(message: Message, state: FSMContext):
        """Start a new survey."""
        await message.reply(
            "Let's start a new survey. You can type /cancel at any time to stop.\n\n"
            "What's your name?"
        )
        await state.set_state(SurveyStates.NAME)
    
    @dp.message_handler(state=SurveyStates.NAME)
    async def process_name(message: Message, state: FSMContext):
        """Process name response."""
        name = message.text.strip()
        if len(name) < 2:
            await message.reply("Please enter a valid name (at least 2 characters).")
            return
        
        await state.update_data(name=name)
        await message.reply(
            f"Nice to meet you, {name}!\n\n"
            "How old are you? (Please enter a number)"
        )
        await state.set_state(SurveyStates.AGE)
    
    @dp.message_handler(state=SurveyStates.AGE)
    async def process_age(message: Message, state: FSMContext):
        """Process age response."""
        try:
            age = int(message.text.strip())
            if age < 1 or age > 120:
                await message.reply("Please enter a valid age (between 1 and 120).")
                return
            
            await state.update_data(age=age)
            
            # Create inline keyboard for gender selection
            from telegrampy.keyboard import KeyboardBuilder, InlineKeyboardButton
            
            keyboard = KeyboardBuilder()
            keyboard.add_button(
                text="Male",
                callback_data="gender_male"
            )
            keyboard.add_button(
                text="Female",
                callback_data="gender_female"
            )
            keyboard.new_row()
            keyboard.add_button(
                text="Other",
                callback_data="gender_other"
            )
            keyboard.add_button(
                text="Prefer not to say",
                callback_data="gender_not_specified"
            )
            
            await message.reply(
                "What's your gender?",
                reply_markup=keyboard.build().to_dict()
            )
            await state.set_state(SurveyStates.GENDER)
        except ValueError:
            await message.reply("Please enter a valid age (numbers only).")
    
    @dp.callback_query_handler(
        lambda c: c.data.startswith("gender_"),
        state=SurveyStates.GENDER
    )
    async def process_gender(callback_query: CallbackQuery, state: FSMContext):
        """Process gender selection."""
        gender = callback_query.data.split("_")[1]
        await state.update_data(gender=gender)
        
        # Create inline keyboard for education selection
        from telegrampy.keyboard import KeyboardBuilder
        
        keyboard = KeyboardBuilder()
        keyboard.add_button(
            text="High School",
            callback_data="education_high_school"
        )
        keyboard.add_button(
            text="Bachelor's",
            callback_data="education_bachelors"
        )
        keyboard.new_row()
        keyboard.add_button(
            text="Master's",
            callback_data="education_masters"
        )
        keyboard.add_button(
            text="PhD",
            callback_data="education_phd"
        )
        keyboard.new_row()
        keyboard.add_button(
            text="Other",
            callback_data="education_other"
        )
        
        await callback_query.message.reply(
            "What's your highest level of education?",
            reply_markup=keyboard.build().to_dict()
        )
        await callback_query.answer()
        await state.set_state(SurveyStates.EDUCATION)
    
    @dp.callback_query_handler(
        lambda c: c.data.startswith("education_"),
        state=SurveyStates.EDUCATION
    )
    async def process_education(callback_query: CallbackQuery, state: FSMContext):
        """Process education selection."""
        education = callback_query.data.split("_", 1)[1]
        await state.update_data(education=education)
        
        await callback_query.message.reply(
            "What are your interests? (Enter multiple interests separated by commas)"
        )
        await callback_query.answer()
        await state.set_state(SurveyStates.INTERESTS)
    
    @dp.message_handler(state=SurveyStates.INTERESTS)
    async def process_interests(message: Message, state: FSMContext):
        """Process interests response."""
        interests = [i.strip() for i in message.text.split(",") if i.strip()]
        if not interests:
            await message.reply("Please enter at least one interest.")
            return
        
        await state.update_data(interests=interests)
        
        # Get all survey data
        data = await state.get_data()
        
        # Format confirmation message
        confirmation = (
            "Please confirm your survey responses:\n\n"
            f"Name: {data['name']}\n"
            f"Age: {data['age']}\n"
            f"Gender: {data['gender']}\n"
            f"Education: {data['education'].replace('_', ' ').title()}\n"
            f"Interests: {', '.join(data['interests'])}\n\n"
            "Is this information correct?"
        )
        
        # Create confirmation keyboard
        from telegrampy.keyboard import KeyboardBuilder
        
        keyboard = KeyboardBuilder()
        keyboard.add_button(
            text="✅ Yes, submit",
            callback_data="confirm_yes"
        )
        keyboard.add_button(
            text="❌ No, restart",
            callback_data="confirm_no"
        )
        
        await message.reply(
            confirmation,
            reply_markup=keyboard.build().to_dict()
        )
        await state.set_state(SurveyStates.CONFIRMATION)
    
    @dp.callback_query_handler(
        lambda c: c.data == "confirm_yes",
        state=SurveyStates.CONFIRMATION
    )
    async def confirm_survey(callback_query: CallbackQuery, state: FSMContext):
        """Process survey confirmation."""
        # Get all survey data
        data = await state.get_data()
        
        # Here you would typically save the survey data to a database
        logger.info(f"Survey completed: {data}")
        
        await callback_query.message.reply(
            "Thank you for completing the survey! Your responses have been recorded."
        )
        await callback_query.answer()
        await state.finish()
    
    @dp.callback_query_handler(
        lambda c: c.data == "confirm_no",
        state=SurveyStates.CONFIRMATION
    )
    async def reject_survey(callback_query: CallbackQuery, state: FSMContext):
        """Process survey rejection."""
        await callback_query.message.reply(
            "Survey cancelled. Type /survey to start a new one."
        )
        await callback_query.answer()
        await state.finish()
    
    # Start polling
    try:
        await dp.start_polling()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 