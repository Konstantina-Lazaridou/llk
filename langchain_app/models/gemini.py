import os
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

def get_gemini_model_client() -> BaseChatModel:
    return init_chat_model(model= os.environ["GEMINI_VERSION"], model_provider="google_genai")
