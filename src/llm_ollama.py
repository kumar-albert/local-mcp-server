import ollama
from src.utils import extract_json
MODEL = "llama3.1"

def think(conversation: list) -> dict:
    response = ollama.chat(
        model=MODEL,
        messages=conversation,
    )
    text = response["message"]["content"]
    return extract_json(text)