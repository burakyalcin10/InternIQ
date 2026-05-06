📹 VIDEO TOPIC: Best Practices for Building Agentic Systems (Rules 3 to 10)
🕐 COVERAGE: Workflow over autonomy, bottom-up architecture, model selection strategy, context vs. memory, prompting over complex fixes, tracing, and the scientific mindset in AI engineering.

***

**⭐ 🔹 Favor Workflow Over Autonomy Initially (Rule 3)**
→ When embarking on a new AI agent solution, it is highly tempting to rush immediately into building a fully autonomous system. However, the best practice is to start by building simple, step-by-step workflows. By favoring hard-coded workflows initially, you maintain control and predictability, which is crucial for debugging and validation. 

When working with frameworks like the OpenAI Agents SDK, there are multiple approaches to orchestrating multi-agent systems. The instructor highlights three distinct methods:
1. **Tools:** Having one agent call out to another agent as if it were a tool.
2. **Handoffs:** Passing control entirely from one agent to a different agent.
3. **Isolated Python Workflows (The Deep Research Approach):** Using standard Python code to execute each agent call in complete isolation, one step at a time, rather than letting the agents orchestrate themselves.

The instructor strongly recommends starting with the **third approach** (Isolated Python Workflows). 

```python
# Conceptual representation of the Isolated Python Workflow
# Instead of agents calling each other autonomously, Python dictates the flow step-by-step.

# Step 1: Call an agent in isolation
step_1_output = runner.run(agent_A, input_data) 

# Step 2: Use Python logic to process or route, then call the next agent
step_2_output = runner.run(agent_B, step_1_output) 
```
Only after this hard-coded workflow operates successfully should you begin converting it into a more autonomous system using Handoffs or Tool calling, gradually granting the agents more responsibility.

> ⭐ **EXAM NOTE:** Understanding the progression from hard-coded programmatic workflows (Python orchestration) to fully autonomous agentic orchestration (Handoffs/Tools) is a foundational architectural principle. You will likely be tested on *why* we avoid full autonomy at the start of a project (to maintain control, predictability, and ease of debugging).

**⭐ 🔹 Work Bottom-Up, Not Top-Down (Rule 4)**
→ This is a crucial architectural directive, especially for those coming from a traditional Software Engineering background. It is a common mistake to start a project with a blank sheet of paper and draw a massive, complex, top-down "agent architecture diagram." 
Instead, you must build **bottom-up**. 
*   **Bottom-Up Approach:** Start with a single, simple agent designed to solve just one small fraction of your overall problem using a single LLM call. Work on this micro-problem until the agent solves it perfectly. Once successful, add the next agent, slowly combining these functional building blocks to form the larger platform. Discover what works and what doesn't organically.
*   **Top-Down Approach (Avoid):** Designing a massive, interconnected multi-agent web before testing individual components. If you build everything at once and it fails, it is nearly impossible to isolate the point of failure.

> ⭐ **EXAM NOTE:** The distinction between top-down and bottom-up architecture is critical. Exam questions frequently present a scenario where a complex multi-agent system is failing and ask for the architectural flaw: the answer is often that the developer did not build and test bottom-up components first.

**🔹 Start Simple, Then Add (Rule 5)**
→ Closely related to Rule 4, this principle dictates that you should always begin with the simplest possible solution. The instructor notes that many students send in massive, hundreds-of-lines-of-code solutions that are broken, asking "why isn't this working?" The failure occurs because the system became too complex too quickly. You cannot debug a massive, unproven agentic system. You must solve a simple problem, do it really well, and incrementally add complexity. Put the building blocks together only after they are proven individually.

**⭐ 🔹 Start with Large Frontier Models, Then Reduce (Rule 6)**
→ Model selection should follow a top-down approach regarding capability and cost. When starting a project with small datasets or proof-of-concept tasks, you should always begin with the highest-end, most capable "frontier" models available (e.g., GPT-4o, Claude 3.5 Sonnet). 
*   **Phase 1 (Proof of Concept):** Use expensive, high-powered models to prove that your workflow and theory actually work in practice. (Note: The instructor mentions avoiding "Claude Opus" if it is prohibitively expensive, but favors highly capable models like Claude Sonnet or GPT-4o).
*   **Phase 2 (Optimization):** Once the concept is proven, attempt to transition the workload to cheaper, lighter, faster models (e.g., Claude 3.5 Haiku, GPT-4o-mini). To achieve comparable performance on these lighter models, you will need to make your prompts significantly more instructive, precise, and directive.

