"""PUCIT GPA/CGPA assistant - Assignment 3.
Tools come from our MCP server; memory in SQLite; answers are streamed."""

import asyncio
import os

from fastmcp.client import Client
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.mcp import MCPAdapter
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from llm import llm                      # also calls load_dotenv()
from local_tools import save_report      # writes on the student's own machine

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
FASTMCP_KEY = os.getenv("FASTMCP_KEY")   # only if the host needs auth
DB_PATH = "chats.db"

SYSTEM_PROMPT = """
You help PUCIT BS(CS) students with GPA and CGPA questions.

1. Never calculate in your head, even credit-hour totals. Every numerical
   answer must use a tool result. Do not guess marks, credit hours, CGPA,
   or the student's semester. Ask for one or two missing details at a time.
2. Use marks_to_grade_points for marks, calculate_semester_gpa for a weighted
   semester GPA, and calculate_new_cgpa for a new projected CGPA.
   Use get_semester_courses for known courses and their credit hours.
3. MD-001 and MD-002 are non-credit pass/fail: exclude them. Count all other
   graded courses, including separate labs and Quran Translation (0.5 CH).
4. For a target CGPA, obtain the current CGPA, completed credit hours,
   target CGPA, and first unfinished semester. If someone says 'I am IN
   semester 5', semester 5 is the first unfinished semester. Do not ask
   which semester comes next when the student has already told you this.
5. For target planning, call get_semester_courses for the first unfinished
   semester. It includes tool-calculated planning hours for that semester,
   then for that semester plus each later semester. For EACH horizon, pass
   those tool-provided hours to required_gpa_for_target. Start with one
   semester. If the required GPA is above 4.0, say that deadline is
   impossible and AUTOMATICALLY check the next horizon, then the next,
   until the first required GPA is at most 4.0 or semester 8 is reached.
   Do not ask permission to continue. If no horizon works, explain that.
   If asked about this semester alone, first answer that deadline, then
   also explain the earliest possible later horizon.
6. For every target-CGPA plan, show each checked horizon in a Markdown table:
   | Horizon | Remaining credit hours | Required GPA | Verdict |
   |---|---|---|---|
   Use one row per horizon and only tool-provided numbers. Keep the table
   even if the terminal does not align it. Never call GPA above 4.0 achievable.
7. Offer to save only after a semester GPA, projected CGPA, or target plan.
   Never call save_report until the student asks you to save. Ask for a
   filename when needed. Your memory of this student (name, CGPA, credit
   hours, target) lasts between runs: use it instead of asking again.
8. Do not handle repeats/improvements, curves, incomplete grades,
   withdrawals or freezes.
9. If a tool returns "TOOL ERROR", the calculation service is unavailable.
   Tell the student plainly, do NOT guess any number, and suggest trying
   again later.
"""

TOOL_ERROR = (
    "TOOL ERROR: the calculation service could not be reached or failed "
    "({err}). Tell the student it is unavailable right now. Do not guess."
)


# ------------------------------------------------------------- Task 6 ---
class ToolErrorMiddleware(AgentMiddleware):
    """A tool that raises (server down, network...) becomes an error
    ToolMessage, so the model is told and no tool call is left unanswered."""

    @staticmethod
    def _error(request, exc: Exception) -> ToolMessage:
        call = request.tool_call
        return ToolMessage(
            content=TOOL_ERROR.format(err=f"{type(exc).__name__}: {exc}"),
            tool_call_id=call["id"], name=call["name"], status="error",
        )

    def wrap_tool_call(self, request, handler):
        try:
            return handler(request)
        except Exception as exc:  # noqa: BLE001
            return self._error(request, exc)

    async def awrap_tool_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as exc:  # noqa: BLE001
            return self._error(request, exc)


async def repair_dangling_tool_calls(app, config) -> int:
    """Heal a saved thread that has a tool call with no answer (old crash,
    Ctrl+C, saved before the middleware existed): add an error ToolMessage."""
    state = await app.aget_state(config)
    messages = state.values.get("messages", [])
    answered = {m.tool_call_id for m in messages if isinstance(m, ToolMessage)}
    fixes = [
        ToolMessage(content=TOOL_ERROR.format(err="the call never returned an answer"),
                    tool_call_id=c["id"], name=c["name"], status="error")
        for m in messages if isinstance(m, AIMessage)
        for c in m.tool_calls if c["id"] not in answered
    ]
    if fixes:
        await app.aupdate_state(config, {"messages": fixes})
    return len(fixes)


