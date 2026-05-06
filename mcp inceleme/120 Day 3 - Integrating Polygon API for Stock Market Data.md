```text
📹 VIDEO TOPIC: Building a Trading Floor - Integrating Polygon.io Market Data into an MCP Server
🕐 COVERAGE: Real market data integration, handling API rate limits via caching, FastMCP server creation, and agent testing.

**🔹 Project Overview: Autonomous Trading Floor**
→ The primary project for this week's course module is to construct a "trading floor" utilizing autonomous agents capable of buying and selling equities. While the account management system and the actual buying/selling execution will remain simulated (using the previously built account management tools), the agents will base their trading decisions on real-world market data. To feed this real market data to the agents, the system will utilize a specific Model Context Protocol (MCP) server.

**🔹 Polygon.io for Financial Market Data**
→ While there are numerous MCP servers available for providing market data, the instructor's preferred choice is a service called Polygon.io. Polygon is a highly popular, well-known professional provider of financial market data. It provides robust APIs to fetch various financial metrics, including stock share prices, which the agents will need to evaluate trades.

**🔹 Polygon.io Plans: Free vs. Paid**
→ Polygon.io offers different tiers of service. Understanding these is critical because it dictates how the API can be queried.
*   **Free Plan**: The instructor highly recommends sticking to the free plan for this course. Under the free plan, the market data provided is end-of-day data, specifically as of the previous day's business close. For example, if queried today, it will return the closing stock prices from yesterday.
*   **Paid Plan**: For users wanting more immediate data, Polygon offers paid plans starting between $20 to $30 a month. This tier provides data on a 15-minute delay but offers unlimited API usage. Higher tiers offer real-time data, but the instructor notes this is unnecessary unless the user is already an active day trader.

**🔹 Setting up Polygon.io API Credentials**
→ To integrate Polygon.io, a specific setup sequence is required to obtain and configure the API key locally:
1. Sign up for an account on Polygon.io.
2. Navigate to the "Keys" section located in the left-hand navigation menu.
3. Click the blue "New Key" button to generate a new API key.
4. Copy the generated key.
5. Open the project's `.env` file and add the key under the variable name `POLYGON_API_KEY`.

To verify the key is loaded correctly in the Python environment, the following code pattern is used:
```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)
polygon_api_key = os.getenv("POLYGON_API_KEY")

# Check if successfully loaded
if not polygon_api_key:
    print("POLYGON_API_KEY is not set")
```

**🔹 Direct Usage of the Polygon REST Client**
→ Before building the MCP server, the instructor demonstrates how to interact directly with Polygon's Python client to fetch a single stock price.
```python
from polygon import RESTClient

# Initialize the client using the API key
client = RESTClient(polygon_api_key)

# Fetch the previous close price for Apple (AAPL)
# The [0] accesses the first item in the returned aggregate data array
client.get_previous_close_agg("AAPL")[0]
```
Running this code returns the previous closing price for Apple, which in the video's example is `$195.27`.

**⭐ 🔹 API Rate Limiting and the Caching Workaround (`market.py`)**
→ The Polygon.io Free Plan enforces strict API rate limiting, allowing only 5 API calls per minute. If an autonomous agent tries to look up multiple individual share prices sequentially, it will rapidly hit this limit, causing the tool to fail and the agent to crash. To solve this, the instructor created a custom wrapper module named `market.py`.
The module employs a "sneaky" caching architecture: Polygon counts a request for a *single* stock price as one API call, but it *also* counts a request for a snapshot of *every single share price in the entire market* as just one API call.
Here is the logical sequence of the `market.py` workaround:
1. An agent requests a specific share price (e.g., AAPL).
2. The `market.py` module checks if the user is on the free plan.
3. Instead of asking Polygon for just AAPL, the module requests the full market snapshot for the prior business day (using 1 out of the 5 allowed API calls).
4. The module saves (caches) this massive dataset locally.
5. It extracts the AAPL price from the cache and returns it.
6. When the agent asks for a second stock (e.g., MSFT), the module bypasses the Polygon API entirely, reads directly from the local cache, and returns the price instantly without consuming any API limits.

To prove the effectiveness of this cache, the instructor loops the price lookup function 1,000 times. Because of the cache, it executes instantly without triggering rate limits.
```python
from market import get_share_price

# Proving the cache works by avoiding the 5 calls/min limit
for i in range(1000):
    get_share_price("AAPL")
```
> ⭐ **EXAM NOTE:** Understanding how to wrap and cache rate-limited external APIs before exposing them as MCP tools is a critical architectural pattern. Direct exposure of strict rate-limited APIs to autonomous agents usually results in failure, as agents operate much faster than humans and may rapidly loop or retry tool calls.

**⭐ 🔹 Creating the `market_server.py` MCP Server**
→ To allow the AI agent to access this safely cached market data, the `market.py` logic must be exposed as an MCP server. The instructor creates a file named `market_server.py` using the `FastMCP` framework. This server takes the complex caching logic from `market.py` and abstracts it, presenting it to the agent as a single, simple tool called `lookup_share_price`.
```python
from mcp.server.fastmcp import FastMCP
from market import get_share_price

# Initialize the FastMCP server with a recognizable name
mcp = FastMCP("market_server")

# Use the decorator to expose this function as an MCP tool
@mcp.tool()
async def lookup_share_price(symbol: str) -> float:
    """This tool provides the current price of the given stock symbol.
    
    Args:
        symbol: The symbol of the stock
    """
    # Calls the cached wrapper function, NOT the Polygon API directly
    return get_share_price(symbol)

# Standard boilerplate to run the server over standard I/O
if __name__ == "__main__":
    mcp.run(transport="stdio")
```
> ⭐ **EXAM NOTE:** You must know the exact syntax for creating a tool using `FastMCP`. The critical requirements are: instantiating `FastMCP`, using the `@mcp.tool()` decorator, providing a clear Python docstring (which becomes the tool description given to the LLM), defining type hints (which generate the JSON schema for tool arguments), and running the server via the `stdio` transport.

**🔹 Testing the MCP Server with an Agent**
→ To conclude, the instructor tests the newly created MCP server by connecting an autonomous agent to it within a Jupyter Notebook environment.
1. The server is launched locally.
2. The tools are verified by calling `await server.list_tools()`.
3. The agent is configured to use the `gpt-4o-mini` model.
4. The agent is provided with instructions: *"You answer questions about the stock market."*
5. The agent is prompted: *"What's the share price of Apple?"*
6. The LLM intelligently maps the word "Apple" to the stock ticker "AAPL".
7. It triggers the `lookup_share_price` MCP tool, passing "AAPL" as the argument.
8. The MCP tool retrieves `$195.27` from the cache and passes it back to the agent.
9. The agent formulates the final natural language response based on the tool's output.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. API Rate Limiting and the Caching Workaround (`market.py`)
2. Creating the `market_server.py` MCP Server (FastMCP Syntax)
```