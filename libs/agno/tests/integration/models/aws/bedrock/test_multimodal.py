from pathlib import Path

import pytest

from agno.agent.agent import Agent
from agno.media import Image
from agno.models.aws import AwsBedrock


def test_image_input_bytes():
    """
    Only bytes input is supported for multimodal models
    """
    agent = Agent(model=AwsBedrock(id="us.amazon.nova-pro-v1:0"), markdown=True, telemetry=False, monitoring=False)

    image_path = Path(__file__).parent.parent.parent.joinpath("sample_image.jpg")

    # Read the image file content as bytes
    image_bytes = image_path.read_bytes()

    response = agent.run(
        "Tell me about this image.",
        images=[Image(content=image_bytes, format="jpeg")],
    )

    assert "bridge" in response.content.lower()


@pytest.mark.asyncio
async def test_async_image_input_bytes():
    """Test async image input using bytes with Amazon Nova Pro model.

    Only bytes input is supported for multimodal models.
    """
    agent = Agent(model=AwsBedrock(id="us.amazon.nova-pro-v1:0"), markdown=True, telemetry=False, monitoring=False)

    image_path = Path(__file__).parent.parent.parent.joinpath("sample_image.jpg")

    image_bytes = image_path.read_bytes()

    response = await agent.arun(
        "Tell me about this image.",
        images=[Image(content=image_bytes, format="jpeg")],
    )

    assert "bridge" in response.content.lower()


@pytest.mark.asyncio
async def test_async_image_input_stream():
    """Test async image input with streaming using Amazon Nova Pro model."""
    agent = Agent(model=AwsBedrock(id="us.amazon.nova-pro-v1:0"), markdown=True, telemetry=False, monitoring=False)

    image_path = Path(__file__).parent.parent.parent.joinpath("sample_image.jpg")
    image_bytes = image_path.read_bytes()

    response_stream = await agent.arun(
        "Describe this image in detail.", images=[Image(content=image_bytes, format="jpeg")], stream=True
    )

    responses = []
    async for chunk in response_stream:
        responses.append(chunk)
        assert chunk.content is not None

    assert len(responses) > 0

    full_content = ""
    for r in responses:
        full_content += r.content or ""

    assert "bridge" in full_content.lower()


@pytest.mark.asyncio
async def test_async_multiple_images():
    """Test async processing of multiple images."""
    agent = Agent(model=AwsBedrock(id="us.amazon.nova-pro-v1:0"), markdown=True, telemetry=False, monitoring=False)

    image_path = Path(__file__).parent.parent.parent.joinpath("sample_image.jpg")
    image_bytes = image_path.read_bytes()

    response = await agent.arun(
        "Compare these two images and tell me what you see.",
        images=[Image(content=image_bytes, format="jpeg"), Image(content=image_bytes, format="jpeg")],
    )

    assert response.content is not None
    assert len(response.content) > 0
