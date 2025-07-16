from langchain_core.prompts import ChatPromptTemplate



promptTemplate = {
    "summarize_error_log": ChatPromptTemplate.from_messages([
        ("system", "You are a analyzer for error logs. Your task is to summarize the error log and provide insights."),
        ("human", "Summarize this error log in bullet points, focusing on:\n- Error types\n- Frequency of errors\n- Critical errors\n- Any patterns\n\nError log:\n{error_log}.\n\n Generate response in such a way that your response is a prompt to the llm. Don't provide any solution or code. Just create prompt."),
        ("placeholder", "{chat_history}"),
        ("placeholder", "{agent_scratchpad}"),
    ]),
}

def get_template(template: str, error_log: str) -> ChatPromptTemplate:
    """
    Returns a ChatPromptTemplate for summarizing the error log.

    :param error_log: The error log to be summarized.
    :return: A ChatPromptTemplate configured for summarizing the error log.
    """
    if not error_log:
        raise ValueError("Error log cannot be empty.")

    # Return the template (you format it later when calling LLM)
    result = promptTemplate.get(template)
    if result is None:
        raise ValueError(f"Template '{template}' not found.")
    return result


