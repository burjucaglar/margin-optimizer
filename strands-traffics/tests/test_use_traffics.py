import json
import os
from unittest.mock import patch

import responses

from strands_traffics.use_traffics import use_traffics


def test_discovery_services():
    """Test discovering all available services."""
    res = use_traffics(service="_", endpoint="_")
    assert res["status"] == "success"
    content = res["content"][0]["json"]
    
    # Check that categories exist
    assert "hotels" in content["available_services"]
    assert "offers" in content["available_services"]
    assert "bookings" in content["available_services"]
    
    # Check previews
    assert "hotels" in content["preview"]


def test_discovery_endpoints():
    """Test discovering endpoints within a service."""
    res = use_traffics(service="hotels", endpoint="_")
    assert res["status"] == "success"
    content = res["content"][0]["json"]
    
    # Check that it returns endpoints for the hotels service
    assert content["service"] == "hotels"
    eps = content["available_endpoints"]
    
    # Should have main search and details
    assert "main" in eps
    assert eps["main"]["path"] == "/hotels"
    
    assert "get_by_id" in eps
    assert eps["get_by_id"]["path"] == "/hotels/{giataId}"


def test_missing_service():
    """Test with an invalid service name."""
    res = use_traffics(service="invalid_service", endpoint="_")
    assert res["status"] == "error"
    assert "not found" in res["content"][0]["text"]


def test_missing_endpoint():
    """Test with an invalid endpoint name."""
    res = use_traffics(service="hotels", endpoint="invalid_endpoint")
    assert res["status"] == "error"
    assert "not found" in res["content"][0]["text"]


def test_missing_required_params():
    """Test validation of required parameters."""
    # /hotels requires productType and adults
    res = use_traffics(service="hotels", endpoint="main", params='{"productType": "pauschal"}')
    assert res["status"] == "error"
    assert "Missing required parameters" in res["content"][0]["text"]
    assert "adults" in res["content"][0]["text"]


@responses.activate
def test_successful_request():
    """Test a successful mocked request."""
    # Mock the Connector API response
    responses.add(
        responses.GET,
        "https://connector.traffics.de/v3/rest/hotels",
        json={"hotelList": [{"name": "Test Hotel", "price": 100}]},
        status=200
    )
    
    res = use_traffics(
        service="hotels",
        endpoint="main",
        params='{"productType": "pauschal", "adults": 2}',
        api_key="test-key"
    )
    
    assert res["status"] == "success"
    content = res["content"][0]["json"]
    assert content["result"]["hotelList"][0]["name"] == "Test Hotel"


@responses.activate
def test_path_parameters():
    """Test that path parameters are correctly injected and removed from query."""
    responses.add(
        responses.GET,
        "https://connector.traffics.de/v3/rest/hotels/12345",
        json={"name": "Test Hotel"},
        status=200
    )
    
    res = use_traffics(
        service="hotels",
        endpoint="get_by_id",
        params='{"giataId": 12345, "adults": 2}',  # adults is required for some reason in the spec
        api_key="test-key"
    )
    
    assert res["status"] == "success"
    
    # Check that the request URL was formatted correctly
    assert len(responses.calls) == 1
    url = responses.calls[0].request.url
    assert "/hotels/12345" in url


@patch.dict(os.environ, {}, clear=True)
def test_missing_api_key():
    """Test that API key is required for actual requests."""
    res = use_traffics(
        service="hotels",
        endpoint="main",
        params='{"productType": "pauschal", "adults": 2}'
        # missing api_key
    )
    
    assert res["status"] == "error"
    assert "Authentication error" in res["content"][0]["text"]


def test_param_parsing():
    """Test different param input formats."""
    from strands_traffics.use_traffics import _parse_params
    
    assert _parse_params(None) == {}
    assert _parse_params("") == {}
    assert _parse_params('{"a": 1}') == {"a": 1}
    assert _parse_params({"a": 1}) == {"a": 1}
    assert _parse_params("invalid_json") == {}
