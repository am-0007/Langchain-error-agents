import os
import asyncio
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.runnables import Runnable
import os
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda
from typing import List, Optional, Any, Dict
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool

from PromptTemplate.PromptTemplate import get_template

class LogReader:
    def __init__(self, llm: ChatOllama):
        self.llm = llm
    
    # @tool(description="""Reads and optionally summarizes error logs. If no log_path is provided, a default log file will be read.""")
    def enhanced_log_reader(self, log_path: str = "") -> str:
        path = get_path_to_log_file(log_path)
        print(f"Reading log file from: {path}")
        try:
            with open(path, "r") as file:
                contents = file.read()
                if len(contents) > 500:
                    print("Summarizing log contents...")
                    summary = self.summarize_log(contents, self.llm)
                    return f"Error:\n{summary}\n\n"
                return contents
        except FileNotFoundError:
            return f"Log file not found at {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
        
    def summarize_log(self, log_contents: str, llm: ChatOllama) -> str:
        """Standalone summarization function"""
        if llm and len(log_contents) > 500:
            summarize_prompt = get_template("summarize_error_log", error_log=log_contents)
            summarize_chain = (
                summarize_prompt 
                | llm 
                | RunnableLambda(lambda x: getattr(x, 'content', x) if not isinstance(x, str) else x)
            )
            summary = summarize_chain.invoke({"error_log": log_contents})
            print(f"Summary log: {summary}")
            print("-----" * 80)
            return f"""
                {{ 
                    "log_summary": "{summary}",
                    "log_contents": "{log_contents.replace('\"', '\\"').replace('\\n', '\\\\n')}"
                }}
                """.strip()
        return log_contents.strip()

 
def register_tools(llm: ChatOllama):
    log_reader = LogReader(llm)

    @tool(description="Reads and summarizes error logs. Defaults to a specific log file if no path is provided.")
    def enhanced_log_reader(log_path: str = "") -> str:
        return log_reader.enhanced_log_reader(log_path)

    return [enhanced_log_reader]


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
    
    print(f"Using default log file path: {default_log_path}")
    
    return default_log_path

# # 4. Modified registration
# def register_tools(llm: ChatOllama):
#     enhanced_tool = enhanced_log_reader
#     return llm.bind_tools([enhanced_tool])

if __name__ == "__main__":
    log_path = "/Users/ajmaharjan/Documents/langChain/errorAgents/resource log/mrf_error_only.log"
    print(get_path_to_log_file(log_path=log_path))
    #print(asyncio.run(read_error_log.ainvoke({})))