# ------------------------------------------------------------- Task 3 ---
async def list_threads(memory) -> list[str]:
    names: list[str] = []
    async for cp in memory.alist(None):
        tid = cp.config["configurable"]["thread_id"]
        if tid not in names:
            names.append(tid)
    return names


async def show_history(app, config) -> None:
    state = await app.aget_state(config)
    messages = state.values.get("messages", [])
    if not messages:
        print("  (no messages yet)")
    for m in messages:
        kind = type(m).__name__
        if isinstance(m, AIMessage):
            for c in m.tool_calls:
                print(f"  [{kind}] tool call -> {c['name']}({c['args']})")
        if m.content:
            print(f"  [{kind}] {m.text}")


# ------------------------------------------------------------- Task 4 ---
async def chat_turn(app, text: str, config) -> None:
    inputs = {"messages": [HumanMessage(text)]}      # only the NEW message
    line_open = False
    async for chunk in app.astream(
        inputs, config, stream_mode=["updates", "messages"], version="v2"
    ):
        if chunk["type"] == "messages":
            token, metadata = chunk["data"]          # one piece of the answer
            node = metadata["langgraph_node"]        # which node made it
            if node == "model" and token.text:
                if not line_open:
                    print("Agent: ", end="", flush=True)
                    line_open = True
                print(token.text, end="", flush=True)
        else:                                        # "updates"
            for node, update in chunk["data"].items():
                for m in (update or {}).get("messages", []):
                    if isinstance(m, AIMessage) and m.tool_calls:
                        for c in m.tool_calls:
                            print(f"\n  🔧 {c['name']}({c['args']}) ...", flush=True)
                    elif isinstance(m, ToolMessage):
                        icon = "⚠️ " if m.status == "error" else "✅"
                        print(f"  {icon} {m.name} done", flush=True)
                        line_open = False
    print()


# --------------------------------------------------------------- main ---
async def ask_name(memory) -> str:
    saved = await list_threads(memory)
    print("Saved chats:", ", ".join(saved) if saved else "(none yet)")
    while True:
        name = (await asyncio.to_thread(input, "Who is chatting? ")).strip()
        if name:
            return name


def build_agent(model, tools, memory):
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=memory,
        middleware=[ToolErrorMiddleware()],
    )


async def main() -> None:
    target = Client(MCP_URL, auth=FASTMCP_KEY) if FASTMCP_KEY else MCP_URL
    try:
        # Keep the adapter open while the agent can invoke MCP tools.
        async with MCPAdapter(target) as adapter:
            mcp_tools = await adapter.list_tools()
            print("MCP tools:", [t.name for t in mcp_tools])

            async with AsyncSqliteSaver.from_conn_string(DB_PATH) as memory:
                app = build_agent(llm, mcp_tools + [save_report], memory)

                name = await ask_name(memory)
                config = {"configurable": {"thread_id": name}}
                print(f"Hi {name}! Commands: /switch  /history  /forget  exit")

                while True:
                    text = (await asyncio.to_thread(input, f"\n{name}: ")).strip()
                    if not text:
                        continue
                    if text.lower() in ("exit", "quit"):
                        print("Goodbye!")
                        break
                    if text == "/switch":
                        name = await ask_name(memory)
                        config = {"configurable": {"thread_id": name}}
                        continue
                    if text == "/history":
                        await show_history(app, config)
                        continue
                    if text == "/forget":
                        await memory.adelete_thread(name)
                        print(f"Forgot everything about {name}.")
                        continue
                    try:
                        await repair_dangling_tool_calls(app, config)
                        await chat_turn(app, text, config)
                    except Exception as error:  # noqa: BLE001  (e.g. Groq API error)
                        print("\nAPI error:", error)
                        await repair_dangling_tool_calls(app, config)
    except Exception as exc:  # noqa: BLE001
        print(f"Could not connect to MCP server at {MCP_URL}: {type(exc).__name__}: {exc}")
        print("Start the server first and verify MCP_URL in agent/.env.")


if __name__ == "__main__":
    asyncio.run(main())
