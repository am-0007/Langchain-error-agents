import os
import asyncio
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

@tool(description="Reads the error log from the given path and returns its contents.")
async def read_error_log(log_path: str = "") -> str:
   path = get_path_to_log_file(log_path=log_path)
   print(f"Reading log file from: {path}")
   return await read_resource(uri=path)
     
async def read_resource(uri: str) -> str:
    async def read_log_file(uri: str) -> str:
        """
        Reads the log file and returns its contents.
        """
        try: 
            with open(uri, "r") as file:
                log_contents = file.read()
            return log_contents
        except FileNotFoundError:
            return f"Log file not found at {uri}. Please check the path."

    
    log_contents = await read_log_file(uri)
    return log_contents



def get_path_to_log_file(log_path: str = "") -> str:
    """
    Returns the path to the log file. If a valid log_path is provided and exists, it is returned.
    Otherwise, a default path is constructed and returned.
    """
    if log_path and os.path.isfile(log_path):
        return log_path

    # Determine the directory of the current file
    current_file_path = os.path.abspath(__file__)
    
    # Assuming the project root is two levels up from this file
    project_root = os.path.abspath(os.path.join(current_file_path, "..", ".."))
    
    # Construct the default log file path
    default_log_path = os.path.join(project_root, "resource log", "mrf_error_only.log")
    
    return default_log_path

tools = [read_error_log]


def register_tools(llm : ChatOllama):
    return llm.bind_tools(tools)

if __name__ == "__main__":
    log_path = "/Users/ajmaharjan/Documents/deerhold/mcp/error_agent/resource log/mrf_error_only.log"
    print(get_path_to_log_file(log_path=log_path))
    print(asyncio.run(read_error_log.ainvoke({"log_path": log_path})))