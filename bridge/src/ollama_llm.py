import os

import ollama

from src.logger import logger

OLLAMA_MODEL = os.environ["OLLAMA_MODEL"]


def run_ollama(prompt: str) -> str:
    logger.debug(f"Running Ollama model: {OLLAMA_MODEL}")
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]
