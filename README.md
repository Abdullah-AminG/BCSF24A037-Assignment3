# Assignment 3 - PUCIT CGPA Guider (MCP + Memory + Streaming)

**Roll No:** BCSF24A037


## Submission information

- **MCP server URL:** https://cgpa-guider-bcsf24a037.fastmcp.app/mcp
- **API key:** Required. Configure the FastMCP Bearer token for the MCP client. Do not publish the actual secret in a public GitHub repository.
- **GitHub repository (server code):** https://github.com/Abdullah-AminG/BCSF24A037-Assignment3


## Project structure
- `server/`: FastMCP server and six shared CGPA tools.
- `agent/`: LangChain agent, SQLite conversation memory, streaming, and local report-saving tool.

`save_report` remains local because it writes to the student's own computer. The six calculation/course tools are exposed by the MCP server.

## Ubuntu / local run
Use two Ubuntu terminals. Python 3.11 or newer is recommended.

### Terminal 1 - MCP server
```bash
cd BCSF24A037_Assignment3/server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
fastmcp list server.py
fastmcp call server.py get_remaining_credit_hours current_semester=6
python server.py
```

The HTTP MCP endpoint is `http://127.0.0.1:8000/mcp`.

### Terminal 2 - Agent
```bash
cd BCSF24A037_Assignment3/agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
python agent.py
```

Put your real Groq key in `.env`:
```dotenv
GROQ_API_KEY=your_groq_api_key
MCP_URL=http://127.0.0.1:8000/mcp
FASTMCP_KEY=
```

Never upload `.env` or publish API keys to GitHub. `.env.example` is safe to submit.

Chat commands: `/switch`, `/history`, `/forget`, and `exit`.

## Assignment task mapping
1. **MCP server:** `server/server.py` registers all six functions from `server/tools.py`.
2. **Agent connection:** `agent/agent.py` discovers tools using `MCPAdapter` and passes them to `create_agent`.
3. **Memory:** `AsyncSqliteSaver` persists threads in `agent/chats.db`; thread ID is the student's name. `/switch`, `/history`, `/forget` are implemented.
4. **Streaming:** `app.astream(..., stream_mode=["updates", "messages"], version="v2")` streams tokens and tool progress.
5. **Internet hosting:** Deploy `server/` as a Render Web Service. Set root directory to `BCSF24A037_Assignment3/server`, build command `pip install -r requirements.txt`, start command `python server.py`, and environment variable `HOST=0.0.0.0`. Render supplies `PORT`. Set `MCP_URL=https://YOUR-SERVICE.onrender.com/mcp` in the agent's `.env`.
6. **Server failure:** `ToolErrorMiddleware` returns an error `ToolMessage`; `repair_dangling_tool_calls` repairs unanswered calls in saved history.

## Verify server
With the server running, in another terminal:
```bash
fastmcp list http://127.0.0.1:8000/mcp
```
The list should show six tools: `marks_to_grade_points`, `calculate_semester_gpa`, `calculate_new_cgpa`, `required_gpa_for_target`, `get_semester_courses`, `get_remaining_credit_hours`.

## Deployment and submission checklist
- [ ] Deploy the MCP server and replace the pending server URL above.
- [ ] Push the `server/` code to GitHub and paste the repository URL above.
- [ ] Add the deployed URL (and key only if required) to `agent/.env` and test the agent.
- [ ] Keep `.env`, `chats.db`, virtual environments, and API keys out of the submission ZIP.
- [ ] Zip the project as `BCSF24A037_Assignment3.zip`.
