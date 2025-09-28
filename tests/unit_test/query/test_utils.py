# Tests for query_team utils
import pytest
import json

# Import utils
from autology_constructor.idea.query_team.utils import (
    parse_json,
    format_owlready2_value,
    format_sparql_results,
    extract_variables_from_sparql,
    TextFormatter,
    JsonFormatter,
    HtmlFormatter,
    ResultFormatter,
    format_query_results,
    format_sparql_error
)

# Import mock objects if needed (e.g., from conftest)
# from .conftest import MockThingClass

# Add basic tests here according to the plan 