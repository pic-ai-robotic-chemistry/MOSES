# Tests for query_team schemas
import pytest
from pydantic import ValidationError

# Import schemas
from autology_constructor.idea.query_team.schemas import (
    NormalizedQuery,
    ToolCallStep,
    DimensionReport,
    ValidationReport
)

# Add basic tests here according to the plan 