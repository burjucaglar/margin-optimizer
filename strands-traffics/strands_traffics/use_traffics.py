"""
Main tool implementation for Traffics API v3.
Provides access to all 61 endpoints in 10 categories through a single `use_traffics` tool.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from strands import tool

from strands_traffics.client import execute_request
from strands_traffics.endpoints import ENDPOINTS


def _parse_params(params: Optional[str]) -> Dict[str, Any]:
    """Parse JSON params string to dict."""
    if not params:
        return {}
    if isinstance(params, dict):
        return params
    try:
        return json.loads(params)
    except json.JSONDecodeError:
        return {}


def _list_services() -> Dict[str, Any]:
    """Return a discovery map of all available Traffics capabilities."""
    categories = list(ENDPOINTS.keys())
    
    # Show summary of endpoints per category
    summary = {}
    for cat in categories:
        summary[cat] = [
            f"{name} ({ep['method']} {ep['path']})"
            for name, ep in list(ENDPOINTS[cat].items())[:3] # Show max 3 as preview
        ]
        if len(ENDPOINTS[cat]) > 3:
            summary[cat].append(f"... and {len(ENDPOINTS[cat]) - 3} more")
            
    return {
        "status": "success",
        "content": [{
            "json": {
                "available_services": categories,
                "tip": "Set service to one of the above and endpoint to '_' to see all endpoints in that category.",
                "preview": summary
            }
        }]
    }


def _list_endpoints(service: str) -> Dict[str, Any]:
    """List all available endpoints in a specific Traffics service category."""
    if service not in ENDPOINTS:
        return {
            "status": "error",
            "content": [{"text": f"Service '{service}' not found. Available services: {list(ENDPOINTS.keys())}"}]
        }
        
    ep_list = {}
    for name, ep in ENDPOINTS[service].items():
        ep_list[name] = {
            "method": ep["method"],
            "path": ep["path"],
            "summary": ep["summary"],
            "required_params": ep.get("required_params", []),
            "path_params": ep.get("path_params", [])
        }
        
    return {
        "status": "success",
        "content": [{
            "json": {
                "service": service,
                "available_endpoints": ep_list,
                "tip": f"To use an endpoint, call use_traffics(service='{service}', endpoint='<name>') and provide required params."
            }
        }]
    }


@tool
def use_traffics(
    service: str,
    endpoint: str,
    params: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Universal Traffics Connector API v3 client - Access 61 travel endpoints dynamically.
    
    This tool allows interaction with all Traffics travel APIs: hotels, offers, bookings, 
    regions, completions, and more.
    
    Args:
        service: API category (e.g., "hotels", "offers", "bookings", "static", "regions").
                 Pass "_" to discover all 10 available services.
        endpoint: Endpoint name (e.g., "search", "details", "calendar").
                  Pass "_" to list all available endpoints for the specified service.
        params: JSON string of parameters to send (query, body, or path params).
                Example: '{"productType": "pauschal", "adults": 2, "giataId": 1234}'
        api_key: Traffics API key. Defaults to TRAFFICS_API_KEY environment variable.
        
    Returns:
        JSON response with the API result, or error structure.
        
    Authentication:
        You MUST provide an api_key or set TRAFFICS_API_KEY in the environment for actual API 
        calls to succeed. Discovery mode does not require an API key.

    Examples:
        # 1. Discover all service categories
        use_traffics(service="_", endpoint="_")
        
        # 2. Discover all endpoints in the "hotels" category
        use_traffics(service="hotels", endpoint="_")
        
        # 3. Search for hotels (requires params: productType and adults)
        use_traffics(
            service="hotels", 
            endpoint="main", 
            params='{"productType": "pauschal", "adults": 2, "departureAirportList": ["BER"]}'
        )
        
        # 4. Get specific hotel details (requires path param giataId)
        use_traffics(
            service="hotels", 
            endpoint="get_by_id", 
            params='{"giataId": 46522, "adults": 2}'
        )
    """
    
    # Route to discovery mechanisms
    if service == "_":
        return _list_services()
        
    if endpoint == "_":
        return _list_endpoints(service)

    # Validate service exists
    if service not in ENDPOINTS:
        services = list(ENDPOINTS.keys())
        return {
            "status": "error",
            "content": [{"text": f"Service '{service}' not found. Available: {services}. Use service='_' to discover."}]
        }
        
    # Validate endpoint exists
    if endpoint not in ENDPOINTS[service]:
        eps = list(ENDPOINTS[service].keys())
        return {
            "status": "error",
            "content": [{"text": f"Endpoint '{endpoint}' not found in '{service}'. Available: {eps}. Use endpoint='_' to discover."}]
        }
        
    # Validation passed - extract info
    ep_info = ENDPOINTS[service][endpoint]
    call_params = _parse_params(params)
    
    # Check for required parameters
    missing = []
    required_params = ep_info.get("required_params", [])
    
    for req in required_params:
        if req not in call_params:
            missing.append(req)
            
    if missing:
        return {
            "status": "error",
            "content": [{
                "text": f"Missing required parameters for {service}.{endpoint}: {missing}. "
                        f"All required params: {required_params}"
            }]
        }

    # Execute request
    return execute_request(
        method=ep_info["method"],
        path=ep_info["path"],
        params=call_params,
        api_key=api_key
    )
