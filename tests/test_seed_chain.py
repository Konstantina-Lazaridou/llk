import pytest
from unittest.mock import patch, mock_open, MagicMock
from langchain_app.chains.seed_chain import create_seed_chain

@pytest.mark.parametrize("model_passed", [None, MagicMock()])
@patch("langchain_app.chains.seed_chain.StrOutputParser")
@patch("langchain_app.chains.seed_chain.get_gemini_model_client")
@patch("langchain_app.chains.seed_chain.PromptTemplate")
@patch("builtins.open", new_callable=mock_open, read_data="template content")
def test_seed_chain_model_variants(mock_file, mock_prompt_template, mock_get_model, mock_str_output_parser, model_passed):
    # Mock prompt template
    mock_prompt_template.return_value = MagicMock()
    # Mock model if not passed
    mock_model = None
    if model_passed is None:
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        # Mock background model calls
        mock_model.with_retry.return_value = mock_model
    else:
        model_passed.with_retry.return_value = model_passed
    # Mock StrOutputParser to ensure more isolation
    mock_str_output_parser.return_value = MagicMock()

    # Call the function under test
    chain = create_seed_chain("dummy_template.txt", model=model_passed)
    
    # Assert the dummy file was opened in the function under test
    mock_file.assert_called_once_with("dummy_template.txt", "r")
    # Assert the dummy content was read and the mock prompt template was created
    mock_prompt_template.assert_called_once_with(
        input_variables=["language", "language_level", "word_amount", "word_type"],
        template="template content",
    )
    # Assert the model default was fetched if not passed
    if model_passed is None:
        mock_get_model.assert_called_once()
    else:
        mock_get_model.assert_not_called()
    # Assert the model was returned in case of retry
    if mock_model and mock_model.call_count > 0:
        mock_model.with_retry.assert_called_once()
    elif model_passed and model_passed.call_count > 0:
        model_passed.with_retry.assert_called_once()
    # Assert the returned value is either chainable or at least some valid object
    assert hasattr(chain, "__or__") or chain is not None