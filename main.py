from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
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
from langchain_core.runnables import RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from utils.streaming_utils import aprint_stream, astream_output

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

agent = create_tool_calling_agent(
    llm,
    tools=tools,
    prompt=ChatPromptTemplate.from_messages([
        ("system", "You are a helpful code generator assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]),
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

conversation_chain = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
# async def stream_response(messages: List[BaseMessage], session_id="user-123"):
#     print("🤖 AI Response (streaming): ", end='', flush=True)
    
#     # Extract last message content as user input
#     last_human_message = messages[-1].content if messages else ""
#     get_memory(session_id).messages.append(HumanMessage(content=last_human_message))
    
#     stream = conversation_chain.astream(
#         {"input": last_human_message, "chat_history": get_memory(session_id).messages},
#         config=RunnableConfig(configurable={"session_id": session_id})
#     )

#     full_response = ""

#     async for chunk in stream:
#         # Debug: Show the whole chunk if needed
#         #print("\n📦 Chunk:", chunk)

#         tool_calls = chunk.get("tool_calls")
#         if tool_calls:
#             print("\n\n🔧 Tool calls:")
#             for tool_call in tool_calls:
#                 print(f"▶ Tool: {tool_call['name']}")
#                 print(f"▶ Args: {tool_call.get('args', {})}", flush=True)

#         content = chunk.get("content")
#         if content:
#             print(content, end='', flush=True)
#             full_response += content

#     print()
#     print("-" * 80)
#     get_memory(session_id).add_ai_message(full_response)
#     return full_response

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def stream_response(messages: List[BaseMessage], session_id="user-123"):
    print("🤖 AI Response (streaming): ", end='', flush=True)

    last_human_message = messages[-1].content if messages else ""
    get_memory(session_id).messages.append(HumanMessage(content=last_human_message))

    # Use your astream_output function to stream token by token
    stream = astream_output(
        agent_executor=conversation_chain,
        input_data={"input": last_human_message, "chat_history": get_memory(session_id).messages},
        config=RunnableConfig(configurable={"session_id": session_id}),
    )

    # Print stream and get full response
    full_response = await aprint_stream(stream)

    print("\n" + "-" * 80)
    get_memory(session_id).add_ai_message(full_response)
    return full_response

async def main():
    print(await stream_response(messages=message, session_id="user-1234"))
    print(f"history: {get_memory('user-1234').messages}")

    while True:
        try:
            user_input = await asyncio.to_thread(input, "👤 You: ")
            if user_input.lower() in ('exit', 'quit'):
                break
            await stream_response([HumanMessage(content=user_input)], "user-1234")
            print(f"history: {get_memory('user-1234').messages}")
        except (KeyboardInterrupt, EOFError):
            break
        finally:
            print("🧹 Cleaning up memory...")
            memories.clear()

if __name__ == "__main__":
    asyncio.run(main())
