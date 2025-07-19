# streaming_utils.py
import asyncio
from typing import Any, Dict, AsyncGenerator, List, Generator
from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnableConfig, Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
import pprint

# async def astream_output(
#     agent_executor: AgentExecutor,
#     input_data: Dict[str, Any],
#     config: RunnableConfig,
# ) -> AsyncGenerator[str, None]:
#     """
#     Streams output from an agent executor asynchronously, yielding token by token.
#     Focuses on the final response content only.
#     """
#     full_output = []
    
#     async for event in agent_executor.astream_events(input_data, config=config, version="v1"):
#         event_type = event["event"]
        
#         if event_type == "on_llm_stream":
#             # Extract token content
#             chunk = event.get("data", {}).get("chunk", {})
#             content = chunk.get("content", "")
            
#             if content:
#                 yield content
#                 full_output.append(content)
#                 await asyncio.sleep(0.02)  # Smooth streaming
                
#         elif event_type == "on_agent_finish":
#             # Ensure final output is fully streamed
#             result = event.get("data", {}).get("output", "")
#             if result and result not in "".join(full_output):
#                 yield result

async def astream_output(
    agent_executor: RunnableWithMessageHistory,
    input_data: Dict[str, Any],
    config: RunnableConfig,
) -> AsyncGenerator[str, None]:
    """
    Streams output from an agent executor or RunnableWithMessageHistory asynchronously.
    Focuses on the final response content only.
    """
    full_output = []
    
    async for event in agent_executor.astream_events(input_data, config=config, version="v1"):
        # print(f"\n🔄 Event: {event['event']}")
        event_type = event["event"]
        #print("event_type", event_type)  # Uncomment for detailed event debugging
        if event_type == "on_llm_stream":
            chunk = event.get("data", {}).get("chunk", {})
            content = chunk.get("content", "")
            # print(content, end='', flush=True)
            if content:
                yield content
                full_output.append(content)
                await asyncio.sleep(0.02)

        elif event_type == "on_agent_finish":
            result = event.get("data", {}).get("output", "")
            if result and result not in "".join(full_output):
                yield result

async def aprint_stream(
    stream: AsyncGenerator[str, None],
    prefix: str = ""
) -> str:
    """
    Prints an async stream and returns the full response.
    """
    full_response: List[str] = []
    print(prefix, end='', flush=True)
    
    try:
        async for token in stream:
            print(token, end='', flush=True)
            full_response.append(token)
    finally:
        return "".join(full_response)

        
def stream_chain_output(
    chain: Runnable,
    input_data: Dict[str, Any],
) -> str:
    """
    Streams output from an LLM-backed chain synchronously, yielding token by token.
    Designed for chains like summarize_chain that invoke LLMs.
    """
    full_output = ""

    print("🔄 Streaming chunk:", full_output, flush=True)
    for chunk in chain.stream(input_data):
        # Extract content if chunk is a Document, LLM response object, etc.
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        
        if content:
            full_output += content
            print(content, end='', flush=True)
    return full_output