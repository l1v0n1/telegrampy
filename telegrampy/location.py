"""
Location services module for Telegram bots.
"""
import logging
from typing import Optional, Dict, Any, List, Tuple
from math import radians, sin, cos, sqrt, atan2
from .types import Message, Location
from .keyboard import KeyboardBuilder

logger = logging.getLogger(__name__)

class LocationHandler:
    """
    Handler for location-based services.
    
    Attributes:
        default_radius (float): Default search radius in kilometers
        max_radius (float): Maximum search radius in kilometers
        min_radius (float): Minimum search radius in kilometers
    """
    
    def __init__(
        self,
        default_radius: float = 5.0,
        max_radius: float = 50.0,
        min_radius: float = 0.1
    ):
        """
        Initialize the location handler.
        
        Args:
            default_radius (float): Default search radius in kilometers
            max_radius (float): Maximum search radius in kilometers
            min_radius (float): Minimum search radius in kilometers
        """
        self.default_radius = default_radius
        self.max_radius = max_radius
        self.min_radius = min_radius
        
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1 (float): First point latitude
            lon1 (float): First point longitude
            lat2 (float): Second point latitude
            lon2 (float): Second point longitude
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
        
    def is_within_radius(
        self,
        center: Location,
        point: Location,
        radius: float
    ) -> bool:
        """
        Check if a point is within a given radius of a center point.
        
        Args:
            center (Location): Center location
            point (Location): Point to check
            radius (float): Radius in kilometers
            
        Returns:
            bool: True if point is within radius
        """
        distance = self.calculate_distance(
            center.latitude,
            center.longitude,
            point.latitude,
            point.longitude
        )
        return distance <= radius
        
    def create_location_keyboard(
        self,
        location: Location,
        radius: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a keyboard for requesting location.
        
        Args:
            location (Location): Current location
            radius (Optional[float]): Search radius
            
        Returns:
            Dict[str, Any]: Keyboard markup
        """
        radius = radius or self.default_radius
        radius = max(min(radius, self.max_radius), self.min_radius)
        
        builder = KeyboardBuilder()
        builder.add_button(
            text="📍 Share Location",
            request_location=True
        )
        
        return builder.build().to_dict()
        
    def create_venue_keyboard(
        self,
        venues: List[Dict[str, Any]],
        location: Location
    ) -> Dict[str, Any]:
        """
        Create a keyboard for displaying venues.
        
        Args:
            venues (List[Dict[str, Any]]): List of venues
            location (Location): Current location
            
        Returns:
            Dict[str, Any]: Keyboard markup
        """
        builder = KeyboardBuilder()
        
        for venue in venues:
            distance = self.calculate_distance(
                location.latitude,
                location.longitude,
                venue["location"]["latitude"],
                venue["location"]["longitude"]
            )
            
            text = f"{venue['title']} ({distance:.1f}km)"
            builder.add_button(text=text, callback_data=f"venue_{venue['id']}")
            
        return builder.build().to_dict()
        
    def format_location_message(
        self,
        location: Location,
        venues: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Format a message with location information.
        
        Args:
            location (Location): Location to format
            venues (Optional[List[Dict[str, Any]]]): List of nearby venues
            
        Returns:
            str: Formatted message
        """
        message = f"📍 Location: {location.latitude}, {location.longitude}"
        
        if venues:
            message += "\n\nNearby venues:"
            for venue in venues:
                distance = self.calculate_distance(
                    location.latitude,
                    location.longitude,
                    venue["location"]["latitude"],
                    venue["location"]["longitude"]
                )
                message += f"\n• {venue['title']} ({distance:.1f}km)"
                
        return message
        
    def parse_location_message(
        self,
        message: Message
    ) -> Optional[Location]:
        """
        Parse location from a message.
        
        Args:
            message (Message): Message to parse
            
        Returns:
            Optional[Location]: Parsed location
        """
        if message.location:
            return message.location
        elif message.venue:
            return message.venue.location
        elif message.text:
            try:
                # Try to parse coordinates from text
                lat, lon = map(float, message.text.split(","))
                return Location(latitude=lat, longitude=lon)
            except:
                pass
        return None
        
    def validate_location(
        self,
        location: Location
    ) -> bool:
        """
        Validate a location.
        
        Args:
            location (Location): Location to validate
            
        Returns:
            bool: True if location is valid
        """
        try:
            return (
                -90 <= location.latitude <= 90 and
                -180 <= location.longitude <= 180
            )
        except:
            return False
            
    def get_bounding_box(
        self,
        center: Location,
        radius: float
    ) -> Tuple[Location, Location]:
        """
        Get bounding box for a location and radius.
        
        Args:
            center (Location): Center location
            radius (float): Radius in kilometers
            
        Returns:
            Tuple[Location, Location]: Southwest and northeast corners
        """
        # Convert radius to degrees (approximate)
        lat_radius = radius / 111.32  # 1 degree = 111.32 km
        lon_radius = radius / (111.32 * cos(radians(center.latitude)))
        
        southwest = Location(
            latitude=center.latitude - lat_radius,
            longitude=center.longitude - lon_radius
        )
        northeast = Location(
            latitude=center.latitude + lat_radius,
            longitude=center.longitude + lon_radius
        )
        
        return southwest, northeast 