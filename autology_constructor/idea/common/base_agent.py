from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from typing import Type, TypeVar, List, Optional, Any
from pydantic import BaseModel
from langchain_core.language_models import BaseLanguageModel

# Generic type for Pydantic models used in structured output
T = TypeVar("T", bound=BaseModel)

class AgentTemplate:
    """A template class for creating language model agents with tools.

    This class provides functionality to create and configure an agent workflow
    that combines a language model with a set of tools. The workflow allows
    the agent to use tools to accomplish tasks through a series of steps.

    Attributes:
        name (str): The name identifier for this agent template.
        tools (list): The list of tools available to the agent (can be empty).
        system_prompt (str): The system prompt that defines the agent's behavior.
        model_instance: The base language model instance provided during initialization.
        model_with_tools: The language model instance potentially bound with tools.
    """

    def __init__(self, model: BaseLanguageModel, name: str = "BaseAgent", tools: Optional[List[Any]] = None, system_prompt: str = "You are a helpful AI assistant."):
        """Initializes the AgentTemplate.

        Args:
            model: The language model instance to use.
            name: The name identifier for this agent template.
            tools: A list of tools available to the agent. Defaults to an empty list.
            system_prompt: The system prompt defining the agent's behavior.
        """
        if tools is None:
            tools = []

        self.name = name
        self.tools = tools
        self.system_prompt = system_prompt
        self.model_instance = model # Store the original model instance

        # Bind tools immediately if provided, store separately
        if self.tools:
            self.model_with_tools = self.model_instance.bind_tools(self.tools)
        else:
            self.model_with_tools = self.model_instance # No tools to bind

    def _get_structured_llm(self, pydantic_schema: Type[T]):
        """Returns an LLM instance configured for structured output with the given Pydantic schema."""
        if not self.model_instance:
            raise ValueError(f"Model instance not available in agent '{self.name}' to configure structured output.")
        try:
            # Use the original model instance for configuring structured output
            return self.model_instance.with_structured_output(pydantic_schema)
        except Exception as e:
            # Handle potential errors during configuration
            raise RuntimeError(f"Failed to configure structured output for schema {pydantic_schema.__name__} in agent '{self.name}': {e}") from e

    # Keeping create_agent and create_react_agent for potential compatibility or future use
    # Note: They might need adjustments based on the new __init__ structure

    