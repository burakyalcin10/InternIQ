📹 VIDEO TOPIC:
🕐 COVERAGE: Debugging Agent Traces, Development Lifecycle Best Practices, and Python Module Organization for MCP Servers and Prompts.

**🔹 Debugging Agent Actions via Traces**
→ When an agent fails to perform an expected action (such as buying a specific stock like Tesla), the first step is to inspect the execution traces (e.g., via `platform.openai.com/traces`). In the demonstrated scenario, the trace revealed that the agent attempted to execute the `buy_shares` tool but received a specific error: `"Error executing tool buy_shares: Insufficient funds to buy shares."` 
This highlights the importance of well-designed tool error messages. Because a previous "crew of agents" (from a prior development phase) implemented a strict business requirement to prevent overdrafts, the tool correctly blocked the action and returned a descriptive error. The agent processed this error, understood why the purchase failed, and naturally omitted the failed Tesla purchase from its final summary.

**⭐ 🔹 Best Practices for Building Agentic Workflows (Lab vs. Code)**
→ A critical philosophy for building agentic frameworks and solving business problems with AI is the development lifecycle approach: **Always start in the lab.** 
When tasked with a commercial problem, a common mistake developers make is immediately diagramming complex, multi-agent architectures and writing raw Python modules. This often leads to failure and frustration when the agents don't behave as intended. 
Instead, developers must wear their "data science hat" and begin in an experimental environment like a Jupyter Notebook. This "lab" phase is strictly for experimenting with prompts, testing different agent configurations, and finding the right balance between **autonomy** and **coherence**. Only after the agent's behavior is proven reliable in the notebook should the solution be extracted and refactored into formal Python modules.

> ⭐ **EXAM NOTE:** This is a foundational methodology for agent engineering. Questions may test your understanding of the agent development lifecycle, specifically why prompt experimentation in a notebook must precede complex architectural coding to ensure the balance of autonomy and coherence.

**⭐ 🔹 MCP Server Configuration and Role-Specific Assignment (`mcp_params.py`)**
→ To maintain clean code and separate concerns, MCP server configurations should be extracted into a dedicated file (e.g., initially misnamed as `mcp_servers.py` but corrected to `mcp_params.py`). While Python doesn't force this separation, it is an organized way to keep server definitions tidy.
This file defines which tools and servers are provided to different agents based on their specific roles:
1. **Market Data Configuration**: The code uses an `if/else` block based on environment variables to select the market data source. It can either use the official `polygon_mcp` server, or a custom-built `market_server.py` designed to cache results and prevent exceeding the free tier limits of the Polygon.io API.
2. **Trader MCP Servers**: The execution agent (Trader) is equipped with:
   - `accounts_server.py`: A homegrown server for managing account data.
   - `push_server.py`: A homegrown server for sending push notifications.
   - The selected Market Data MCP server.
3. **Researcher MCP Servers**: The analysis agent (Researcher) is equipped with a distinct set of servers suited for discovery:
   - `mcp-server-fetch`: Uses a headless Playwright browser behind the scenes to fetch web pages.
   - `server-brave-search`: A free API tool for conducting web searches.
   - `mcp-memory-sqlite`: An SQL-based memory server.

> ⭐ **EXAM NOTE:** You must understand the architectural pattern of assigning role-specific MCP servers to specialized agents (e.g., giving execution tools to a Trader and search/memory tools to a Researcher). Additionally, using a custom caching MCP server to bypass API rate limits is a practical production pattern.

**⭐ 🔹 Agent Memory Isolation Strategy**
→ When configuring the `mcp-memory-sqlite` server for multiple agents, it is crucial to maintain isolated memory banks so agents do not cross-contaminate their learned context. This is achieved by dynamically naming the SQLite database file based on the specific agent's name. 
```python
"args": ["run", "mcp-memory-sqlite"],
"env": {"SQLITE_URL": f"file:{name}.db"}
```
By passing the `name` variable into the configuration, every distinct Researcher/Trader pair gets its own isolated SQLite database file.

> ⭐ **EXAM NOTE:** Memory isolation is a vital concept in multi-agent systems. Passing dynamic identifiers (like an agent's name) to the memory MCP server ensures state separation between autonomous entities.

**⭐ 🔹 Prompt Management and Separation of Concerns (`templates.py`)**
→ To keep the core application logic clean, all text-heavy instructions, system prompts, and tool descriptions should be moved to a dedicated file named `templates.py`. This module consists of functions that return formatted strings (e.g., `researcher_instructions()`, `research_tool()`, `trader_instructions(name: str)`).
Highly "opinionated frameworks" enforce this separation automatically. For example, CrewAI forces developers to store prompts in external `YAML` files, taking the text completely out of the code. When building a custom framework, developers must self-enforce this discipline by using a templates module, ensuring there is a single centralized location to edit and manage agent prompts.

> ⭐ **EXAM NOTE:** Architectural design patterns regarding the separation of text/prompts from execution logic are highly testable. Know the difference between how opinionated frameworks (CrewAI using YAML) vs custom frameworks (using a dedicated `templates.py` module) handle prompt management.

**⭐ 🔹 Dynamic Context Injection vs. Tool Usage**
→ Inside `templates.py`, a powerful optimization technique is used to provide the agent with current environmental context without forcing the agent to use a tool. 
Instead of equipping the agent with a "get_current_date" tool (which costs tokens, execution time, and introduces potential failure points), the exact current date and time are dynamically injected directly into the prompt string using Python:
```python
The current datetime is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
```
Similarly, real-time state variables like the agent's `name`, its assigned `strategy`, and its `account` details are injected directly into the prompt text before passing it to the LLM.

> ⭐ **EXAM NOTE:** This is a critical performance and reliability optimization pattern. Providing deterministic context (like the current date/time or static account details) via string injection is vastly superior to making the LLM waste reasoning cycles and API calls trying to fetch that data via an MCP tool.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. Best Practices for Building Agentic Workflows (Lab vs. Code)
2. MCP Server Configuration and Role-Specific Assignment (`mcp_params.py`)
3. Agent Memory Isolation Strategy
4. Prompt Management and Separation of Concerns (`templates.py`)
5. Dynamic Context Injection vs. Tool Usage