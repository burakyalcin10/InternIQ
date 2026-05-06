📹 VIDEO TOPIC:
🕐 COVERAGE: MCP Architecture Recap, Knowledge Graph Memory, and Persistent Memory Tools

**⭐ 🔹 **Three Configurations of MCP Servers****
→ The instructor recaps the core architecture of the Model Context Protocol (MCP) by outlining the three distinct configurations for running MCP servers:
1. **Local Server, Local Resources:** The simplest configuration. The MCP server runs entirely on your local computer and only interacts with local resources (e.g., local file system, or handwritten local databases like an 'accounts' server).
2. **Local Server, Remote Resources (APIs):** The most common configuration. The MCP server runs locally on your machine but makes remote API calls over the internet to access online services and data.
3. **Remote Server, Remote Resources (Managed/Hosted MCP Server):** The server is hosted remotely and accesses remote resources. The instructor notes this is not a common architecture currently, but it represents a fully managed approach that will be explored briefly.
> ⭐ **EXAM NOTE:** This is the foundational definition of MCP deployment architectures. Understanding the distinction between where the server runs (host computer vs. remote server) versus where the resources live is critical for answering architecture-level questions.

**🔹 [MCP Server Distribution and Execution]**
→ The instructor clarifies how local MCP servers (Configurations 1 and 2) are typically distributed. While it is possible to write your own, most of the time developers use MCP servers that have been made available online via public repositories. Developers use package execution commands like `npx` (for Node.js) or `uvx` (for Python) to dynamically download the shared server code from the internet and execute it locally on their own machines. 

**⭐ 🔹 **Memory in the MCP Paradigm****
→ The instructor highlights a fundamental shift in how "memory" is conceptualized in the MCP age compared to older frameworks. In previous AI frameworks (such as LangChain), memory is often treated as a single, monolithic, built-in construct. However, in an MCP-driven architecture, memory is simply viewed as **another set of tools** that you equip the LLM with. An LLM can be provided with many different types of memory tools simultaneously, and it uses these tools to proactively request, store, or query context as needed during its execution.
> ⭐ **EXAM NOTE:** This conceptual shift—from memory as a rigid framework construct to memory as discrete, selectable tools provided via MCP—is a core philosophy of modern agentic design. You must understand that in MCP, memory is managed via standard tool calling.

**🔹 [Knowledge Graph Memory MCP Server]**
→ To demonstrate local MCP servers, the instructor introduces a Node.js-based Knowledge Graph Memory MCP server. Instead of just saving raw text logs, this specific type of memory understands structured data. It breaks down information into **Entities**, **Observations** about those entities, and **Relationships** between different entities. This allows the LLM to build a connected web of context.

**🔹 [SQLite (libSQL) vs. JSON Memory Storage]**
→ The instructor compares two implementations of the knowledge graph memory server:
- **JSON-based:** Stores the knowledge graph in a flat JSON file. The instructor notes this version is less stable.
- **SQLite (libSQL)-based:** Stores the memory in a lightweight SQLite database. The instructor prefers this version as it is much more stable.
Additionally, the SQLite version allows developers to specify a specific directory and filename for the database (e.g., a database called `ed.db` in a `memory` folder). This is highly advantageous because it allows developers to maintain isolated, distinct memory stores for different agents.

**🔹 [Knowledge Graph Memory Tools]**
→ When the Memory MCP server is connected, it exposes a specific suite of tools to the LLM to manage the knowledge graph. The instructor lists the following available tools:
1. `create_entities`: Creates new entities alongside observations.
2. `search_nodes`: Searches for existing entities and their related observations.
3. `read_graph`: Retrieves the connections and relations between entities.
4. `create_relations`: Defines how two or more entities are connected.
5. `delete_entity`: Removes an entity from memory entirely.
6. `delete_relation`: Removes a specific connection between entities.

**🔹 [Code Pattern: Testing Memory Persistence]**
→ The lab demonstrates how to instantiate an agent, give it memory tools, and test its recall across different sessions.
**Step 1: Storing Information**
An agent is given instructions defining its persona ("My name's Ed... I'm an LLM engineer teaching a course about AI agents including the MCP protocol"). The agent uses its MCP tools to parse this instruction and save it to the local SQLite database.
**Step 2: Recalling Information**
A completely new agent instance is created using the *exact same* instructions, model, and connected MCP memory server. The user sends a simple prompt: *"My name is Ed. What do you know about me?"* Because the new agent has access to the persistent SQLite database via MCP tools, it successfully queries the database and replies with the previously stored information.
```python
# Connecting to the MCP Server (passing in parameters like npx commands and DB path)
async with MCPServerStudio(params=params, client_session_timeout_seconds=30) as mcp_server:
    
    # Creating the Agent and equipping it with the MCP server
    agent = Agent(
        name="agent", 
        instructions=instructions, 
        model=model, 
        mcp_server=mcp_server
    )
    
    # Running the agent with a specific request
    result = await Runner.run(agent, request)
```

**🔹 [Analyzing Traces for Memory Tools]**
→ To prove exactly how the agent retrieved the information, the instructor navigates to OpenAI's tracing dashboard (`platform.openai.com/traces`) to view the execution trace.
- The trace shows the LLM independently deciding to call the `search_nodes` tool.
- It passed the specific query `"Ed"`.
- The tool returned a structured JSON output containing the `EntityType` ("Person"), and an array of `Observations` (e.g., "Ed is an LLM engineer", "Ed is teaching a course about the MCP protocol"). The LLM then parsed this JSON output in the background to generate its final natural language response to the user.

**🔹 [Transitioning to Type 2 MCP Servers]**
→ At the end of the video, the instructor transitions to testing the second configuration of MCP servers: local servers calling remote web APIs. The example introduced is **Brave Search**, noting that unlike the local SQLite memory tool, this new configuration will require the user to configure a remote API key to function.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. Three Configurations of MCP Servers
2. Memory in the MCP Paradigm