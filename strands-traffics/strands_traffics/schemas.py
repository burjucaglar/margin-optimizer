"""
Response parsing helpers for Traffics Connector API v3.
The API defines 169 schemas. Since responses are returned dynamically as raw JSON,
these utilities can help extract common data safely without running into KeyError issues.
"""

from typing import Any, Dict, List, Optional


def extract_hotels(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Safe extraction of hotel lists from search responses."""
    if not isinstance(response, dict):
        return []
    
    # Traffics API returns hotels under 'hotelList' usually
    return response.get("hotelList", [])


def extract_offers(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Safe extraction of offer lists from offer search responses."""
    if not isinstance(response, dict):
        return []
        
    return response.get("offerList", [])


def get_cheapest_offer(offers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find the cheapest offer in a list of Traffics offers."""
    if not offers:
        return None
        
    def get_price(offer):
        # Different offer types store price slightly differently
        try:
            return offer.get("price", {}).get("total", float("inf"))
        except (AttributeError, TypeError):
            # Try flat price attribute
            return offer.get("price", float("inf"))
            
    try:
        return min(offers, key=get_price)
    except Exception:
        return None


def extract_error_message(response: Dict[str, Any]) -> str:
    """Extract human-readable error messages from Traffics 400/500 responses."""
    if not isinstance(response, dict):
        return str(response)
        
    if "error" in response and isinstance(response["error"], dict):
        return response["error"].get("message", "Unknown API error")
        
    return response.get("message", "Unknown error structure")
