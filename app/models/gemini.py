from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

def get_gemini_model_client() -> BaseChatModel:
    return init_chat_model("gemini-2.0-flash", model_provider="google_genai")
