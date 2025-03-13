# TelegramPy Examples

This directory contains example bots that demonstrate various features of the TelegramPy framework.

## Prerequisites

Before running these examples, make sure you have:

1. Python 3.7 or higher installed
2. TelegramPy framework installed
3. A Telegram Bot token (get one from [@BotFather](https://t.me/BotFather))
4. Redis server (optional, for state storage)

## Environment Variables

Most examples use environment variables for configuration:

- `BOT_TOKEN`: Your Telegram Bot API token
- `REDIS_URL`: URL for Redis connection (default: `redis://localhost:6379/0`)
- `WEBHOOK_HOST`: Domain name for webhook (for webhook example)
- `WEBHOOK_PORT`: Port for webhook server (default: `8443`)
- `WEBHOOK_SSL_CERT`: Path to SSL certificate file (for webhook example)
- `WEBHOOK_SSL_PRIV`: Path to SSL private key file (for webhook example)
- `WEBHOOK_SECRET`: Secret token for webhook validation (for webhook example)

## Examples

### 1. Simple Bot (`simple_bot.py`)

A basic example that demonstrates the core functionality of the TelegramPy framework:

- Command handling
- Echo functionality
- Basic message handling

**Run with:**

```bash
export BOT_TOKEN="your_bot_token_here"
python simple_bot.py
```

### 2. Complete Bot (`complete_bot.py`)

A comprehensive example that demonstrates most features of the TelegramPy framework, including:

- Command handling
- Finite State Machine (FSM) for conversations
- Media handling
- Payment processing
- Location handling
- Story interaction
- Voice chat moderation
- Inline keyboards and callback queries

**Run with:**

```bash
export BOT_TOKEN="your_bot_token_here"
export REDIS_URL="redis://localhost:6379/0"
python complete_bot.py
```

### 3. Webhook Bot (`webhook_bot.py`)

Demonstrates how to use webhooks instead of polling for receiving updates:

- Setting up a webhook server
- SSL configuration
- Webhook validation
- Basic command handling

**Run with:**

```bash
export BOT_TOKEN="your_bot_token_here"
export WEBHOOK_HOST="your_domain.com"
export WEBHOOK_PORT="8443"
export WEBHOOK_SSL_CERT="path/to/cert.pem"
export WEBHOOK_SSL_PRIV="path/to/privkey.pem"
export WEBHOOK_SECRET="your_secret_token"
python webhook_bot.py
```

### 4. FSM Bot (`fsm_bot.py`)

Demonstrates how to use the Finite State Machine (FSM) for multi-step conversations:

- State management
- Form filling
- Inline keyboards for options
- Data validation
- Confirmation flow

**Run with:**

```bash
export BOT_TOKEN="your_bot_token_here"
export REDIS_URL="redis://localhost:6379/0"
python fsm_bot.py
```

### 5. Topic Management Bot (`topic_bot.py`)

Demonstrates how to manage forum topics in Telegram groups:

- Creating, editing, closing, reopening, and deleting topics
- Topic listing and selection
- Interactive topic management with inline keyboards
- Group-specific functionality

**Run with:**

```bash
export BOT_TOKEN="your_bot_token_here"
python topic_bot.py
```

**Note:** To use this bot, you need to:
1. Add the bot to a group
2. Make the group a forum (in group settings)
3. Give the bot admin privileges

## Notes

- These examples are meant for educational purposes and may need adjustments for production use.
- For webhook examples, you need a domain with SSL certificate.
- Redis is recommended for state storage in production, but you can use other storage backends.

## Additional Resources

- [TelegramPy Documentation](https://telegrampy.readthedocs.io/)
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Redis Documentation](https://redis.io/documentation) 