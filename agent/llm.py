from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model(
    "groq:openai/gpt-oss-20b",
    reasoning_format="parsed",
    reasoning_effort="low",
    max_completion_tokens=4096,
    model_kwargs={"parallel_tool_calls": False}
)