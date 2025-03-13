import pytest
from unittest.mock import AsyncMock, patch

from telegrampy import Bot


@pytest.fixture
def bot():
    """Create a Bot instance with a mocked session."""
    with patch("telegrampy.bot.aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        bot_instance = Bot(token="test_token")
        yield bot_instance


@pytest.mark.asyncio
async def test_bot_initialization(bot):
    """Test that the Bot is initialized correctly."""
    assert bot.token == "test_token"
    assert bot.base_url == "https://api.telegram.org/bottest_token/"


@pytest.mark.asyncio
async def test_get_me(bot):
    """Test the get_me method."""
    # Mock the response
    mock_response = {
        "ok": True,
        "result": {
            "id": 123456789,
            "is_bot": True,
            "first_name": "Test Bot",
            "username": "test_bot",
            "can_join_groups": True,
            "can_read_all_group_messages": False,
            "supports_inline_queries": False
        }
    }
    
    # Set up the mock
    bot._make_request = AsyncMock(return_value=mock_response)
    
    # Call the method
    result = await bot.get_me()
    
    # Assert the result
    assert result == mock_response["result"]
    bot._make_request.assert_called_once_with("getMe")


@pytest.mark.asyncio
async def test_send_message(bot):
    """Test the send_message method."""
    # Mock the response
    mock_response = {
        "ok": True,
        "result": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": True,
                "first_name": "Test Bot",
                "username": "test_bot"
            },
            "chat": {
                "id": 987654321,
                "first_name": "Test",
                "last_name": "User",
                "username": "test_user",
                "type": "private"
            },
            "date": 1623456789,
            "text": "Test message"
        }
    }
    
    # Set up the mock
    bot._make_request = AsyncMock(return_value=mock_response)
    
    # Call the method
    result = await bot.send_message(
        chat_id=987654321,
        text="Test message"
    )
    
    # Assert the result
    assert result == mock_response["result"]
    bot._make_request.assert_called_once_with(
        "sendMessage",
        {
            "chat_id": 987654321,
            "text": "Test message"
        }
    ) 