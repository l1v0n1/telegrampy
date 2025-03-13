"""
Type definitions for Telegram API objects using Pydantic models.
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class User(BaseModel):
    """Telegram user model."""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None

class Chat(BaseModel):
    """Telegram chat model."""
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_forum: Optional[bool] = None
    photo: Optional[Dict[str, Any]] = None
    pinned_message: Optional[Dict[str, Any]] = None
    permissions: Optional[Dict[str, Any]] = None
    slow_mode_delay: Optional[int] = None
    message_auto_delete_time: Optional[int] = None
    has_aggressive_anti_spam_enabled: Optional[bool] = None
    has_hidden_members: Optional[bool] = None

class MessageEntity(BaseModel):
    """Telegram message entity model."""
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    language: Optional[str] = None
    custom_emoji_id: Optional[str] = None

class Location(BaseModel):
    """Telegram location model."""
    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float] = None
    live_period: Optional[int] = None
    heading: Optional[int] = None
    proximity_alert_radius: Optional[int] = None

class Venue(BaseModel):
    """Telegram venue model."""
    location: Location
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    google_place_id: Optional[str] = None
    google_place_type: Optional[str] = None

class Message(BaseModel):
    """Telegram message model."""
    message_id: int
    date: int
    chat: Chat
    from_user: Optional[User] = Field(None, alias="from")
    sender_chat: Optional[Chat] = None
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None
    is_automatic_forward: Optional[bool] = None
    reply_to_message: Optional[Dict[str, Any]] = None
    via_bot: Optional[User] = None
    edit_date: Optional[int] = None
    has_protected_content: Optional[bool] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    caption_entities: Optional[List[MessageEntity]] = None
    audio: Optional[Dict[str, Any]] = None
    document: Optional[Dict[str, Any]] = None
    photo: Optional[List[Dict[str, Any]]] = None
    sticker: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    voice: Optional[Dict[str, Any]] = None
    video_note: Optional[Dict[str, Any]] = None
    caption: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None
    dice: Optional[Dict[str, Any]] = None
    game: Optional[Dict[str, Any]] = None
    poll: Optional[Dict[str, Any]] = None
    venue: Optional[Venue] = None
    location: Optional[Location] = None
    new_chat_members: Optional[List[User]] = None
    left_chat_member: Optional[User] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[List[Dict[str, Any]]] = None
    delete_chat_photo: Optional[bool] = None
    group_chat_created: Optional[bool] = None
    supergroup_chat_created: Optional[bool] = None
    channel_chat_created: Optional[bool] = None
    message_auto_delete_timer_changed: Optional[Dict[str, Any]] = None
    migrate_to_chat_id: Optional[int] = None
    migrate_from_chat_id: Optional[int] = None
    pinned_message: Optional[Dict[str, Any]] = None
    invoice: Optional[Dict[str, Any]] = None
    successful_payment: Optional[Dict[str, Any]] = None
    connected_website: Optional[str] = None
    passport_data: Optional[Dict[str, Any]] = None
    proximity_alert_triggered: Optional[Dict[str, Any]] = None
    video_chat_scheduled: Optional[Dict[str, Any]] = None
    video_chat_started: Optional[Dict[str, Any]] = None
    video_chat_ended: Optional[Dict[str, Any]] = None
    video_chat_participants_invited: Optional[Dict[str, Any]] = None
    web_app_data: Optional[Dict[str, Any]] = None
    reply_markup: Optional[Dict[str, Any]] = None

class CallbackQuery(BaseModel):
    """Telegram callback query model."""
    id: str
    from_user: User = Field(..., alias="from")
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    chat_instance: str
    data: Optional[str] = None
    game_short_name: Optional[str] = None

class PreCheckoutQuery(BaseModel):
    """Telegram pre-checkout query model."""
    id: str
    from_user: User = Field(..., alias="from")
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[Dict[str, Any]] = None

class ChatMember(BaseModel):
    """Telegram chat member model."""
    user: User
    status: str
    is_anonymous: Optional[bool] = None
    custom_title: Optional[str] = None
    until_date: Optional[int] = None
    can_be_edited: Optional[bool] = None
    can_manage_chat: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_manage_video_chats: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_manage_topics: Optional[bool] = None

class Story(BaseModel):
    """
    Telegram story model.
    
    Attributes:
        id (str): Unique story ID
        user_id (int): User ID who created the story
        media_type (str): Type of media in the story
        media_data (Dict[str, Any]): Media data
        caption (Optional[str]): Story caption
        created_at (datetime): Creation timestamp
        expires_at (datetime): Expiration timestamp
        views (int): View count
        likes (int): Like count
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    media_type: str
    media_data: Dict[str, Any]
    caption: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    views: int = 0
    likes: int = 0

class Update(BaseModel):
    """Telegram update model."""
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None
    inline_query: Optional[Dict[str, Any]] = None
    chosen_inline_result: Optional[Dict[str, Any]] = None
    callback_query: Optional[CallbackQuery] = None
    shipping_query: Optional[Dict[str, Any]] = None
    pre_checkout_query: Optional[PreCheckoutQuery] = None
    poll: Optional[Dict[str, Any]] = None
    poll_answer: Optional[Dict[str, Any]] = None
    my_chat_member: Optional[Dict[str, Any]] = None
    chat_member: Optional[Dict[str, Any]] = None
    chat_join_request: Optional[Dict[str, Any]] = None 