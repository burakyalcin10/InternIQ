📹 VIDEO TOPIC: AI Engineer Agentic Track: The Complete Agent & MCP Course
🕐 COVERAGE: Building an Autonomous Trading Agent, Managing Multiple MCP Servers, and Tracing Agentic Workflows

---

**🔹 The `traders.py` Module Overview**
→ The `traders.py` module serves as the core Python file where the autonomous trader agents are defined. It takes the concepts and code previously explored in Jupyter notebook labs and packages them into a clean, reusable Python module. The primary goal of this module is to establish an autonomous trader that can independently alternate between executing trades and rebalancing a portfolio, while utilizing a secondary researcher agent and a wide array of Model Context Protocol (MCP) tools to make informed decisions.

**⭐ 🔹 Handling Multiple MCP Servers with `AsyncExitStack`**
→ When working with the OpenAI Agents SDK and connecting to multiple MCP servers, the standard approach is to use asynchronous context managers (`async with`). If an agent requires access to many servers (e.g., three or more), nesting these context managers creates deeply indented, hard-to-read, and "ugly" code (often referred to as the "pyramid of doom"). 
To solve this and dynamically load multiple servers, the instructor introduces an advanced Python technique using `contextlib.AsyncExitStack`. This construct allows you to iterate over a list of server parameters and enter their context managers programmatically without nesting.

```python
# The "ugly" nested way:
async with MCPServerStudio(params1) as mcp_server1:
    async with MCPServerStudio(params2) as mcp_server2:
        async with MCPServerStudio(params3) as mcp_server3:
            mcp_servers = [mcp_server1, mcp_server2, mcp_server3]

# The clean, dynamic way using AsyncExitStack:
from contextlib import AsyncExitStack

async with AsyncExitStack() as stack:
    mcp_servers = [
        await stack.enter_async_context(MCPServerStudio(params)) 
        for params in mcp_server_params
    ]
```
While both methods are functionally equivalent, the `AsyncExitStack` approach is significantly neater and scales infinitely without altering the code structure.

> ⭐ **EXAM NOTE:** Understanding how to dynamically initialize multiple MCP servers without deep nesting is critical for scaling agentic architectures. `AsyncExitStack` is the standard Python pattern for managing dynamic lists of asynchronous context managers.

**⭐ 🔹 Model Agnosticism and Provider Switching**
→ A robust agentic system should not be locked into a single LLM provider. At the top of the `traders.py` module, the code includes logic to switch between different models and providers effortlessly. Rather than relying exclusively on OpenAI, the application can route requests to DeepSeek, Grok, Google, or use OpenRouter (an aggregation service) to connect to any model of choice. The `get_model` function evaluates the configured model string and automatically initializes the correct client provider. 

> ⭐ **EXAM NOTE:** Model Agnosticism (the ability to swap foundational models via tools like OpenRouter without rewriting agent logic) is a core design principle in modern AI engineering to ensure fault tolerance and cost optimization.

**🔹 The `Trader` Class Architecture**
→ The module packages the agent logic into a structured `Trader` class. When a new instance of this class is created (e.g., `trader = Trader("Ed")`), it is instantiated with a specific name, an assigned LLM model, and an underlying OpenAI SDK agent object. Because the agent is given the name "Ed", it is specifically programmed to look up and interact with the financial accounts associated with "Ed" via the MCP resources. The `Trader` class encapsulates both the primary trading agent and the secondary `Researcher` agent (which acts as a tool for the trader).

**⭐ 🔹 State Management: Alternating Behaviors (Trade vs. Rebalance)**
→ To make the trader truly autonomous and capable of handling multiple distinct responsibilities, a simple state management mechanism is introduced using a boolean flag (`self.do_trade`). The agent alternates its behavior between making aggressive trading decisions and optimizing/rebalancing its portfolio.
1. When the `run` method is triggered, it checks the `self.do_trade` flag.
2. If `True`, the agent is prompted with a "trade" message (instructing it to evaluate the market and buy/sell).
3. If `False`, the agent is prompted with a "rebalance" message (instructing it to optimize its current portfolio).
4. At the very end of the `run` execution, the flag is inverted (`self.do_trade = not self.do_trade`), ensuring the opposite behavior occurs on the next cycle.

