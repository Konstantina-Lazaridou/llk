from langchain.llms import BaseLLM
from google import genai
import os
from typing import List, Dict, Any, Optional

class GeminiLLM(BaseLLM):
    
    api_key: str = os.environ["GOOGLE_AI_STUDIO_API_KEY"]
    model: str = "gemini-2.0-flash"
    client: genai.Client = None

    def __init__(self, **data):
        super().__init__(**data)
        object.__setattr__(self, 'client', genai.Client(api_key=self.api_key))

    def _generate(self, prompt: str) -> str:
        retries = 2
        for _ in range(retries):
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            try:
                response_string = response.to_json_dict()["candidates"][0]["content"]["parts"][0]["text"]
                response_string = response_string.replace("```", "").strip()
            except (ValueError, KeyError, SyntaxError) as e:
                print(f"Output parsing error: {e}. Retrying...")
                continue
        return response_string

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.model}

    @property
    def _llm_type(self) -> str:
        return "Google Gemini"
