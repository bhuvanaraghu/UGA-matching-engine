"""Tests for Claude prompt chain (mocked API)."""

from unittest.mock import MagicMock, patch

import pytest

from src.pdf_parser.prompt_chain import PromptChain, PromptChainResult


def _mock_response(text: str) -> MagicMock:
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    usage = MagicMock()
    usage.input_tokens = 1000
    usage.output_tokens = 200
    usage.cache_read_input_tokens = 800
    usage.cache_creation_input_tokens = 200
    response.usage = usage
    return response


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("anthropic.Anthropic")
def test_run_executes_six_steps_in_order(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.side_effect = [
        _mock_response("p1 output"),
        _mock_response("p2 output"),
        _mock_response("p3 output"),
        _mock_response("p4 output"),
        _mock_response("p5 output"),
        _mock_response("p6 output"),
    ]

    chain = PromptChain(api_key="test-key")
    result = chain.run("Sample program document text.")

    assert isinstance(result, PromptChainResult)
    assert result.p1 == "p1 output"
    assert result.p6 == "p6 output"
    assert mock_client.messages.create.call_count == 6

    first_call = mock_client.messages.create.call_args_list[0]
    user_content = first_call.kwargs["messages"][0]["content"]
    doc_block = user_content[0]
    assert "cache_control" in doc_block
    assert "PROGRAM DOCUMENT" in doc_block["text"]


@patch.dict("os.environ", {}, clear=True)
def test_raises_without_api_key():
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        PromptChain(api_key=None)


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("anthropic.Anthropic")
def test_retries_on_rate_limit(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    rate_error = Exception("rate limit exceeded")
    ok_response = _mock_response("ok")

    mock_client.messages.create.side_effect = [
        rate_error,
        ok_response,
        ok_response,
        ok_response,
        ok_response,
        ok_response,
        ok_response,
    ]

    chain = PromptChain(api_key="test-key")
    with patch("src.pdf_parser.prompt_chain.time.sleep"):
        result = chain.run("doc")
    assert result.p1 == "ok"
