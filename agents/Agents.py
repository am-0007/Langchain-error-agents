from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_ollama import ChatOllama

class AgentExecutorWithTools:
    def __init__(self, tools, llm : ChatOllama):
        self.tools = tools
        self.llm = llm

    def getAgents(self):
        return create_tool_calling_agent(self.llm, self.tools, )