import os

import ollama

from src.logger import logger

OLLAMA_MODEL = os.environ["OLLAMA_MODEL"]


def run_ollama(prompt: str) -> str:
    logger.debug(f"Running Ollama model: {OLLAMA_MODEL}")
    logger.debug(f"Prompt:\n{prompt}")
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        think=False,
    )
    content = response["message"]["content"]
    logger.debug(f"Response:\n{content}")
    return content
