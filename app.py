from __future__ import annotations
import streamlit as st
st.set_page_config(layout="wide")
from streamlit.runtime.state import SessionStateProxy
import json
from collections import OrderedDict
import ast
import os
import asyncio
from transformers import pipeline
import transformers
import torch
torch.classes.__path__ = []

def save_progress(vocabulary: dict, word_type: str, meanings: OrderedDict, state: SessionStateProxy) -> None:
    with open("vocabulary.json", "w") as f:
        data = {"known": sorted(list(set(vocabulary["known"]))), "unknown": sorted(list(set(vocabulary["unknown"])))}
        json.dump({word_type: data}, f, indent=2)
    with open("meanings.json", "w") as f:
        meanings = OrderedDict(sorted(meanings.items()))
        json.dump(meanings, f, indent=2)
    state.saved = True

async def get_meaning(word: str, textgen_pipeline: transformers.pipelines.Pipeline) -> None:
    """Generate the meaning of a German word in the form of an English phrase."""
    messages = [
        {"role": "system", "content": "You are a German native speaker and teach German to English speakers. You are proficient in English. You answer in English and try to be easily understandable for a student learning the C1 German level."},
        {"role": "user", "content": f"Please give me a phrase that contains a short explanation of the word '{word}' in the context of driving a car, including a few synonyms in German. Your answer should be formatted into a Python dictionary where the key is 'meaning' and the value is the short phrase explaining the meaning of the given word. Please include nothing else in your answer other than this dictionary with this one key. Please don't start the answer with '```python' and also don't end the answer with '```'."},
    ]
    retries = 2
    for _ in range(retries):
        outputs = textgen_pipeline(messages, max_new_tokens=256, return_full_text=False)
        try:
            response = ast.literal_eval(outputs[0]["generated_text"].strip())["meaning"]
            st.session_state.meanings[word] = response
            print(f"Word: '{word}', Output: '{outputs}'")
            return
        except (ValueError, KeyError, SyntaxError) as e:
            print(f"Output parsing error: {e}. Retrying...")
            continue