> ⭐ **EXAM NOTE:** This is a standard industry pipeline for LLM application development: prototype on frontier models to validate feasibility, then optimize prompts/context to deploy on cheaper/smaller models to save costs and reduce latency.

**⭐ 🔹 Think Context Rather Than Memory (Rule 7)**
→ The term "Memory" in AI engineering (often divided into short-term memory like conversation history, and long-term memory like RAG databases or Knowledge Graphs from trading projects) is an overworked and potentially distracting construct. 
Instead of getting bogged down in "types of memory," you should shift your mindset to focus purely on **Context**. 
Ultimately, all memory techniques are simply methods for finding relevant text and injecting it into the final prompt. You should focus on:
1. What information does the LLM actually need to answer the question?
2. Are the tools and retrieval systems successfully putting that exact information into the prompt?
If the right context is in the prompt, the agent will succeed, regardless of the theoretical "memory architecture" you are using.

> ⭐ **EXAM NOTE:** This is a major paradigm shift. If tested on "Memory" in an agentic context, remember the core philosophy: memory is just a retrieval mechanism to provide *context* in the prompt. The ultimate source of truth is the final prompt payload.

**⭐ 🔹 Most Problems are Solved with Prompts (Rule 8)**
→ When an agentic system fails or produces incorrect output, developers often instinctively reach for complex, heavy-handed engineering fixes—such as fine-tuning models, swapping out encoder LLMs for RAG, or redesigning the architecture. 
The reality is that the vast majority of difficulties are fixed simply by writing **better prompts**. 
Before changing the architecture, apply these prompt engineering fixes:
*   Make the prompt simpler.
*   Make it more directive and instructive.
*   Tell the model exactly what *not* to do (negative prompting).
*   Provide concrete examples of good output (Few-Shot Prompting).

> ⭐ **EXAM NOTE:** This is the golden rule of LLM debugging. Always optimize the prompt before resorting to fine-tuning or architectural changes. Expect troubleshooting questions to emphasize prompt engineering as the first step in resolving poor agent performance.

**⭐ 🔹 Look at the Traces (Rule 9)**
→ Examining execution traces is a vital discipline that must not be skipped. Even if an agent appears to be working perfectly and outputs the correct answer, you must look at the traces.
*   **Why trace?** An agent might be arriving at the correct answer inefficiently. It might be caught in weird internal loops, making unnecessary or redundant tool calls, or executing hidden "gotchas" that cost time and tokens. Tracing ensures the agent is behaving exactly as you expect under the hood.

> ⭐ **EXAM NOTE:** Tracing is the primary observability tool for agents. Just because the final output is correct does not mean the system is structurally sound. You will be tested on the importance of traces for finding hidden loops and optimizing tool calls.

**🔹 Be a Scientist; No Shortcut to R&D (Rule 10)**
→ Building AI systems requires a fundamentally different mindset than traditional application development. An AI Engineer must wear two hats:
1. **The Software Engineer Hat:** Building infrastructure, code, and deployments.
2. **The Data Scientist Hat:** Focusing on experimentation, metrics, and observation.
When starting a new system, you must take off the SWE hat and put on the Scientist hat. Do not rely on "instinct" to guess which model (A, B, or C) or which technique to use. There are no shortcuts. You must:
*   Embrace pure R&D and experimentation.
*   Try multiple models and techniques side-by-side.
*   Measure the results against your predefined business metric (referencing Rule 2).
*   Let the data dictate which approach works best.

***
## ⭐ MUST-KNOW LIST (Exam-Critical Concepts)
1. Favor Workflow Over Autonomy Initially (Rule 3)
2. Work Bottom-Up, Not Top-Down (Rule 4)
3. Start with Large Frontier Models, Then Reduce (Rule 6)
4. Think Context Rather Than Memory (Rule 7)
5. Most Problems are Solved with Prompts (Rule 8)
6. Look at the Traces (Rule 9)