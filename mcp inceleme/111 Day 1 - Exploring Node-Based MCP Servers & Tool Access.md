📹 VIDEO TOPIC: JavaScript/Node-based MCP Servers (Playwright & Filesystem)
🕐 COVERAGE: Node-based MCP servers setup, Playwright browser automation, Filesystem read/write isolation

***

**⭐ 🔹 Python vs. JavaScript MCP Server Execution (uvx vs. npx)**
→ The instructor begins by contrasting the execution methods of different Model Context Protocol (MCP) servers based on the language they are written in. Previously, the course covered a Python-based MCP server (`fetch`), which was executed by calling `uvx` (a runner for Python packages from PyPI). However, when moving to JavaScript-based MCP servers, the execution command changes. JavaScript-based servers are run using server-side JavaScript via `node`, and specifically utilizing the `npx` (Node Package Execute) command provided by `npm` (the Node Package Manager). 

> ⭐ **EXAM NOTE:** This is a fundamental operational distinction in the MCP ecosystem. You must know that Python-based MCP servers are typically invoked with `uvx`, while JavaScript/Node-based MCP servers are invoked with `npx`.

**🔹 Node.js Prerequisites for JS MCP Servers**
→ Because these new MCP servers are JavaScript-based, they require server-side JavaScript execution. To run them, you must have `node` installed on your local computer. 
- **Version Requirement:** You need a relatively recent version of Node.js. 
- **Version Management:** The instructor recommends using `nvm` (Node Version Manager) if you are currently running an older version and need to upgrade seamlessly.
- **Verification:** You must ensure that the `npx` command is available and working by running `npx --version` in your terminal. 

**🔹 The Playwright MCP Server Setup**
→ The first JavaScript-based MCP server introduced is based on Microsoft's **Playwright**, a highly popular browser automation software. To integrate it, the code utilizes the `MCPServerStdio` context manager, just like with Python servers, but passes in Node-specific execution parameters.
- **Command:** `npx`
- **Package:** `@playwright/mcp-server` (or `@playwright/mcp@latest` as seen on screen)

```python
# Defining the parameters to run the Node-based Playwright MCP Server
playwright_params = {
    "command": "npx", 
    "args": ["-y", "@playwright/mcp@latest"] # -y auto-confirms the installation via npx
}

# The standard code construct for connecting to the MCP Server
async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=30) as server:
    # Awaiting the server to spawn, install the package, and list available tools
    playwright_tools = await server.list_tools()

playwright_tools
```

**⭐ 🔹 Playwright vs. Fetch MCP Server (Granularity of Control)**
→ The instructor highlights a critical architectural comparison between the previously used `fetch` MCP server and the `Playwright` MCP server. 
- **Fetch MCP Server:** Much simpler. It returns exactly **one tool** designed solely to collect the Markdown contents of a single provided web page URL.
- **Playwright MCP Server:** Returns a **massive suite of tools** that gives the agent fine-grained, highly granular control over the entire browser process. 

This granular control enables the creation of "Sidekick" agents (referenced from Week 4 of the course) that can actively power and manipulate a browser window step-by-step rather than just passively reading a URL. The tools returned by Playwright include:
1. Close the browser
2. Resize the browser window
3. View console messages
4. Upload a file
5. Press a specific key on the keyboard
6. Navigate backward and forward
7. Take a screenshot (noted as "super interesting" for visual agent workflows)
8. Drag, click, hover, and select elements

> ⭐ **EXAM NOTE:** Understanding the difference between passive data fetching (`fetch`) and active, granular automation (`Playwright`) is crucial for agent design. If an exam question asks how to allow an agent to visually interact with, click, or navigate a dynamic web application, Playwright is the correct MCP choice, not a simple URL fetcher.

**🔹 The Plug-and-Play Nature of MCP**
→ A core philosophy of Model Context Protocol (MCP) servers emphasized by the instructor is how effortlessly they allow developers to equip agents with vast capabilities. Because the protocol standardizes how tools are requested and returned (via `server.list_tools()`), a developer can simply find an MCP server that interests them (like Playwright), point the code at it, and instantly endow their agent with a whole slew of complex tools without writing the underlying tool logic.

**⭐ 🔹 The Filesystem MCP Server & Security Sandboxing**
→ The second JavaScript-based MCP server introduced is Anthropic's official reference server for local file manipulation: `@modelcontextprotocol/server-filesystem`. Because granting an AI agent the ability to read and write files on a local computer is inherently dangerous, the instructor details a strict **Sandboxing** pattern.
- **How Sandboxing Works:** Instead of giving the agent access to the entire hard drive, you programmatically define a specific, isolated directory (the "sandbox") and pass that absolute path into the MCP server's arguments. The agent is permanently restricted to only reading and writing within this designated folder.

```python
import os

# 1. Programmatically define the absolute path to a safe local directory called "sandbox"
sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))

# 2. Pass the sandbox_path as an argument to the filesystem MCP server
files_params = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]
}

# 3. Spawn the server and request its tools
async with MCPServerStdio(params=files_params, client_session_timeout_seconds=30) as server:
    file_tools = await server.list_tools()

file_tools
```

> ⭐ **EXAM NOTE:** The concept of "Sandboxing" the Filesystem MCP server is highly testable from a security architecture perspective. You must know that passing an absolute path constraint to the filesystem MCP server restricts the agent's file operations strictly to that directory to prevent catastrophic system modifications.

**🔹 Filesystem MCP Server Capabilities**
→ Once the `server-filesystem` client is spawned and connects to the server, it requests the tools (`await server.list_tools()`). The resulting output provides the agent with the ability to read and write from the local file system (within the sandbox constraint). The specific tools returned include:
- `read_file`: Read the contents of a single file.
- `read_multiple_files`: Read multiple files simultaneously.
- `create_directory`: Create a new folder.
- `list_directory`: See the contents of a folder.
*(and implicitly, other tools to write/edit files based on the instructor's explanation of "read and write" capabilities).*

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. Python vs. JavaScript MCP Server Execution (uvx vs. npx)
2. Playwright vs. Fetch MCP Server (Granularity of Control)
3. The Filesystem MCP Server & Security Sandboxing