async def app(word_type: str, language: str, language_level: str, textgen_pipeline: transformers.pipelines.Pipeline) -> None:
    """Update and enrich user vocabulary interactively for given input word type."""

    vocabulary = None  # the users known and unknown words, separated per word type
    current_vocabulary = None  # the current word type vocabulary
    meanings = None  # the meanings of the words in the vocabulary
    
    # Load user vocabulary and check if it exists

    with open("vocabulary.json", "r") as f:
        vocabulary = json.load(f)
    if not vocabulary:
        message = "Error: vocabulary not found. Cannot start the app."
        st.write(message) 
        st.stop()  # sys.exit(1) was reloading the app
    current_vocabulary = vocabulary[word_type] if word_type in vocabulary else None
    if not current_vocabulary:
        message = f"Error: vocabulary for word type '{word_type}' not found. Cannot start the app."
        st.write(message)
        st.stop()
    
    # Load word meanings file

    with open("meanings.json", "r") as f:
        meanings = json.load(f)
        meanings = OrderedDict(sorted(meanings.items()))
    
    # Initialize words and meanings if they don't exist yet in this session state

    if 'known_words' not in st.session_state:
        st.session_state.known_words = current_vocabulary["known"].copy()
        st.session_state.updated_known_words = current_vocabulary["known"].copy()
    if 'unknown_words' not in st.session_state:
        st.session_state.unknown_words = current_vocabulary["unknown"].copy()
    if 'meanings' not in st.session_state:
        st.session_state.meanings = meanings.copy()

    # Initialize flags if they doesn't exist yet in this session state

    if 'saved' not in st.session_state:
        st.session_state.saved = False
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = {}
        for word in st.session_state.known_words:
            # Initialize the button clicked state for each word in the vocabulary
            if word not in st.session_state.button_clicked:
                st.session_state.button_clicked[f'{word}'] = False

    # Start the quiz

    st.title(f"Learn {word_type} {language} verbs!")
    st.header("🎯 Select unknown words")
    st.subheader(f"This is a list of {language} words that correspond to your {language_level} level. \
                 Select the words you don't know so you can :diving_mask: into them later on. \
                 Allow time between clicking each word to let the translation be generated in the background. \
                 The new unknown words and their meanings will be shown in the lists below.")

    # Display all words in the vocabulary and let user mark the words they don't currently know
    # The meanings of the unknown words will be fetched asynchronously

    def update_meanings(generation_task: asyncio.Task, new_unknown_word: str) -> None:
        # Did not work because of 'new_unknown_word' being different than intented
        """Update the meanings dictionary when a new word meaning is done being generated."""
        result = generation_task.result()
        # nonlocal meanings
        # meanings[new_unknown_word] = result
        st.session_state.meanings[new_unknown_word] = result
        print(f"Meanings state update: {st.session_state.meanings}")

    item_num_per_row = 10
    # Display words in each row horizontally
    for i in range(0, len(st.session_state.known_words), item_num_per_row):
        words_in_row = st.session_state.known_words[i:i+item_num_per_row]
        columns = st.columns(len(words_in_row))
        for col, word in zip(columns, words_in_row):
            with col:
                # If the word is clicked, remove the word from known words and add it to unknown words to use for review later
                if not st.session_state.button_clicked[f'{word}']:
                    if st.button(word, key=word):
                        st.session_state.button_clicked[f'{word}'] = True
                        # Enable save button every time a new word exists
                        st.session_state.saved = False
                        # Save progress
                        st.session_state.unknown_words.append(word)
                        st.session_state.updated_known_words.remove(word)
                        # Get the meaning for the unknown word
                        if word not in st.session_state.meanings:
                            generation_task = asyncio.create_task(get_meaning(word=word, textgen_pipeline=textgen_pipeline))
                            # generation_task.add_done_callback(lambda task: update_meanings(task, word))
                # If the word is already in unknown words, disable the button
                else:
                    st.button(f"{word} 	✅", disabled=True, key=word)
    
    # Update dictionaries to reflect the changes in the session state
    current_vocabulary["known"] = st.session_state.updated_known_words
    current_vocabulary["unknown"] = st.session_state.unknown_words
    meanings = st.session_state.meanings

    st.markdown("<div style='width: 100%; height: 40px;'></div>", unsafe_allow_html=True)

    st.header(f"📚 Your {word_type} vocabulary")
    # st.write(st.session_state.unknown_words)
    with st.expander("Open/close word list"):
        for idx, word in enumerate(st.session_state.unknown_words, start=1):
            st.write(f"{idx}. {word}")

    st.markdown("<div style='width: 100%; height: 40px;'></div>", unsafe_allow_html=True)
    
    st.header(f":flag-us: Available translations")
    # st.write(st.session_state.meanings)
    with st.expander("Open/close meanings list"):
        for word, meaning in st.session_state.meanings.items():
            st.markdown(f"**{word.capitalize()}**: {meaning}")

    st.markdown("<div style='width: 100%; height: 40px;'></div>", unsafe_allow_html=True)

    # Save progress
    col1, col2 = st.columns(2)

    with col1:
        st.header("📌 Save your progress")
        st.subheader("Save the unknown words you've selected and their meanings to continue learning later on.")
        st.button("Save", on_click=save_progress, args=(current_vocabulary, word_type, meanings, st.session_state))
        if st.session_state.saved:
            st.write("🎉 Your progress has been saved!")
    with col2:
        st.header(":boom: Update translations")
        st.subheader("Click the button to update the table with the latest meanings of the unknown words.")
        st.session_state.meanings = OrderedDict(sorted(st.session_state.meanings.items()))
        meanings = st.session_state.meanings
        st.button("Update")  # session is rerun when the button is clicked and the dict is updated


async def main() -> None:
    """Update and enrich user vocabulary interactively for given input word type."""

    word_type = os.environ["WORD_TYPE"]
    language = os.environ["LANGUAGE"]
    language_level = os.environ["LANGUAGE_LEVEL"]

    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    textgen_pipeline = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
    )

    await app(word_type=word_type, language=language, language_level=language_level, textgen_pipeline=textgen_pipeline)

if __name__ == "__main__":
    asyncio.run(main())    