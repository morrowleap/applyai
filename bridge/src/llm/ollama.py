import os

import ollama

from src.logger import logger


def run_ollama(prompt: str) -> str:
    model = os.environ["OLLAMA_MODEL"]
    logger.debug(f"Running Ollama model: {model}")
    logger.debug(f"Prompt:\n{prompt}")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        think=False,
    )
    content = response["message"]["content"]
    logger.debug(f"Response:\n{content}")
    return content
