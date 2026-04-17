# strands-traffics

A universal Traffics travel API tool for [Strands Agents](https://github.com/strands-agents/sdk-python). Dynamically access **all 61 endpoints** of the Traffics Connector API v3 through a single tool.

## Installation

```bash
pip install strands-traffics
```

## Quick Start

```python
from strands import Agent
from strands_traffics import use_traffics

# Create an agent with the tool
agent = Agent(tools=[use_traffics])

# Set your API key in environment
# export TRAFFICS_API_KEY="your_api_key"

# Ask the agent to find hotels or any other travel operation
agent("Search for package holidays (pauschal) for 2 adults.")
```

## How It Works

This tool dynamically maps to all Traffics API categories and endpoints. Instead of separate tools for every endpoint, you use single `use_traffics` tool:

| Parameter | Description |
|-----------|-------------|
| `service` | API Category (e.g., `hotels`, `offers`, `regions`, `static`) |
| `endpoint`| Endpoint name (e.g., `main`, `get_by_id`, `calendar`) |
| `params`  | JSON string of query/body/path parameters |
| `api_key` | Optional. If not provided, uses `TRAFFICS_API_KEY` env var |

### Service Discovery

Don't know the exact endpoint? Use `"_"` to discover available capabilities!

```python
# List all 10 service categories
use_traffics(service="_", endpoint="_")

# List all endpoints in the "hotels" category
use_traffics(service="hotels", endpoint="_")
```

## Usage Examples

### Searching Hotels
```python
use_traffics(
    service="hotels",
    endpoint="main",
    params='{"productType": "pauschal", "adults": 2, "departureAirportList": ["BER"], "duration": "7"}'
)
```

### Hotel Details (Path parameters)
Path parameters (like `{giataId}`) are automatically extracted from the `params` object and mapped to the URL.
```python
use_traffics(
    service="hotels",
    endpoint="get_by_id",
    params='{"giataId": 123456, "adults": 2}' # giataId is mapped to the path
)
```

### Finding Offers
```python
use_traffics(
    service="offers",
    endpoint="main",
    params='{"productType": "flight", "adults": 1, "departureAirportList": ["FRA"]}'
)
```

### Reference Data (Static)
```python
use_traffics(service="static", endpoint="airports")
```

## API Features Included

- **Massive Data Protection**: Auto-truncates large API responses (>50KB) so your agent's context window isn't overloaded.
- **Smart Formatting**: Parses path params correctly (e.g. `/hotels/{giataId}` automatically consumes `giataId` from params).
- **Resilience**: Configured with built-in retry logic for rate limits and intermittent server issues.
- **Authentication**: Fully handles the Traffics `apiKey` header.

## Available Service Categories

1. `hotels` — Search, info, reviews, recommendations
2. `offers` — Packages, flights, hotel-only, deals
3. `bookings` — Book offers, check status
4. `regions` — Destinations and regions
5. `static` — Airports, stations, locations, boards
6. `completions` — Autocomplete for search bars
7. `tourOperators` — Tour operator lists
8. `documents` — Visa, forms, requirements
9. `loopback` — Testing / verification
10. `experimental` — Beta features

## License

Apache License 2.0
