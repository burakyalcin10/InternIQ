📹 VIDEO TOPIC: Building a Multi-Agent System with OpenAI Agents SDK and Model Context Protocol (MCP)
🕐 COVERAGE: Instantiating Multiple MCP Servers, Multi-Agent Collaboration via Tools, Using MCP Resources, and Tracing Agent Execution

**🔹 Instantiating Multiple MCP Servers**
→ The process begins by taking parameters gathered previously into lists (`params`) and using them to instantiate multiple Model Context Protocol (MCP) servers. The instructor loops through these parameters to create `MCPServerStido` instances for each, applying a 30-second `client_session_timeout`. This prepares a collection of distinct MCP servers that the agents will later use to interact with external systems. 

**⭐ 🔹 Multi-Agent Collaboration via Tool Conversion**
→ To create a collaborative multi-agent system, the instructor defines two distinct agents: a **Trader** (responsible for making trading decisions) and a **Researcher** (responsible for conducting deep market research). Based on the OpenAI Agents SDK paradigm, the best way to have one agent use another is to convert the sub-agent (the Researcher) into a tool that the primary agent (the Trader) can call. The Trader treats the Researcher exactly like any other function or API tool.
> ⭐ **EXAM NOTE:** This is a fundamental design pattern in the OpenAI Agents SDK for multi-agent architecture: treating sub-agents as tools. You must know that to enable agent collaboration, you expose one agent as a callable tool to another.

**⭐ 🔹 Prompt Engineering: Injecting Context vs. Tool Lookups**
→ When defining the Researcher agent's system prompt, the instructor explicitly passes the current date (`datetime.now()`) directly into the instructions. This is a deliberate design choice: instead of giving the agent a tool to look up the current date, providing it upfront saves the agent from having to make an unnecessary tool call. This reduces complexity, saves tokens, and speeds up execution.
> ⭐ **EXAM NOTE:** This highlights a crucial best practice in agent design: if a piece of context is known statically at runtime (like the current date or user ID), inject it directly into the prompt rather than forcing the agent to use a tool to fetch it.

**⭐ 🔹 The `as_tool()` Method**
→ To convert the Researcher agent into a tool, the instructor uses the `as_tool()` method provided by the SDK. When doing this, it is critical to provide a clear `name` and a detailed `description`. The description is what the primary agent (the Trader) reads to understand *when* and *why* it should use this tool, making it the mechanism that drives the agentic handoff.
```python
researcher_tool = await get_researcher_tool()
tool = researcher_tool.as_tool(
    name="Researcher",
    description="This tool researches online for news and opportunities...\nDescribe what kind of research you're looking for."
)
```
> ⭐ **EXAM NOTE:** You must know that `as_tool()` is the SDK method used to wrap an agent into a tool, and that the `description` parameter is the sole piece of context the LLM uses to decide whether to trigger that handoff.

**🔹 Handling Multiple MCP Server Connections**
→ Normally, a single MCP server connection is managed using a context manager (`with` statement). However, because this system uses a list of multiple MCP servers, nesting multiple `with` blocks would result in clunky, deeply indented code. Instead, the instructor iterates through the list of servers and calls `await server.connect()` directly. (Note: The instructor mentions that in a production environment, you must ensure proper cleanup/disconnection, though it matters less in a persistent Jupyter environment).
```python
for server in researcher_mcp_servers:
    await server.connect()
```

**⭐ 🔹 Controlling Agent Execution Limits (`max_turns`)**
→ When running the agent using `Runner.run()`, the instructor explicitly passes a `max_turns` parameter. The default value is 10, meaning the agent can execute a maximum of 10 sequential tool calls before the SDK forcefully halts it. Because the Researcher agent is expected to do deep, iterative web searching, `max_turns` is increased to 30. Conversely, if you want to prevent an agent from getting stuck in an infinite loop of overthinking, you would lower this number.
```python
result = await Runner.run(researcher, research_question, max_turns=30)
```
> ⭐ **EXAM NOTE:** Understanding `max_turns` is critical for controlling agent execution loops. It is the primary safeguard against infinite agent loops and must be tuned based on the complexity of the task (e.g., deep research requires higher turns).

