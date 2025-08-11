from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder



promptTemplate = {
    "summarize_error_log": ChatPromptTemplate.from_messages([
        ("system", "You are a analyzer for error logs. Your task is to summarize the error log and provide insights and create me a prompt that could be used by another llm."),
        ("human", 
         '''
            Summarize the provided error log in clear and concise bullet points, with a focus on the following aspects:

                - Types of errors encountered
                - Frequency of each error type
                - Identification of any critical errors
                - Any observable patterns in the errors
                - Error Log:
                    {error_log}

                Format your response as a prompt intended for another LLM. Do not include any solutions or code snippets.

                At the end, briefly indicate the likely cause of the errors and where in the system or process they seem to originate from.
                Also provide a summary of the log in a JSON format with keys "log_summary" and "log_contents". The "log_contents" should contain the original log content.
                Ensure the JSON is well-formed and properly escaped.
                            
                Important: Just provide the prompt without any additional text or explanation.
         '''
         ),
        ("placeholder", "{chat_history}"),
        ("placeholder", "{agent_scratchpad}"),
    ]),
    "general_prompt" : ChatPromptTemplate.from_messages([
        ("system", "You are a helpful code generator assistant."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]),
}

def get_template(template: str) -> ChatPromptTemplate:
    """
    Returns a ChatPromptTemplate for summarizing the error log.

    :param template: The name of the template to retrieve. 
    :return: A ChatPromptTemplate configured for summarizing the error log.
    """
    
    # Return the template (you format it later when calling LLM)
    result = promptTemplate.get(template)
    if result is None:
        raise ValueError(f"Template '{template}' not found.")
    return result


