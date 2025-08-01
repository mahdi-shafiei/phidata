from typing import Optional

import pytest

from agno.agent import Agent  # noqa
from agno.models.aws import AwsBedrock
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.yfinance import YFinanceTools


def test_tool_use():
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = agent.run("What is the current price of TSLA?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None


def test_tool_use_stream():
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response_stream = agent.run("What is the current price of TSLA?", stream=True, stream_intermediate_steps=True)

    responses = []
    tool_call_seen = False

    for chunk in response_stream:
        responses.append(chunk)

        # Check for ToolCallStartedEvent or ToolCallCompletedEvent
        if chunk.event in ["ToolCallStarted", "ToolCallCompleted"] and hasattr(chunk, "tool") and chunk.tool:
            if chunk.tool.tool_name:
                tool_call_seen = True

    assert len(responses) > 0
    assert tool_call_seen, "No tool calls observed in stream"
    full_content = ""
    for r in responses:
        full_content += r.content or ""


def test_parallel_tool_calls():
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = agent.run("What is the current price of TSLA and AAPL?")

    # Verify tool usage
    tool_calls = []
    for msg in response.messages:
        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    assert len([call for call in tool_calls if call.get("type", "") == "function"]) >= 2  # Total of 2 tool calls made
    assert response.content is not None


def test_multiple_tool_calls():
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True), DuckDuckGoTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = agent.run("What is the current price of TSLA and what is the latest news about it?")

    # Verify tool usage
    tool_calls = []
    for msg in response.messages:
        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    assert len([call for call in tool_calls if call.get("type", "") == "function"]) >= 2  # Total of 2 tool calls made
    assert response.content is not None


def test_tool_call_custom_tool_no_parameters():
    def get_the_weather_in_tokyo():
        """
        Get the weather in Tokyo
        """
        return "It is currently 70 degrees and cloudy in Tokyo"

    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[get_the_weather_in_tokyo],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = agent.run("What is the weather in Tokyo?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None
    assert "70" in response.content


def test_tool_call_custom_tool_optional_parameters():
    def get_the_weather(city: Optional[str] = None):
        """
        Get the weather in a city

        Args:
            city: The city to get the weather for
        """
        if city is None:
            return "It is currently 70 degrees and cloudy in Tokyo"
        else:
            return f"It is currently 70 degrees and cloudy in {city}"

    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[get_the_weather],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = agent.run("What is the weather in Paris?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None
    assert "70" in response.content


def test_tool_call_list_parameters():
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[ExaTools()],
        instructions="Use a single tool call if possible",
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = agent.run(
        "What are the papers at https://arxiv.org/pdf/2307.06435 and https://arxiv.org/pdf/2502.09601 about?"
    )

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    tool_calls = []
    for msg in response.messages:
        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    for call in tool_calls:
        if call.get("type", "") == "function":
            assert call["function"]["name"] in ["get_contents", "exa_answer", "search_exa"]
    assert response.content is not None


# ==================== ASYNC TESTS ====================


@pytest.mark.asyncio
async def test_async_tool_use():
    """Test async tool usage with Claude model."""
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun("What is the current price of TSLA?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None


@pytest.mark.asyncio
async def test_async_tool_use_stream():
    """Test async streaming tool usage."""
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response_stream = await agent.arun(
        "What is the current price of TSLA?", stream=True, stream_intermediate_steps=True
    )

    responses = []
    tool_call_seen = False

    async for chunk in response_stream:
        responses.append(chunk)

        # Check for ToolCallStartedEvent or ToolCallCompletedEvent
        if chunk.event in ["ToolCallStarted", "ToolCallCompleted"] and hasattr(chunk, "tool") and chunk.tool:
            if chunk.tool.tool_name:
                tool_call_seen = True

    assert len(responses) > 0
    assert tool_call_seen, "No tool calls observed in stream"


@pytest.mark.asyncio
async def test_async_parallel_tool_calls():
    """Test async parallel tool calls."""
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun("What is the current price of TSLA and AAPL?")

    # Verify tool usage
    tool_calls = []
    for msg in response.messages:
        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    assert len([call for call in tool_calls if call.get("type", "") == "function"]) >= 2
    assert response.content is not None


@pytest.mark.asyncio
async def test_async_multiple_tool_calls():
    """Test async multiple different tool calls."""
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[YFinanceTools(cache_results=True), DuckDuckGoTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun("What is the current price of TSLA and what is the latest news about it?")

    # Verify tool usage
    tool_calls = []
    for msg in response.messages:
        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    assert len([call for call in tool_calls if call.get("type", "") == "function"]) >= 2
    assert response.content is not None


@pytest.mark.asyncio
async def test_async_tool_call_custom_tool_no_parameters():
    """Test async custom tool with no parameters."""

    def get_the_weather_in_tokyo():
        """
        Get the weather in Tokyo
        """
        return "It is currently 70 degrees and cloudy in Tokyo"

    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[get_the_weather_in_tokyo],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun("What is the weather in Tokyo?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None
    assert "70" in response.content


@pytest.mark.asyncio
async def test_async_tool_call_custom_tool_optional_parameters():
    """Test async custom tool with optional parameters."""

    def get_the_weather(city: Optional[str] = None):
        """
        Get the weather in a city

        Args:
            city: The city to get the weather for
        """
        if city is None:
            return "It is currently 70 degrees and cloudy in Tokyo"
        else:
            return f"It is currently 70 degrees and cloudy in {city}"

    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[get_the_weather],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun("What is the weather in Paris?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None
    assert "70" in response.content


@pytest.mark.asyncio
async def test_async_tool_call_list_parameters():
    """Test async tool calls with list parameters."""
    agent = Agent(
        model=AwsBedrock(id="anthropic.claude-3-sonnet-20240229-v1:0"),
        tools=[ExaTools()],
        instructions="Use a single tool call if possible",
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun(
        "What are the papers at https://arxiv.org/pdf/2307.06435 and https://arxiv.org/pdf/2502.09601 about?"
    )

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    tool_calls = []
    for msg in response.messages:
        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)
    for call in tool_calls:
        if call.get("type", "") == "function":
            assert call["function"]["name"] in ["get_contents", "exa_answer", "search_exa"]
    assert response.content is not None


@pytest.mark.asyncio
async def test_async_nova_tool_use():
    """Test async tool usage with Nova model (if available)."""
    agent = Agent(
        model=AwsBedrock(id="amazon.nova-lite-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response = await agent.arun("What is the current price of TSLA?")

    # Verify tool usage
    assert any(msg.tool_calls for msg in response.messages)
    assert response.content is not None


@pytest.mark.asyncio
async def test_async_nova_tool_use_stream():
    """Test async streaming tool usage with Nova model (if available)."""
    agent = Agent(
        model=AwsBedrock(id="amazon.nova-lite-v1:0"),
        tools=[YFinanceTools(cache_results=True)],
        markdown=True,
        telemetry=False,
        monitoring=False,
    )

    response_stream = await agent.arun(
        "What is the current price of TSLA?", stream=True, stream_intermediate_steps=True
    )

    responses = []
    tool_call_seen = False

    async for chunk in response_stream:
        responses.append(chunk)

        # Check for ToolCallStartedEvent or ToolCallCompletedEvent
        if chunk.event in ["ToolCallStarted", "ToolCallCompleted"] and hasattr(chunk, "tool") and chunk.tool:
            if chunk.tool.tool_name:
                tool_call_seen = True

    assert len(responses) > 0
    assert tool_call_seen, "No tool calls observed in stream"
