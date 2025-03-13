# TelegramPy

A modern, asynchronous Python framework for building Telegram bots with a focus on performance, clean code architecture, and developer-friendly interfaces.

## Features

- Asynchronous architecture using Python's `asyncio` and `aiohttp`
- Clean, object-oriented API design
- Strong typing support with type hints
- Support for all Telegram Bot API 6.0+ features
- Flexible message and command handler system
- State management system for multi-step conversations
- Middleware architecture for processing updates
- Error handling with detailed logging
- Finite State Machine (FSM) for conversation flows
- Custom filter system for routing messages
- Inline keyboard and callback query handlers
- File upload/download utilities
- Webhook support with proper security
- Redis storage backend
- Message reactions handler system
- Voice chat moderation tools
- Location-based services
- Mini-App integration helpers
- Payment system processing
- Story interaction handlers
- Topic management for group conversations
- Enhanced media processing
- Scheduled message system
- Custom reply markup generators

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Here's a simple example of creating a bot:

```python
from telegrampy import Bot, Dispatcher, Command, Text
from telegrampy.storage import RedisStorage

# Initialize bot and dispatcher
bot = Bot("YOUR_BOT_TOKEN")
storage = RedisStorage("redis://localhost")
dispatcher = Dispatcher(bot)

# Register handlers
@dispatcher.register_handler(Command("start"))
async def start_command(message):
    await message.reply("Hello! I'm your bot.")

@dispatcher.register_handler(Text("hello"))
async def hello_message(message):
    await message.reply("Hi there!")

# Start polling
async def main():
    await dispatcher.start_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Advanced Usage

### Using FSM (Finite State Machine)

```python
from telegrampy import Bot, Dispatcher, State, StateGroup
from telegrampy.storage import RedisStorage

# Define states
class RegistrationStates(StateGroup):
    waiting_for_name = State("waiting_for_name")
    waiting_for_age = State("waiting_for_age")
    waiting_for_email = State("waiting_for_email")

# Initialize bot and dispatcher
bot = Bot("YOUR_BOT_TOKEN")
storage = RedisStorage("redis://localhost")
dispatcher = Dispatcher(bot)

# Registration flow
@dispatcher.register_handler(Command("register"))
async def start_registration(message):
    await message.reply("Please enter your name:")
    await dispatcher.set_state(message.from_user.id, RegistrationStates.waiting_for_name)

@dispatcher.register_handler(state=RegistrationStates.waiting_for_name)
async def process_name(message):
    await dispatcher.update_data(name=message.text)
    await message.reply("Please enter your age:")
    await dispatcher.set_state(message.from_user.id, RegistrationStates.waiting_for_age)

@dispatcher.register_handler(state=RegistrationStates.waiting_for_age)
async def process_age(message):
    await dispatcher.update_data(age=message.text)
    await message.reply("Please enter your email:")
    await dispatcher.set_state(message.from_user.id, RegistrationStates.waiting_for_email)

@dispatcher.register_handler(state=RegistrationStates.waiting_for_email)
async def process_email(message):
    data = await dispatcher.get_data()
    await message.reply(f"Registration complete!\nName: {data['name']}\nAge: {data['age']}\nEmail: {message.text}")
    await dispatcher.finish()
```

### Using Middleware

```python
from telegrampy import Bot, Dispatcher
from telegrampy.middleware import LoggingMiddleware, ThrottlingMiddleware, AuthMiddleware

# Initialize bot and dispatcher
bot = Bot("YOUR_BOT_TOKEN")
dispatcher = Dispatcher(bot)

# Register middlewares
dispatcher.register_middleware(LoggingMiddleware())
dispatcher.register_middleware(ThrottlingMiddleware(rate_limit=1.0))
dispatcher.register_middleware(AuthMiddleware(allowed_users={123456789}))  # Replace with actual user IDs
```

### Using Filters

```python
from telegrampy import Bot, Dispatcher, Command, Text, ChatType, UserID
from telegrampy.filters import CallbackData

# Initialize bot and dispatcher
bot = Bot("YOUR_BOT_TOKEN")
dispatcher = Dispatcher(bot)

# Register handlers with filters
@dispatcher.register_handler(Command("start"), ChatType("private"))
async def start_private(message):
    await message.reply("Hello in private chat!")

@dispatcher.register_handler(Command("start"), ChatType("group"))
async def start_group(message):
    await message.reply("Hello in group chat!")

@dispatcher.register_handler(CallbackData("button_1"))
async def button_callback(callback_query):
    await callback_query.answer("Button clicked!")
```

## Examples

The `examples/` directory contains complete example bots that demonstrate various features of the framework:

1. **Simple Bot** (`examples/simple_bot.py`): A basic example demonstrating core functionality.
2. **Complete Bot** (`examples/complete_bot.py`): A comprehensive example showcasing most features of the framework.
3. **Webhook Bot** (`examples/webhook_bot.py`): Demonstrates how to use webhooks instead of polling.
4. **FSM Bot** (`examples/fsm_bot.py`): Shows how to use the Finite State Machine for multi-step conversations.
5. **Topic Management Bot** (`examples/topic_bot.py`): Demonstrates how to manage forum topics in Telegram groups.

Each example includes detailed comments and demonstrates best practices for building Telegram bots with TelegramPy. See the [examples README](examples/README.md) for more information on running these examples.

## Documentation

For detailed documentation, please visit our [documentation site](https://telegrampy.readthedocs.io/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.