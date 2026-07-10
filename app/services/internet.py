from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType

API_KEY = "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"

# Your NVIDIA LLM
llm = ChatNVIDIA(api_key=API_KEY, model="meta/llama-3.3-70b-instruct", temperature=0)

# Give it internet search capability
search = DuckDuckGoSearchRun()
tools = [search]

# Create agent with internet access
agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True
)

# Now your NVIDIA LLM can search the web
response = agent.run("What's the latest news about NVIDIA GPUs?")
print(response)
