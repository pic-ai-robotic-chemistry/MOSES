import pytest
from unittest.mock import MagicMock
import sys
import os

# Add project root to sys.path to allow importing project modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# --- Mock LLM ---
@pytest.fixture
def mock_llm():
    """Provides a mock BaseLanguageModel."""
    mock = MagicMock()
    # Configure common methods like invoke, stream, etc. as needed for tests
    mock.invoke = MagicMock()
    mock.with_structured_output = MagicMock(return_value=mock) # Chainable
    return mock

# --- Mock owlready2 Objects ---
# Use MagicMock to simulate owlready2 classes and instances
# We need to be careful as owlready2 does a lot of metaclass magic

@pytest.fixture
def MockThingClass():
    """Factory fixture to create mock owlready2 ThingClass objects."""
    def _create_mock_class(name, is_a=None, subclasses=None, ancestors=None, descendants=None, properties=None, restrictions=None, source=None, information=None):
        mock_cls = MagicMock(spec=True) # Use spec=True for stricter mocking if possible
        mock_cls.name = name
        mock_cls.__name__ = name # Important for some representations

        # Simulate class hierarchy methods
        mock_cls.is_a = is_a if is_a is not None else [] # List of mock parent classes or Restrictions
        mock_cls.subclasses = MagicMock(return_value=subclasses if subclasses is not None else [])
        mock_cls.ancestors = MagicMock(return_value=ancestors if ancestors is not None else [])
        mock_cls.descendants = MagicMock(return_value=descendants if descendants is not None else [])

        # Simulate properties
        mock_cls.get_properties = MagicMock(return_value=properties if properties is not None else [])

        # Simulate custom attributes if used in code
        if hasattr(mock_cls, "source"): # Check if attribute exists before setting
             mock_cls.source = source if source is not None else []
        if hasattr(mock_cls, "information"):
             mock_cls.information = information if information is not None else []

        # Simulate Restriction handling (simplified)
        # A more complex mock might be needed depending on how Restrictions are used
        # is_a might contain mock Restriction objects

        # Allow accessing mocked methods/attributes
        mock_cls.attach_mock = MagicMock()

        return mock_cls
    return _create_mock_class

@pytest.fixture
def MockRestriction():
     """Factory fixture to create mock owlready2 Restriction objects."""
     def _create_mock_restriction(property_mock, type_val, value_mock):
         mock_restr = MagicMock()
         mock_restr.property = property_mock
         mock_restr.type = type_val
         mock_restr.value = value_mock
         return mock_restr
     return _create_mock_restriction

@pytest.fixture
def MockProperty():
    """Factory fixture to create mock owlready2 Property objects."""
    def _create_mock_property(name, domain=None, range_val=None, is_data_prop=True):
         mock_prop = MagicMock()
         mock_prop.name = name
         mock_prop.domain = domain if domain is not None else []
         mock_prop.range = range_val if range_val is not None else []
         # Simulate type (DataProperty vs ObjectProperty)
         mock_prop.__class__ = MagicMock()
         if is_data_prop:
             mock_prop.__class__.__name__ = 'DataProperty'
             # Add owlready2.DataProperty to its bases if needed for isinstance checks
         else:
             mock_prop.__class__.__name__ = 'ObjectProperty'
             # Add owlready2.ObjectProperty to its bases if needed
         return mock_prop
    return _create_mock_property


# --- Mock OntologyTools ---
@pytest.fixture
def mock_ontology_tools(MockThingClass, MockProperty):
    """Provides a mock OntologyTools instance."""
    mock = MagicMock()
    # Mock methods used by agents and workflow
    mock.onto = None # Can be set in tests
    mock.get_class_info = MagicMock(return_value={})
    mock.get_class_properties = MagicMock(return_value=[])
    mock.get_parents = MagicMock(return_value=[])
    mock.get_children = MagicMock(return_value=[])
    mock.get_related_classes = MagicMock(return_value={})
    mock.execute_sparql = MagicMock(return_value={"results": []})
    # Mock other methods as needed by specific tests
    # ...
    return mock

# --- Mock Agents ---
@pytest.fixture
def mock_query_parser_agent(mock_llm):
    from autology_constructor.idea.query_team.query_agents import QueryParserAgent
    agent = QueryParserAgent(model=mock_llm)
    agent.structured_llm = MagicMock() # Mock the internal structured LLM
    return agent

@pytest.fixture
def mock_tool_planner_agent(mock_llm):
     from autology_constructor.idea.query_team.query_agents import ToolPlannerAgent
     agent = ToolPlannerAgent(model=mock_llm)
     agent.structured_llm = MagicMock() # Mock the internal structured LLM
     return agent

@pytest.fixture
def mock_strategy_planner_agent(mock_llm):
     from autology_constructor.idea.query_team.query_agents import StrategyPlannerAgent
     agent = StrategyPlannerAgent(model=mock_llm)
     return agent

@pytest.fixture
def mock_tool_executor_agent(mock_llm, mock_ontology_tools):
     from autology_constructor.idea.query_team.query_agents import ToolExecutorAgent
     # Need to handle the OntologyTools dependency
     agent = ToolExecutorAgent(model=mock_llm)
     # Directly assign the mocked tools instance
     agent.ontology_tools_instance = mock_ontology_tools
     return agent

@pytest.fixture
def mock_sparql_expert_agent(mock_llm):
     from autology_constructor.idea.query_team.query_agents import SparqlExpertAgent
     agent = SparqlExpertAgent(model=mock_llm)
     return agent

@pytest.fixture
def mock_validation_agent(mock_llm):
     from autology_constructor.idea.query_team.query_agents import ValidationAgent
     agent = ValidationAgent(model=mock_llm)
     agent.structured_llm = MagicMock() # Mock the internal structured LLM
     return agent

# --- Mock Query Manager Components ---
@pytest.fixture
def mock_query():
     from autology_constructor.idea.query_team.query_manager import Query
     return Query(natural_query="Test query", originating_team="test_team", originating_agent="test_agent")

@pytest.fixture
def mock_query_state():
     return {
         "query": "Test query",
         "source_ontology": MagicMock(),
         "query_type": "unknown",
         "query_strategy": None,
         "additional_ontology": None,
         "originating_team": "test_team",
         "originating_stage": "unknown",
         "available_classes": ["ClassA", "ClassB"],
         "query_results": {},
         "normalized_query": None,
         "execution_plan": None,
         "validation_report": None,
         "sparql_query": None,
         "status": "initialized",
         "stage": "initialized",
         "previous_stage": None,
         "error": None,
         "messages": []
     }

@pytest.fixture
def mock_compiled_graph():
    """Provides a mock compiled LangGraph."""
    mock_graph = MagicMock()
    mock_graph.invoke = MagicMock() # Mock the invoke method
    return mock_graph

@pytest.fixture
def mock_query_queue_manager():
     from autology_constructor.idea.query_team.query_manager import QueryQueueManager
     manager = QueryQueueManager()
     # Mock internal structures if needed for specific tests, e.g., mock PriorityQueue
     manager.pending_queries = MagicMock()
     manager.cache = MagicMock() # Mock the cache
     return manager

# Note: Mocking ThreadPoolExecutor might be complex.
# Often, it's easier to test the tasks submitted to it synchronously
# or mock the submit method to control execution. 