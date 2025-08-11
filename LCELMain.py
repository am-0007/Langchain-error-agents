import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain_core.rate_limiters import InMemoryRateLimiter
from schema.ResponseFormatter import LLMResponse
from langchain_core.messages import BaseMessage
from typing import List
from langchain.agents import AgentExecutor, create_tool_calling_agent
import asyncio

from tools.Tools import register_tools
import textwrap
from dotenv import load_dotenv

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableConfig, RunnableSerializable
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from utils.streaming_utils import aprint_stream, astream_output

from agents.CustomAgentExecutor import get_agent_executor, customAgentExecutor
from agents.callbackHandler.QueueCallbackHandler import QueueCallbackHandler


load_dotenv()

rate_limiter = InMemoryRateLimiter(requests_per_second=1)
memories = {}

message: List[BaseMessage] = [
    SystemMessage(content="You are a helpful code generator assistant."),
    HumanMessage(content="Read the error log from tool and tell me what the problem is. Use the log path: /Users/ajmaharjan/Documents/langChain/errorAgents/resource log/mrf_error_only.log")
]

llm = ChatOllama(
    model="mistral:7b",
    temperature=0.7,
    rate_limiter=rate_limiter
)

tools = register_tools(llm)

def get_memory(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in memories:
        memories[session_id] = InMemoryChatMessageHistory()
        memories[session_id].add_system_message(
            SystemMessage(content="You are a helpful code generator assistant.")
        )
    return memories[session_id]

prompt=ChatPromptTemplate.from_messages([
        ("system", "You are a helpful code generator assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

name2tool = {tool.name: tool.func for tool in tools} # type: ignore

agent_executor : customAgentExecutor = get_agent_executor(llm, max_iterations=3)

async def main():
    print("Ask anything (type 'exit' to quit):")
    
    while True:
        user_input = await asyncio.to_thread(input, "You: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        q = asyncio.Queue()
        streamer = QueueCallbackHandler(queue=q)

        result = await agent_executor.invoke(user_input, streamer)
        print("\n" + "=" * 80)
        print("\n" + "=" * 80)
        print("\nAgent:", result["output"])
    
if __name__ == "__main__":
    asyncio.run(main())