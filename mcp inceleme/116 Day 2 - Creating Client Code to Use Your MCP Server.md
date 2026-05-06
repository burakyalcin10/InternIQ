📹 VIDEO TOPIC: Building and Using MCP Servers and Custom MCP Clients
🕐 COVERAGE: Running a custom Python MCP Server, integrating it with an LLM Agent, understanding the historical context of MCP clients, building a custom MCP client for tools and resources, JSON schema translation, and practical exercises.

***

**🔹 Running a Custom MCP Server Directly**
→ To run an MCP (Model Context Protocol) server locally, you configure parameters that define exactly how the server should be executed, mimicking how a developer would run it via the command line. The parameters require a `command` and its `args`. In this lab, the instructor uses `uv run` to execute the Python script `accounts_server.py`. 
- **Code representation of the parameters:**
  ```python
  params = {
      "command": "uv",
      "args": ["run", "accounts_server.py"]
  }
  ```
When executed within the script, this spawns a "fast MCP client" that connects to the defined server. 

**⭐ 🔹 The `list_tools()` Function**
→ Once the server is spawned, the client can request a list of all available tools that the server exposes using `await server.list_tools()`. 
- In the video, this returns a list of decorated functions ready for LLM use, including:
  1. `get_balance`
  2. `get_holdings`
  3. `buy_shares`
  4. `sell_shares`
  5. `change_strategy`
> ⭐ **EXAM NOTE:** Understanding how a client discovers tools on a server via `list_tools()` is foundational to MCP architecture. It represents the "discovery" phase of the protocol.

**🔹 Integrating the MCP Server with an OpenAIAgent**
→ After verifying the tools exist, the instructor connects an LLM agent directly to the MCP server. This is done using the `OpenAIAgent` and the `mcp_server_studio` context manager.
- **The Workflow:**
  1. Define explicit instructions (e.g., "You are able to manage an account for a client... My name is Ed... What is my balance and my holdings?").
  2. Pass the `params` (the `uv run` command) and a `client_session_timeout` (e.g., 30 seconds) into the context manager.
  3. Initialize the agent, passing the instructions, the model (`gpt-4o-mini`), and the `mcp_server` instance as the tools provider.
  4. Execute the agent (`runner.run()`).
- **Result:** The agent successfully spawns the server, calls the necessary tools (`get_balance` and `get_holdings`), and formulates a natural language response detailing Ed's cash balance ($8,026.64) and his 6 shares of Amazon.

**⭐ 🔹 The Evolution and Necessity of Custom MCP Clients**
→ The instructor provides crucial historical context regarding MCP clients. When the lab was first created, native SDKs (like the `openai-agents-sdk`) did not natively support MCP. Developers *had* to write their own custom MCP clients to extract tools and feed them into the LLM SDK. 
- The instructor notes a humorous anecdote: the exact day he finished writing the custom client code for this course, OpenAI updated their SDK to handle MCP natively, making his custom tool-client code largely obsolete.
- **Why learn it then?** While modern SDKs auto-handle the "plumbing" for *tools*, building a custom MCP client is **still required if you want to use MCP Resources**. Standard SDK context managers handle tools perfectly, but resources currently require custom client logic to access.
> ⭐ **EXAM NOTE:** You must know the distinction between handling Tools vs. Resources in modern AI SDKs. While SDKs abstract away tool discovery and execution, custom MCP clients are still necessary to read and interact with MCP Resources.

**🔹 Building a Custom MCP Client (`accounts_client.py`)**
→ The instructor walks through the code required to build a custom MCP client from scratch, using an implementation styled after Anthropic's reference code.
- **Defining Parameters:** Just like before, the client needs the `uv run` command parameters to know how to spawn the server.
- **Session Management:** The client uses context managers to handle the connection session, calling `await session.initialize()` before making requests.
- **`list_accounts_tools()`:** A function that initializes the session and returns the server's tools.
- **`call_accounts_tool(name, tool_args)`:** A function that initializes the session and executes a specific tool by its name.

**⭐ 🔹 JSON Schema Translation for Tools (`get_accounts_tools_openai`)**
→ One of the most critical jobs of a custom MCP client (historically, and currently for unsupported LLMs) is schema translation. The way MCP returns a tool's JSON definition is very similar—but **not identical**—to the standard JSON schema expected by OpenAI's API. 
- The custom client must iterate through the tools returned by MCP, map the MCP descriptions to OpenAI's expected format, and reconstruct the tool as an OpenAI `function` object.
- **Example:** The instructor prints the raw MCP tool schema side-by-side with the translated OpenAI tool schema to prove they are structured differently.
> ⭐ **EXAM NOTE:** Schema translation is a major concept. You must understand that MCP native tool schemas and OpenAI tool schemas are not identical out-of-the-box, and translation logic (whether custom-built or handled under-the-hood by an SDK update) is required for interoperability.

**🔹 Running the Custom MCP Client for Tools**
→ To prove the custom client works, the instructor:
  1. Calls `list_accounts_tools()` and translates them using `get_accounts_tools_openai()`.
  2. Creates an `OpenAIAgent`, but this time, instead of passing the `mcp_server` directly, he passes the *translated tools array* manually.
  3. The agent successfully returns the same correct response (Ed's balance and holdings). This demonstrates the exact "plumbing" that OpenAI's SDK now does automatically behind the scenes.

**⭐ 🔹 Accessing MCP Resources via a Custom Client**
→ The instructor demonstrates how to fetch a resource using the custom client function `read_accounts_resource(name)`. 
- He queries the resource named `"ed"` using `await read_accounts_resource("ed")`.
- **The Output:** It returns a JSON string representing the exact state of Ed's account (balance, strategy, holdings, transactions).
- **Comparison:** The instructor shows that you *could* get the exact same output by simply importing the Python business logic directly (`Account.get("ed").report()`).
- **The "Why":** Why use an MCP client to get a resource if you can just import the code? Because an MCP server allows you to share resources **systematically and securely** with external systems, LLMs, or other developers without exposing the underlying business logic, database queries, or raw code.
> ⭐ **EXAM NOTE:** Be prepared to explain the architectural benefit of MCP Resources. The purpose is systematic, secure abstraction—allowing systems to read contextual data without needing access to the underlying application logic or source code.

**🔹 Lab Exercises and Best Practices**
→ The instructor concludes the video by assigning exercises to solidify the concepts:
1. **Basic Exercise:** Make a simple MCP Server that contains a single function returning the current date. Expose it as a tool so the agent can accurately state today's date. 
   - *Instructor's insight:* LLMs are notoriously bad at knowing the current date/time natively. Providing a tool for this is a highly recommended best practice.
2. **Harder Exercise:** Write an MCP client and use a *native* OpenAI API call (using the raw OpenAI SDK, not the Agent SDK wrapper) to call the tool via the custom client.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. The `list_tools()` Function
2. The Evolution and Necessity of Custom MCP Clients
3. JSON Schema Translation for Tools (`get_accounts_tools_openai`)
4. Accessing MCP Resources via a Custom Client