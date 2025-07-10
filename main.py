from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain_core.rate_limiters import InMemoryRateLimiter
from schema.ResponseFormatter import LLMResponse
from langchain_core.messages import BaseMessage
from typing import List

# Deprecated 
# from langchain.memory import ConversationSummaryMemory
# from langchain.chains import ConversationChain


from tools.Tools import register_tools
import textwrap
from dotenv import load_dotenv

# Migrated to new implementation for message history
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import Runnable
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.base import RunnableMap
from langchain_core.runnables import RunnableLambda

load_dotenv();

# Step 1: Set up rate limiter (optional)
rate_limiter = InMemoryRateLimiter(requests_per_second=1)

memories = {}

message : List[BaseMessage] = [
    SystemMessage(content="You are a helpful code generator assistant."),
    HumanMessage(content="Read the error log and tell me what the problem is.")
]

# Step 2: Initialize LLM with parameters and structured output
llm = ChatOllama(
    model="mistral:7b",
    temperature=0.7, 
    #stop = ["\nObservation"],
    rate_limiter=rate_limiter  # or remove if not needed
)

# Step 2: Define conversation logic (e.g. registered tools, prompt wrapper, etc.)
base_chain: Runnable = register_tools(llm)

def get_memory(session_id: str):
    if session_id not in memories:
        memories[session_id] = InMemoryChatMessageHistory()
        # Add system message once per session so AI "remembers" role
        memories[session_id].add_system_message(
            SystemMessage(content="You are a helpful code generator assistant.")
        )
    return memories[session_id]

# Step 4: Wrap with RunnableWithMessageHistory
# The runnable that will be wrapped by RunnableWithMessageHistory.
# It is responsible for combining the chat history with the new messages.
chain = (
    RunnableLambda(lambda x: x["chat_history"] + x["messages"]) | base_chain
)

conversation_chain = RunnableWithMessageHistory(
    chain,
    get_memory,
    input_messages_key="messages",
    history_messages_key="chat_history",
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def stream_response(messages: List[BaseMessage], session_id="user-123"):
    print("🤖 AI Response (streaming): ", end='', flush=True)
    # The input to stream() should only be the new messages.
    # The session_id is passed in the config, which RunnableWithMessageHistory uses.
    stream = conversation_chain.stream(
        {"messages": messages},
        config=RunnableConfig(configurable={"session_id": session_id})
    )

    full_response = ""
    for chunk in stream:
        # Check for tool calls in the chunk
        if chunk.tool_calls:
            for tool_call in chunk.tool_calls:
                print(f"\n\nTool call: {tool_call['name']}()", flush=True)
        # Print content if it exists
        if chunk.content:
            token = chunk.content
            print(token, end='', flush=True)
            full_response += token

    print()
    print("-" * 80)  # Add a separator line for clarity
    return full_response

# Step 4: Ask something
stream_response(messages=message[1:], session_id="user-123")

# Optional: continue further conversation
while True:
    user_input = input("👤 You: ")
    stream_response(messages=[HumanMessage(content=user_input)], session_id="user-123")


# def print_memory(session_id: str):
#     history = get_memory(session_id)
#     print(f"\n📚 Message history for session '{session_id}':")
#     print(history)
#     for i, msg in enumerate(history.messages):
#         print(f"[{i}] {msg.type.upper()}: {msg.content}")
        
# print_memory("user-123");

