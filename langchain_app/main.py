import os
from chains.seed_chain import create_seed_chain, fetch_seed_words
from langchain.globals import set_verbose
from langchain.globals import set_debug
# set_debug(True)
# set_verbose(True)

def main() -> None:

    # Load environment variables
    language = os.environ["LANGUAGE"]
    language_level = os.environ["LANGUAGE_LEVEL"]
    word_amount = os.environ["WORD_AMOUNT"]
    word_type = os.environ["WORD_TYPE"]
    seed_prompt = os.environ["SEED_PROMPT"]
    
    # Generate seed words for user's language level
    seed_words = fetch_seed_words(
        chain=create_seed_chain(prompt_template_file=seed_prompt),
        language=language,
        language_level=language_level,
        word_amount=word_amount,
        word_type=word_type
    )
    print(f"Seed words generated: {seed_words}")
    
    # Initialize user vocabulary

    # Update prompt storage


if __name__ == "__main__":

    main()