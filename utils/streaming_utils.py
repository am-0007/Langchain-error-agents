# streaming_utils.py
import asyncio
from typing import Any, Dict, AsyncGenerator, List
from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnableConfig

async def astream_output(
    agent_executor: AgentExecutor,
    input_data: Dict[str, Any],
    config: RunnableConfig,
) -> AsyncGenerator[str, None]:
    """
    Streams output from an agent executor asynchronously, yielding token by token.
    Focuses on the final response content only.
    """
    full_output = []
    
    async for event in agent_executor.astream_events(input_data, config=config, version="v1"):
        event_type = event["event"]
        
        if event_type == "on_llm_stream":
            # Extract token content
            chunk = event.get("data", {}).get("chunk", {})
            content = chunk.get("content", "")
            
            if content:
                yield content
                full_output.append(content)
                await asyncio.sleep(0.02)  # Smooth streaming
                
        elif event_type == "on_agent_finish":
            # Ensure final output is fully streamed
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