# InternIQ MCP Demo Script

## Goal

This demo shows how InternIQ exposes its internship assistant features through MCP.

The important message:

InternIQ is the host application. `mcp_bridge.py` or `interniqmcp` is the MCP client. `interniq_mcp.py` is the MCP server. The transport is stdio. The server exposes InternIQ data and actions as MCP tools, resources, and prompts.

## 1. Start The App

Backend:

```powershell
cd C:\Users\burak\OneDrive\Masaüstü\InternIQ\backend
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Frontend:

```powershell
cd C:\Users\burak\OneDrive\Masaüstü\InternIQ
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173
```

## 2. Explain MCP Roles

Say this during the demo:

```text
In this project, MCP is used as a standard protocol layer between InternIQ and its AI/application features.

Host: InternIQ
Client: mcp_bridge.py or the interniqmcp terminal
Server: backend/mcp_server/interniq_mcp.py
Transport: stdio

The MCP server exposes:
- Tools: callable actions such as search_internships and build_application_context
- Resources: readable app data such as interniq://listings and interniq://companies
- Prompts: reusable prompt templates such as application-prep-prompt
```

## 3. Terminal MCP Demo

Start the interactive MCP terminal:

```powershell
interniqmcp
```

Show available commands:

```text
help
```

Show the actual MCP tools:

```text
tools
```

Show app features exposed through MCP:

```text
features
```

Search internships through MCP:

```text
search python
```

Read one listing:

```text
listing 1
```

Read company context:

```text
company ASELSAN
```

Call a raw MCP tool with JSON arguments:

```text
call build_application_context {"listing_id":1,"cv_text":"Python C++ embedded systems project"}
```

Explain the result:

```text
This result did not come from direct frontend state. The terminal connected to the MCP server over stdio, discovered the server capabilities, called a tool, and received structured listing, company, CV, and prompt context.
```

Run the full workflow from terminal:

```text
workflow 1 "Python C++ embedded systems project"
```

Optional account-based flow:

```text
login <email>
profile
cv-profile 1
workflow-profile 1
logout
```

Exit:

```text
quit
```

## 4. Protocol Trace API Demo

Run the MCP demo endpoint:

```powershell
$body = @{ listing_id = 1; cv_text = "Python C++ embedded systems project" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8001/api/v1/mcp/demo" `
  -ContentType "application/json" `
  -Body $body
```

Point out these fields in the response:

```text
mcp_status
mcp_capabilities.tools
mcp_capabilities.resources
mcp_capabilities.prompts
mcp_trace
mcp_context
```

Expected trace order:

```text
connect
initialize
discover_tools
discover_resources
read_resources
discover_prompts
get_prompt
call_tool
return_context
```

## 5. Frontend Demo

In the browser:

1. Open the Application Assistant page.
2. Select the ASELSAN internship listing.
3. Enter CV text, or leave it empty if using a saved profile CV.
4. Click the preparation button.
5. Show the MCP Protocol Trace panel.
6. Then show the generated LangGraph preparation result.

Say this:

```text
The UI shows the process before the result. First InternIQ connects to the MCP server, discovers tools, reads resources, gets the prompt, calls build_application_context, and then sends that MCP context into the LangGraph workflow.
```

## 6. Why MCP Is Useful Here

Use this explanation:

```text
Without MCP, InternIQ features would only be internal backend functions.

With MCP, the same application capabilities become available through a standard protocol. A terminal client, the FastAPI bridge, or another MCP-compatible host can discover and call the same tools, read the same resources, and reuse the same prompts.

This makes the project easier to demonstrate, inspect, and integrate with other agent hosts.
```

## 7. Final Summary

Close with:

```text
This project demonstrates MCP with a real local server, stdio transport, tools, resources, prompts, a client bridge, terminal usage, API usage, and a visible frontend protocol trace.
```
