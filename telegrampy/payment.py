"""
Payment handling module for Telegram bots.
"""
import logging
from typing import Optional, Dict, Any, List
from .types import Message, PreCheckoutQuery
from .keyboard import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class PaymentHandler:
    """
    Handler for processing payments through Telegram.
    
    Attributes:
        provider_token (str): Payment provider token
        currency (str): Payment currency
        prices (List[Dict[str, Any]]): List of prices
        start_parameter (str): Deep linking parameter
        need_name (bool): Whether to request name
        need_phone_number (bool): Whether to request phone number
        need_email (bool): Whether to request email
        need_shipping_address (bool): Whether to request shipping address
        is_flexible (bool): Whether prices can be adjusted
        send_phone_number_to_provider (bool): Whether to send phone number to provider
        send_email_to_provider (bool): Whether to send email to provider
    """
    
    def __init__(
        self,
        provider_token: str,
        currency: str = "USD",
        prices: Optional[List[Dict[str, Any]]] = None,
        start_parameter: str = "payment",
        need_name: bool = False,
        need_phone_number: bool = False,
        need_email: bool = False,
        need_shipping_address: bool = False,
        is_flexible: bool = False,
        send_phone_number_to_provider: bool = False,
        send_email_to_provider: bool = False
    ):
        """
        Initialize the payment handler.
        
        Args:
            provider_token (str): Payment provider token
            currency (str): Payment currency
            prices (Optional[List[Dict[str, Any]]]): List of prices
            start_parameter (str): Deep linking parameter
            need_name (bool): Whether to request name
            need_phone_number (bool): Whether to request phone number
            need_email (bool): Whether to request email
            need_shipping_address (bool): Whether to request shipping address
            is_flexible (bool): Whether prices can be adjusted
            send_phone_number_to_provider (bool): Whether to send phone number to provider
            send_email_to_provider (bool): Whether to send email to provider
        """
        self.provider_token = provider_token
        self.currency = currency
        self.prices = prices or []
        self.start_parameter = start_parameter
        self.need_name = need_name
        self.need_phone_number = need_phone_number
        self.need_email = need_email
        self.need_shipping_address = need_shipping_address
        self.is_flexible = is_flexible
        self.send_phone_number_to_provider = send_phone_number_to_provider
        self.send_email_to_provider = send_email_to_provider
        
    def add_price(
        self,
        label: str,
        amount: int,
        description: Optional[str] = None
    ) -> None:
        """
        Add a price to the payment.
        
        Args:
            label (str): Price label
            amount (int): Amount in smallest currency unit
            description (Optional[str]): Price description
        """
        price = {"label": label, "amount": amount}
        if description:
            price["description"] = description
        self.prices.append(price)
        
    def create_invoice(
        self,
        title: str,
        description: str,
        payload: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an invoice for payment.
        
        Args:
            title (str): Invoice title
            description (str): Invoice description
            payload (str): Invoice payload
            **kwargs: Additional invoice parameters
            
        Returns:
            Dict[str, Any]: Invoice data
        """
        invoice_data = {
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": self.provider_token,
            "currency": self.currency,
            "prices": self.prices,
            "start_parameter": self.start_parameter,
            "need_name": self.need_name,
            "need_phone_number": self.need_phone_number,
            "need_email": self.need_email,
            "need_shipping_address": self.need_shipping_address,
            "is_flexible": self.is_flexible,
            "send_phone_number_to_provider": self.send_phone_number_to_provider,
            "send_email_to_provider": self.send_email_to_provider
        }
        invoice_data.update(kwargs)
        return invoice_data
        
    def create_payment_button(
        self,
        text: str,
        title: str,
        description: str,
        payload: str,
        **kwargs
    ) -> InlineKeyboardMarkup:
        """
        Create a payment button.
        
        Args:
            text (str): Button text
            title (str): Invoice title
            description (str): Invoice description
            payload (str): Invoice payload
            **kwargs: Additional invoice parameters
            
        Returns:
            InlineKeyboardMarkup: Payment button markup
        """
        invoice_data = self.create_invoice(title, description, payload, **kwargs)
        button = InlineKeyboardButton(
            text=text,
            pay=True,
            **invoice_data
        )
        return InlineKeyboardMarkup([[button]])
        
    async def process_pre_checkout_query(
        self,
        pre_checkout_query: PreCheckoutQuery
    ) -> bool:
        """
        Process a pre-checkout query.
        
        Args:
            pre_checkout_query (PreCheckoutQuery): Pre-checkout query
            
        Returns:
            bool: True if query was processed successfully
        """
        try:
            # Here you would implement your payment validation logic
            # For example, checking stock availability, validating prices, etc.
            
            # For now, we'll just accept all queries
            return True
        except Exception as e:
            logger.error(f"Error processing pre-checkout query: {e}")
            return False
            
    async def process_successful_payment(
        self,
        message: Message
    ) -> None:
        """
        Process a successful payment.
        
        Args:
            message (Message): Message containing payment info
        """
        try:
            # Here you would implement your payment success logic
            # For example, updating database, sending confirmation emails, etc.
            
            # For now, we'll just log the payment
            logger.info(f"Payment successful: {message.successful_payment}")
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            
    def validate_payment_data(
        self,
        payment_data: Dict[str, Any]
    ) -> bool:
        """
        Validate payment data.
        
        Args:
            payment_data (Dict[str, Any]): Payment data to validate
            
        Returns:
            bool: True if data is valid
        """
        try:
            # Here you would implement your payment data validation logic
            # For example, checking required fields, validating amounts, etc.
            
            # For now, we'll just check for required fields
            required_fields = ["currency", "total_amount", "invoice_payload"]
            return all(field in payment_data for field in required_fields)
        except Exception as e:
            logger.error(f"Error validating payment data: {e}")
            return False 