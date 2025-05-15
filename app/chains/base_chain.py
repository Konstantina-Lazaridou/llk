from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from models.gemini import GeminiLLM
import json
from typing import List
import ast


def base_chain(prompt_template_file:str) -> LLMChain:

    # Get template for new words
    with open(prompt_template_file, "r") as file:
        prompt_template = file.read()
        final_prompt_template = PromptTemplate(
            input_variables=["language", "language_level", "word_amount", "word_type"],
            template=prompt_template,
        )
    
    # Set up model and chain
    model = GeminiLLM()
    
    # chain = LLMChain(llm=model, prompt=final_prompt_template, verbose=True)
    chain = final_prompt_template | model

    return chain

def fetch_words(chain: LLMChain, word_type:str, language:str, language_level:str, word_amount:int) -> List[str]:
    response = chain.run(language=language, language_level=language_level, word_amount=word_amount, word_type=word_type)
    word_dict = ast.literal_eval(response.strip())

    # Update existing words
    with open("words.json", "r") as f:
        words = json.load(f)
        current_words = words.get(word_type, [])
        current_words.extend(word_dict[word_type])

    # Remove duplicates and sort the words
    words[word_type] = sorted(list(set(current_words)))

    # Write updated words to file
    with open("words.json", "w") as f:
        json.dump(words, f, indent=1)

    return word_dict
