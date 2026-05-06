📹 VIDEO TOPIC: AI Agents & MCP Architecture Types
🕐 COVERAGE: Implementing Brave Search API (Architecture Type 2) vs. Remote MCP Servers via SSE (Architecture Type 3)

***

**🔹 Previous Internet Search Tools Context**
→ In previous weeks of the course, internet search capabilities for agents were handled using various hosted tools. For instance, the hosted tool with OpenAI used in Week 2 was quite expensive, costing 2.5 cents for every single web search. Other alternatives previously used include Tavily and Serper. The instructor introduces a new, highly cost-effective alternative for the current module.

**🔹 Brave Search API**
→ The Brave Search API is provided by a company that specializes in API-driven searches, which makes it highly optimized for use with AI agents. 
- **Cost / Free Tier:** It features a very generous free tier, allowing up to 2,000 free searches per month without requiring a credit card for setup.
- **Setup:** Users simply create a free account, generate an API key, and place it into their `.env` file under the variable name `BRAVE_API_KEY`. 

**⭐ 🔹 Architecture Type 2: Local MCP Server Calling a Web Service**
→ This is a crucial architectural pattern for MCP (Model Context Protocol). In this architecture, the MCP server software runs locally on your machine, but the code it executes reaches out to make API calls to a remote web service in the cloud. 
- **How it runs:** The code is fetched and executed locally using Node package executer (`npx`).
- **How it connects:** The local server takes your local API credentials and securely passes them in a web call to the remote service (e.g., Brave's servers) to retrieve data.
- **Implementation:** The instructor uses Anthropic's out-of-the-box reference implementation for Brave Search.

> ⭐ **EXAM NOTE:** You must understand the distinction of a "Type 2" architecture. The MCP server itself is a local process (using npx), but its primary function is serving as a localized bridge to a remote cloud API. 

**🔹 Passing Environment Variables to MCP Servers**
→ When configuring an MCP server that requires API keys, you must explicitly pass those keys into the server's environment parameters. This is a new twist introduced in this module.
```python
env = {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}

params = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": env
}

async with MCPServerStudio(params=params) as server:
    mcp_tools = await server.list_tools()
```
- **Explanation:** The `.env` file is loaded into the OS environment. The `os.getenv` command retrieves it, and it is explicitly mapped to the `env` argument inside the `params` dictionary so the JavaScript-based MCP server (`npx`) can access it during initialization.

**🔹 Brave Search MCP Tools**
→ Once the Brave MCP server is initialized, it exposes two specific tools to the agent:
1. `brave_web_search`: Performs a general web search using the API, returning web, news, or article results.
2. `brave_local_search`: Searches for local businesses and places using Brave's Local Search API. *(Note: The instructor points out this specific local search feature likely requires a paid Brave API plan to function).*

**⭐ 🔹 Comparison: Fetch Tool vs. Brave Search Tool**
→ Understanding the mechanical difference between a web fetcher and a search API is critical for agent tool design.
- **Fetch Tool:** Runs a headless browser process locally. It navigates directly to a specific provided URL/web address and scrapes or reads the content.
- **Brave Search Tool:** Does not run a browser. It makes an API call to Brave, asking its proprietary search engine to run a query (similar to a Google search) and returns a structured list of relevant results.

> ⭐ **EXAM NOTE:** This comparison highlights the difference between "navigation/scraping" (Fetch) and "querying/discovery" (Brave API). Be prepared to identify which tool is appropriate given a specific agentic requirement.

**🔹 Executing the Brave Search Query & Tracing**
→ The instructor tests the tool by asking the agent to "search the web for information... research the latest news on Amazon stock price and briefly summarize its outlook." 
- The agent is provided the current date via Python's `datetime` module to ensure context.
- The agent successfully utilizes `brave_web_search`, retrieves the current price ($217), and outputs a summary.
- **Checking the Trace:** The instructor goes to `platform.openai.com/traces` to verify the execution. The trace confirms the agent explicitly routed the function call to `brave_web_search` with the query `"Amazon stock price news May 2025"`.

**⭐ 🔹 Architecture Type 3: Remote MCP Servers (SSE)**
→ In this architecture, the MCP Server does **not** run locally at all. Instead, the MCP server is hosted entirely remotely in the cloud, and your local client/agent connects to it using the **SSE (Server-Sent Events)** approach.
- **Characteristics:** It is currently *not* a common model for sharing or using MCP servers. 
- **Reliability:** It is considered somewhat "flaky." Because the server is hosted by a third party, there are no guarantees the host will keep the server running continuously. The instructor notes he previously had an example of a free hosted Type 3 server, but it went offline and could no longer be demoed.

> ⭐ **EXAM NOTE:** Type 3 architectures are defined by remote hosting of the MCP server itself and connection via SSE. You must know why it is less common (reliability/uptime issues) compared to Type 2 (local server, remote API).

**🔹 Commercial / Enterprise Examples of Type 3 Servers**
→ While rare in open-source, Type 3 Remote MCP Servers are utilized by paid business services and enterprise platforms. Because these are professional subscriptions, the provider maintains the server infrastructure.
- According to the Anthropic documentation, several companies have deployed remote servers that developers can connect to.
- **Examples mentioned:** 
  - **Asana:** Interact with workspace data (URL example: `https://mcp.asana.com/sse`).
  - **Intercom:** Access customer conversations and tickets.
  - **PayPal:** Integrate commerce capabilities (requires professional commerce accounts, not just personal).
  - **Others:** Square, Workato, Zapier.

**🔹 Deploying Custom Remote MCP Servers via Cloudflare**
→ If you want to build and deploy your *own* Type 3 Remote MCP Server so others can connect to it, you can use **Cloudflare**.
- Cloudflare provides tools and documentation to create and deploy remote MCP workers.
- Once deployed, you are given a specific URL that can be plugged directly into Claude Desktop or the OpenAI Agents SDK to connect remotely.

**⭐ 🔹 Authentication in Remote MCP Servers**
→ When dealing with Type 3 Remote Servers, authentication becomes a critical factor. 
- **Why it matters:** If you deploy a public-facing MCP server on the web, you must ensure that only authorized users/agents can connect to it and invoke tools. 
- **Implementation:** Users must log in or pass specific credentials (like OAuth or specific bearer tokens) to prove their identity before the remote server will accept their SSE connection. This is described as one of the "hot new areas" of MCP development.

> ⭐ **EXAM NOTE:** Authentication is uniquely critical for Type 3 architectures. Because the MCP Server is exposed to the public internet, it requires robust auth layers to prevent unauthorized tool execution.

**🔹 Architecture Summary: Type 2 vs. Type 3**
→ The instructor concludes the comparison by stating that **Type 2** is vastly more common today.
- **Common Workflow (Type 2):** You set up an API key, run the MCP server software locally, and pass the key to it so it can fetch data from the cloud.
- **Enterprise Workflow (Type 3):** You do not run the server locally; you connect to a remote URL maintained by a SaaS provider (like Asana) using SSE and Authentication.
- Transitioning to the next topic, the instructor prepares to use another Type 2 server: the **Polygon.io MCP Server** for financial market data.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. **Architecture Type 2: Local MCP Server Calling a Web Service**
2. **Comparison: Fetch Tool vs. Brave Search Tool**
3. **Architecture Type 3: Remote MCP Servers (SSE)**
4. **Authentication in Remote MCP Servers**