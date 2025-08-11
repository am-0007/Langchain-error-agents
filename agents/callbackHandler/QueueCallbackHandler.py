import asyncio
from langchain.callbacks.base import AsyncCallbackHandler


class QueueCallbackHandler(AsyncCallbackHandler):
    """Callback handler that puts tokens into a queue."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.final_answer_seen = False

    async def __aiter__(self):
        while True:
            if self.queue.empty():
                await asyncio.sleep(0.1)
                continue
            token_or_done = await self.queue.get()

            if token_or_done == "<<DONE>>":
                # this means we're done
                return
            if token_or_done:
                yield token_or_done

    async def on_llm_new_token(self, *args, **kwargs) -> None:
        """Put new token in the queue."""
        #print(f"on_llm_new_token: {args}, {kwargs}")
        chunk = kwargs.get("chunk")
        if chunk:
            # check for enhanced_log_reader tool call
            if tool_calls := chunk.message.additional_kwargs.get("tool_calls"):
                if tool_calls[0]["function"]["name"] == "enhanced_log_reader":
                    # this will allow the stream to end on the next `on_llm_end` call
                    self.final_answer_seen = True
        self.queue.put_nowait(kwargs.get("chunk"))
        return

    async def on_llm_end(self, *args, **kwargs) -> None:
        """Put None in the queue to signal completion."""
        #print(f"on_llm_end: {args}, {kwargs}")
        # this should only be used at the end of our agent execution, however LangChain
        # will call this at the end of every tool call, not just the final tool call
        # so we must only send the "done" signal if we have already seen the final_answer
        # tool call
        if self.final_answer_seen:
            self.queue.put_nowait("<<DONE>>")
        else:
            self.queue.put_nowait("<<STEP_END>>")
        return