**🔹 Reviewing Agent Actions via Traces**
→ After running the Researcher agent directly to test it, the instructor uses the OpenAI Platform Traces dashboard to inspect the agent's behavior behind the scenes. The trace visually displays the sequence of tool calls, showing the agent repeatedly using `brave_web_search` followed by `fetch` to read specific web pages, demonstrating the iterative reasoning and action loop.

**🔹 Agent Autonomy through Stored Strategies**
→ When setting up the Trader agent (named "Ed"), the instructor assigns it an initial trading strategy ("You are a day trader that aggressively buys and sells shares..."). This strategy is stored externally within the agent's account data rather than hardcoded in the script. The reasoning is to grant the agent autonomy: by storing the strategy externally, the agent can be given permission to evolve or change its own strategy in the future based on market performance.

**⭐ 🔹 MCP Resources vs. MCP Tools**
→ To retrieve the Trader's strategy and account balance, the instructor utilizes **MCP Resources**. While MCP *Tools* allow an agent to take actions, MCP *Resources* allow the MCP server to expose read-only data or business logic directly to the client. The Python script calls the MCP client, which asks the MCP server for these specific resources (account details and strategy).
> ⭐ **EXAM NOTE:** You must clearly understand the distinction in the Model Context Protocol: **Tools** are callable functions that perform actions or fetch real-time data, while **Resources** are structured, read-only data assets exposed by the server.

**⭐ 🔹 Injecting MCP Resources into Prompts**
→ Once the MCP Resources (account details and strategy) are retrieved, how are they used by the agent? The instructor explains that resources are simply text that you "shove in the prompt." The data is injected directly into the Trader agent's system instructions to give it the context required to make decisions. Furthermore, the resources are provided in JSON format because "LLMs love JSON" and parse it highly effectively.
```python
instructions = f"""
...
Your investment strategy for your portfolio is:
{strategy}

Your current holdings and balance is:
{account_details}
...
"""
```
> ⭐ **EXAM NOTE:** Knowing *how* to utilize an MCP Resource is a key concept. Unlike a tool which the LLM chooses to invoke, a Resource is fetched by the application layer and injected directly into the LLM's system prompt to provide immediate context.

**🔹 The Complete Multi-Agent Run Execution**
→ The instructor instantiates the final Trader `Agent`, passing in its system instructions, the `researcher_tool` (the Researcher agent wrapped as a tool), and the list of `mcp_servers` (containing the specific trading tools). The `Runner.run` function is called with `max_turns=30`. The agent takes significant time to run because it delegates to the Researcher (which browses the web) and then formulates its own trading actions. The final output includes a structured markdown summary of:
1. Research Findings (macroeconomic context).
2. Trades Executed (buying and selling Disney stock).
3. Current Portfolio Status.
4. Next Steps (monitoring other stocks like Tesla).

**🔹 Verifying State Mutation via Traces and Resources**
→ The instructor reviews the final trace to prove the multi-agent hierarchy worked. The trace shows the parent "Ed" agent delegating a massive block of time to the "Researcher" agent. Once the Researcher finishes, "Ed" uses its own direct MCP tools: `list_tickers`, `get_last_trade`, `get_daily_open_close_agg`, and finally mutates state using `buy_shares` and `sell_shares`. To verify this state mutation, the instructor runs the `read_accounts_resource` command again, proving the cash balance decreased and the portfolio holdings updated successfully.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. Multi-Agent Collaboration via Tool Conversion
2. Prompt Engineering: Injecting Context vs. Tool Lookups
3. The `as_tool()` Method
4. Controlling Agent Execution Limits (`max_turns`)
5. MCP Resources vs. MCP Tools
6. Injecting MCP Resources into Prompts