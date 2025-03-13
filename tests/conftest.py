import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from telegrampy import Bot, Dispatcher
from telegrampy.storage import RedisStorage


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def bot():
    """Create a Bot instance with a mocked session."""
    with patch("telegrampy.bot.aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        bot_instance = Bot(token="test_token")
        yield bot_instance
        await bot_instance.close()


@pytest.fixture
async def storage():
    """Create a mock storage instance."""
    mock_storage = AsyncMock(spec=RedisStorage)
    mock_storage.get_state.return_value = None
    mock_storage.get_data.return_value = {}
    mock_storage.set_state.return_value = None
    mock_storage.set_data.return_value = None
    mock_storage.update_data.return_value = None
    mock_storage.finish.return_value = None
    yield mock_storage


@pytest.fixture
async def dispatcher(bot, storage):
    """Create a Dispatcher instance with mocked bot and storage."""
    dp = Dispatcher(bot, storage=storage)
    yield dp 