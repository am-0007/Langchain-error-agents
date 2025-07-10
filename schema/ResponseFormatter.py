from pydantic import BaseModel, Field, conlist

class ContentItem(BaseModel):
    type: str = Field(default="output_text", description="The type of content, e.g., 'output_text'.")
    text: str = Field(description="The detailed and complete answer to the user's question.")
    annotations: list = Field(default_factory=list, description="A list of annotations, typically empty.")

class Message(BaseModel):
    id: str = Field(default="msg_generated", description="A unique identifier for the message.")
    type: str = Field(default="message", description="The type of message, e.g., 'message'.")
    role: str = Field(default="assistant", description="The role of the sender, e.g., 'assistant'.")
    content: conlist(ContentItem, min_length=1) = Field(description="A list of content items.")

class LLMResponse(BaseModel):
    """Defines the JSON structure for the AI's response, mimicking OpenAI's message format."""
    messages: conlist(Message, min_length=1, max_length=1) = Field(description="A list containing a single message from the AI.")