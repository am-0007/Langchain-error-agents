import json
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import ChatOllama

from PromptTemplate.PromptTemplate import get_template
from tools.Tools import register_tools
from .callbackHandler.QueueCallbackHandler import QueueCallbackHandler


import asyncio  # needed for async support
from langchain_core.runnables import RunnableConfig


class customAgentExecutor:
    chat_history: List[BaseMessage]

    def __init__(self, llm: ChatOllama, max_iterations: int = 3) -> None:
        self.chat_history = []
        self.max_iterations = max_iterations
        self.tools = register_tools(llm)
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.query_prompt = get_template("general_prompt")
        self.agent: RunnableSerializable = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: x.get("agent_scratchpad", []),
            }
            | self.query_prompt
            | llm.bind_tools(self.tools, tool_choice="auto")
        )

    async def invoke(self, input: str, streamer: QueueCallbackHandler, verbose: bool = False) -> dict:
        count = 0
        agent_scratchpad = []

        while count < self.max_iterations:
            # Stream response from agent
            response_stream = self.agent.with_config(callbacks=[streamer])
            queue = streamer.queue

            # Start streaming agent output
            output = None
            async for chunk in response_stream.astream({
                "input": input,
                "chat_history": self.chat_history,
                "agent_scratchpad": agent_scratchpad
            }):
                if output is None:
                    output = chunk
                else:
                    output += chunk

                if chunk.content:
                    print(chunk.content, end="", flush=True)

                # If we get tool calls, break and execute tool
                tool_calls = chunk.additional_kwargs.get("tool_calls")
                if tool_calls:
                    break

            # If no tool calls → final response
            if not output.tool_calls:
                final_out_text = output.content
                self.chat_history.extend([
                    HumanMessage(content=input),
                    AIMessage(content=final_out_text)
                ])
                return {"output": final_out_text}

            # Handle tool call
            tool_call = output.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            tool = self.tool_map.get(tool_name)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found.")

            if verbose:
                print(f"\nTool called: {tool_name} with args {tool_args}")

            # Execute tool (await if async)
            if hasattr(tool, "ainvoke"):
                tool_output = await tool.ainvoke(tool_args)
            else:
                tool_output = tool.invoke(tool_args)

            if verbose:
                print(f"Tool output: {tool_output}")

            # Append tool input & output to scratchpad
            agent_scratchpad.append(ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_call_id
            ))

            count += 1

            print("\n" + "=" * 80)
            print("History:: ", self.chat_history)
            print("\n" + "=" * 80)

        return {"output": "[Max iterations reached without final answer.]"}
    


def get_agent_executor(llm: ChatOllama, max_iterations: int = 3) -> customAgentExecutor:
    return customAgentExecutor(llm, max_iterations)
