import os
from chains.base_chain import base_chain

def main() -> None:

    # Load environment variables
    language = os.environ["LANGUAGE"]
    language_level = os.environ["LANGUAGE_LEVEL"]
    word_type = os.environ["WORD_TYPE"]
    word_amount = os.environ["WORD_AMOUNT"]

    chain = base_chain(prompt_template_file="app/prompts/new_words.txt")
    
    # Generate new words
    
    # Initialize user vocabulary

    # Update prompt storage


if __name__ == "__main__":

    main()