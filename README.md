
# Error Log Analysis and Code Generation Agent

This project implements a sophisticated AI agent designed to analyze error logs, generate code, and interact with users in a conversational manner. It leverages LangChain, Ollama, and Elasticsearch to provide a powerful and flexible solution for developers and system administrators.

## Features

- **Error Log Analysis:** The agent can read and analyze error logs, summarizing key information such as error types, frequencies, and critical issues.
- **Conversational AI:** The agent can engage in a conversation with the user, maintaining context and history for a more natural interaction.
- **Code Generation:** The agent can generate code snippets and solutions based on the analysis of error logs.
- **Tool Integration:** The agent is equipped with tools to read files and interact with external systems like Elasticsearch.
- **Streaming Responses:** The agent streams responses back to the user, providing a more interactive and real-time experience.
- **Extensible Architecture:** The project is designed with a modular architecture, making it easy to add new tools, models, and functionality.

## Project Structure

```
.
├───.gitignore
├───main.py
├───.git/...
├───.venv/
├───agents/
│   └───Agents.py
├───elasticsearch/
│   └───ElasticSearchConfig.py
├───PromptTemplate/
│   └───PromptTemplate.py
├───resource log/
│   ├───es_query.log
│   ├───mrf_browser_error.log
│   └───mrf_error_only.log
├───schema/
│   └───ResponseFormatter.py
├───tools/
│   └───Tools.py
└───utils/
    └───streaming_utils.py
```

- **`main.py`**: The entry point of the application. It initializes the agent, tools, and other components, and starts the conversational loop.
- **`agents/Agents.py`**: Defines the AI agent and its configuration.
- **`tools/Tools.py`**: Implements the tools that the agent can use, such as reading files and summarizing logs.
- **`elasticsearch/ElasticSearchConfig.py`**: Manages the connection to Elasticsearch.
- **`schema/ResponseFormatter.py`**: Defines the data structures for the agent's responses.
- **`PromptTemplate/PromptTemplate.py`**: Contains the prompt templates used to guide the agent's behavior.
- **`utils/streaming_utils.py`**: Provides utility functions for streaming responses from the agent.
- **`resource log/`**: Contains log files that can be used for testing and demonstration.

## Getting Started

### Prerequisites

- Python 3.10+
- Pip
- Ollama
- Elasticsearch (optional)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the environment variables:**

   Create a `.env` file in the root of the project and add the following variables:

   ```
   es-port=9200
   es-domain=localhost
   es-username=your-username
   es-password=your-password
   ```

### Running the Application

1. **Start the Ollama service:**

   Follow the instructions on the [Ollama website](https://ollama.ai/) to download and run the Ollama service.

2. **Run the main application:**

   ```bash
   python main.py
   ```

## Usage

Once the application is running, you can interact with the agent through the command line. The agent will prompt you for input, and you can ask it to analyze error logs, generate code, or answer questions.

**Example:**

```
👤 You: Read the error log from tool and tell me what the problem is. Use the log path: /Users/ajmaharjan/Documents/langChain/errorAgents/resource log/mrf_error_only.log
```

The agent will then read the specified log file, analyze its contents, and provide a summary of the errors it finds.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
