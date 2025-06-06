"""Run `pip install ollama sqlalchemy 'fastapi[standard]'` to install dependencies."""

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage

local_agent_storage_file: str = "tmp/local_agents.db"
common_instructions = [
    "If the user asks about you or your skills, tell them your name and role.",
]

coding_agent = Agent(
    name="Coding Agent",
    agent_id="coding_agent",
    model=Ollama(id="hhao/qwen2.5-coder-tools:32b"),
    reasoning=True,
    markdown=True,
    add_history_to_messages=True,
    description="You are a coding agent",
    add_datetime_to_instructions=True,
    storage=SqliteStorage(
        table_name="coding_agent",
        db_file=local_agent_storage_file,
        auto_upgrade_schema=True,
    ),
)

playground = Playground(
    agents=[coding_agent],
    name="Coding Agent",
    description="A playground for coding agent",
    app_id="coding-agent",
)
app = playground.get_app()

if __name__ == "__main__":
    playground.serve(app="coding_agent:app", reload=True)
