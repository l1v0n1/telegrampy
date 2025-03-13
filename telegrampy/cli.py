"""
Command-line interface for TelegramPy.
"""
import argparse
import asyncio
import logging
from .bot import Bot
from .dispatcher import Dispatcher
from .storage import RedisStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="TelegramPy CLI")
    parser.add_argument(
        "--token",
        required=True,
        help="Telegram Bot API token"
    )
    parser.add_argument(
        "--redis-url",
        default="redis://localhost",
        help="Redis URL (default: redis://localhost)"
    )
    parser.add_argument(
        "--webhook-url",
        help="Webhook URL for receiving updates"
    )
    parser.add_argument(
        "--webhook-port",
        type=int,
        default=8443,
        help="Webhook port (default: 8443)"
    )
    return parser.parse_args()

async def start_polling(bot: Bot, dispatcher: Dispatcher):
    """Start polling for updates."""
    logger.info("Starting polling...")
    await dispatcher.start_polling()

async def start_webhook(bot: Bot, dispatcher: Dispatcher, url: str, port: int):
    """Start webhook server."""
    logger.info(f"Starting webhook server on {url}:{port}")
    await bot.set_webhook(url=url)
    # Here you would implement the webhook server
    # This is a placeholder for the actual implementation
    while True:
        await asyncio.sleep(1)

async def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize bot and dispatcher
    bot = Bot(args.token)
    storage = RedisStorage(args.redis_url)
    dispatcher = Dispatcher(bot)
    
    try:
        if args.webhook_url:
            await start_webhook(bot, dispatcher, args.webhook_url, args.webhook_port)
        else:
            await start_polling(bot, dispatcher)
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        await storage.close()

if __name__ == "__main__":
    asyncio.run(main()) 