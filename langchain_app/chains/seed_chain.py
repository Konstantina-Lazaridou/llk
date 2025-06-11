from langchain.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.base import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_app.models.gemini import get_gemini_model_client
import json
from typing import List
import ast


def seed_chain(prompt_template_file:str, model:BaseChatModel = None) -> RunnableSequence:

    # Get prompt template for seed word generation
    with open(prompt_template_file, "r") as file:
        file_content = file.read()
        prompt_template = PromptTemplate(
            input_variables=["language", "language_level", "word_amount", "word_type"],
            template=file_content,
        )
    
    # Set up model and chain
    if not model:
        model = get_gemini_model_client()
        
    return prompt_template | model.with_retry(retry_if_exception_type=(ValueError, KeyError, SyntaxError), stop_after_attempt=2) | StrOutputParser()

def fetch_seed_words(chain: RunnableSequence, word_type:str, language:str, language_level:str, word_amount:int) -> List[str]:
    
    response = chain.invoke(input={
        "language": language,
        "language_level": language_level,
        "word_amount": word_amount,
        "word_type": word_type
    })
    print(f"Response: {response}")

    word_dict = ast.literal_eval(response.strip())
    print(f"Parsed response: {word_dict}")

    with open("words.json", "r") as f:
        words = json.load(f)
        # Update existing words if they are any
        current_words = words.get(word_type, [])
        current_words.extend(word_dict[word_type])

        # Remove duplicates and sort the words
        words[word_type] = sorted(list(set(current_words)))

        # Write updated words to file
        with open("words.json", "w") as f:
            json.dump(words, f, indent=1)

    return word_dict
