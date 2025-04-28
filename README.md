# Language Learning Konstantina

Personalized LLM-based application to assist language learning.

This Streamlit app helps users expand their foreign language vocabulary via a curated list of topic-related words tailored to their language level. Users can mark unfamiliar words, which are automatically translated in English in the background. These new words, along with their explanations, are then stored and displayed in the app. It serves as an effective tool for learning, reviewing, and reinforcing vocabulary.

# Installation

Create a `.env` file based on `.env_`.
Run the following:
```
poetry install
eval $(poetry env activate)
export POETRY_PLUGIN_DOTENV_LOCATION=.env
```

# Usage

## Prerequisites

The app assumes there is a `words.json` with the input words and a `vocabulary.json` for building the user's vocabulary.
For example, with regards to driving a car, on app start the `words.json` for learning German would look like:

```json
{
  "driving": [
    "abbiegen",
    "...",
    "zur\u00fccksetzen"
  ]
}
```

and `vocabulary.json` like:

```json
{
  "driving": {
    "known": [
      "abbiegen",
      "...",
      "zur\u00fccksetzen"
    ],
    "unknown": [
    ]
  }
}
```

## Run

```

poetry run -vvv streamlit run app.py

```

The app would look like:

<img src="images/app_screenshot_1.png" alt="Word selection" width="70%" />
<img src="images/app_screenshot_2.png" alt="Word translations" width="70%" />