```python
async def run(self):
    try:
        # ... execution logic ...
        if self.do_trade:
            # Trigger trade message
        else:
            # Trigger rebalance message
            
        # Flip the flag for the next iteration
        self.do_trade = not self.do_trade
    except Exception as e:
        print(f"Error running trader")
```

> ⭐ **EXAM NOTE:** This alternating boolean flag is a foundational example of implementing a state machine within an agentic loop. It proves how simple application-level logic can guide an LLM to perform distinct, alternating workflows autonomously.

**🔹 Execution and Tracing the Agentic Workflow**
→ In the Jupyter lab, the instructor instantiates the trader (`trader = Trader("Ed")`) and executes it using `await trader.run()`. To understand exactly what the autonomous agent is doing under the hood, they review the execution trace in the OpenAI platform (`platform.openai.com/traces`). The trace reveals a complex, multi-step orchestration:
1. **List MCP Tools:** The agent first fetches all available tools.
2. **Delegation:** The Trader agent calls the `Researcher` agent as a tool.
3. **Research:** The Researcher agent independently triggers a `brave_web_search` tool to gather market context, then returns the data to the Trader.
4. **Market Analysis:** The Trader regains control and repeatedly calls `get_snapshot_ticker` to check real-time prices for specific stocks (Amazon, Apple, Microsoft).
5. **Execution:** The Trader sequentially calls the `buy_shares` tool for Amazon, Apple, and Microsoft. It then calls the `sell_shares` tool to offload Spotify shares to gain liquidity.
6. **Notification:** Finally, the agent calls a `push` tool to send a push notification to the user's phone summarizing the executed trades.

**⭐ 🔹 Tool Execution Errors and Return Values**
→ After the 48-second execution, the platform outputs a warning: `Error running tool` specifically tied to the final push notification tool. However, the instructor confirms that the push notification successfully arrived on their mobile device. The instructor deduces that the error occurred because the Python function defining the push tool did not include a `return` statement (it did not return a string or confirmation payload back to the LLM).

> ⭐ **EXAM NOTE:** This is a critical concept in MCP and tool calling: even if a tool's side-effect (e.g., updating a database, sending a message) succeeds, the function MUST return a value (usually a string or JSON) back to the agent. Failure to return a value will cause the LLM framework to register a tool execution error.

**🔹 Verifying Agent Actions via Resources**
→ To prove the agent actually performed the actions seen in the trace, the instructor calls `await read_accounts_resource("Ed")`. The output confirms the state changes: the portfolio's cash balance has been adjusted, the holdings now include the newly purchased Amazon shares, and the transaction history is accurately logged. This demonstrates the seamless integration between the agent's tool calls and the underlying database/resource state.

**🔹 Scaling Tools: Evaluating the Total MCP Tool Count**
→ To highlight the power of the MCP architecture, the instructor runs a short script to count exactly how many tools were made available to the system. By importing `trader_mcp_server_params` and `researcher_mcp_server_params`, iterating through them via an `AsyncExitStack`, and counting the output of `await mcp_servers.list_tools()`, the system reveals it is connected to **6 MCP servers** providing a massive total of **44 tools** to the agents.

**🔹 Course Conclusion and Next Steps**
→ The instructor concludes the technical review of the code by urging students to replicate the lab, deeply study `traders.py`, and experiment by modifying the system prompts located in `templates.py`. Altering the prompt will directly change the trading persona (e.g., from an aggressive day trader to a conservative long-term investor). For students with financial backgrounds, adding more specialized tools is highly encouraged. Finally, the instructor teases the upcoming "Day 5" module, which will feature a full UI/platform integration and a comprehensive comparative summary of all the agent frameworks (AutoGen, LangGraph, CrewAI, OpenAI SDK) covered in the course.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. **Handling Multiple MCP Servers with `AsyncExitStack`**
2. **Model Agnosticism and Provider Switching**
3. **State Management: Alternating Behaviors (Trade vs. Rebalance)**
4. **Tool Execution Errors and Return Values**