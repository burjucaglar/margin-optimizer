"""
HTTP client for Traffics Connector API v3.
Handles authentication, exact path parameter parsing, URL generation, and error handling.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

BASE_URL = "https://connector.traffics.de/v3/rest"
SESSION_CACHE = {}


def get_client() -> requests.Session:
    """Create or retrieve a cached requests session with retry logic."""
    if "default" not in SESSION_CACHE:
        session = requests.Session()

        # Add generic headers
        session.headers.update({
            "User-Agent": "strands-traffics-tool/0.1.0",
            "Accept": "application/json",
        })

        # Setup retry strategy (for rate-limiting and timeouts)
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        SESSION_CACHE["default"] = session

    return SESSION_CACHE["default"]


def format_url(path: str, params: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """
    Format URL path with path parameters and separate remaining parameters as query arguments.
    Example: path="/hotels/{giataId}", params={"giataId": 123, "adults": 2}
    Returns: ("/hotels/123", {"adults": 2})
    """
    # Find all path parameters in the format {param}
    path_param_keys = re.findall(r"\{([^}]+)\}", path)
    
    formatted_path = path
    query_params = {**params} if params else {}

    for key in path_param_keys:
        if key not in query_params:
            raise ValueError(f"Missing required path parameter: '{key}'")
        
        # Replace the param in path and remove it from query params
        val = str(query_params.pop(key))
        # Ensure proper URL encoding for path segments
        formatted_path = formatted_path.replace(f"{{{key}}}", quote(val))

    return BASE_URL + formatted_path, query_params


def truncate_response(content: Any, max_size_kb: int = 50) -> Any:
    """
    Truncate large responses to prevent blowing up the agent's context window.
    Particularly useful for Traffics API responses which can be massive.
    """
    if not isinstance(content, (dict, list)):
        return content

    content_str = json.dumps(content)
    # If the response goes past max limit (e.g. lots of elements in lists)
    if len(content_str) > max_size_kb * 1024:
        # If it's a list, truncate the number of items
        if isinstance(content, list):
            # Arbitrarily return first 20 elements
            return content[:20] + [{"_notice": f"Truncated list. Orig length={len(content)}"}]
            
        # If it's a dict, check for large array fields
        if isinstance(content, dict):
            truncated = False
            result = {}
            for k, v in content.items():
                if isinstance(v, list) and len(v) > 50:
                    result[k] = v[:50]
                    truncated = True
                else:
                    result[k] = v
                    
            if truncated:
                result["_notice"] = "Some arrays in the response were truncated to prevent overflow."
                return result
                
        # Fallback for massive single objects
        return {"_error": "Response was too large to process safely (>50KB). Please use more restrictive filters."}

    return content


def execute_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Execute raw HTTP request against Traffics Connector API."""
    
    # Check for authentication
    key = api_key or os.environ.get("TRAFFICS_API_KEY")
    if not key:
        return {
            "status": "error",
            "content": [{"text": "Authentication error: 'TRAFFICS_API_KEY' environment variable or 'api_key' parameter is required. You can use 'service=\"_\"' for discovery without auth."}]
        }

    try:
        session = get_client()
        
        # Parse params into query and path parameters
        url, query_params = format_url(path, params or {})
        
        headers = {
            "Authorization": f"apiKey {key}"  # Traffics API specific auth header format
        }
        
        # Prepare body based on method type 
        req_params = {}
        if method in ("GET", "DELETE"):
            req_params["params"] = query_params
        else:
            req_params["json"] = query_params

        # Send request
        t0 = time.time()
        response = session.request(
            method=method,
            url=url,
            headers=headers,
            timeout=30.0,
            **req_params
        )
        
        duration = int((time.time() - t0) * 1000)

        # Handle errors
        if not response.ok:
            error_msg = response.text
            try:
                error_msg = response.json()
            except ValueError:
                pass
                
            return {
                "status": "error",
                "content": [{
                    "json": {
                        "error": f"HTTP {response.status_code}",
                        "details": error_msg,
                        "url": response.url
                    }
                }]
            }

        # Parse success format
        try:
            result = response.json()
        except ValueError:
            result = {"text": response.text}
            
        # Truncate if response is massive
        safe_result = truncate_response(result)

        return {
            "status": "success",
            "content": [{
                "json": {
                    "ms": duration,
                    "url": response.url,
                    "result": safe_result
                }
            }]
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "content": [{"text": "Request timed out after 30 seconds."}]
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "content": [{"text": f"Request failed: {str(e)}"}]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"Execution error: {str(e)}"}]
        }
