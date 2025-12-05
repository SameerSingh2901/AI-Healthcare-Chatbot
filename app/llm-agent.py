import logging
from pathlib import Path
from typing import List

import requests

# Import your GraphConnector
from graph_connector import GraphConnector

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Configuration
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
INSTRUCTIONS_PATH = BASE_DIR / "instructions.txt"

OLLAMA_MODEL = "llama3.1:latest"
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # ✅ fixed


# -------------------------
# Helpers
# -------------------------
def load_instructions() -> str:
    if not INSTRUCTIONS_PATH.exists():
        return "You are a helpful medical assistant. Provide clear, concise answers and disclaimers."
    return INSTRUCTIONS_PATH.read_text(encoding="utf-8")


def call_ollama(
    prompt: str, model: str = OLLAMA_MODEL, system_prompt: str = None
) -> str:
    """Direct API call to Ollama localhost."""
    payload = {"model": model, "prompt": prompt, "stream": False}
    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Error calling Ollama API: {str(e)}")


def extract_symptoms(user_input: str) -> List[str]:
    """Use LLM to extract one or more symptoms from natural language as simple words."""
    system_instructions = (
        "You are a symptom extractor. Extract all symptoms from the text. "
        "Return them as a comma-separated list of simple one words (e.g., 'fever, cough, headache'). "
        "Do not add extra text."
    )
    prompt = f"User said: '{user_input}'. Extract all core symptoms in one or two words each."
    response = call_ollama(prompt, system_prompt=system_instructions)

    # Normalize into list
    symptoms = [s.strip().lower() for s in response.split(",") if s.strip()]
    return symptoms


# -------------------------
# Chatbot Logic
# -------------------------
def medical_chatbot():
    """Interactive chatbot with memory, symptom extraction, and graph RAG."""
    print("🤖 Hello! I’m your healthcare assistant.")
    print("Please tell me your symptoms.\n")

    chat_history = []  # keeps previous dialogue
    symptoms = []

    while True:
        user_input = input("You: ").strip()
        chat_history.append({"role": "user", "content": user_input})

        # Check if user is done
        if user_input.lower() in ["no", "none", "that's it", "finished"]:
            if len(symptoms) < 2:
                print("🤖 Please provide at least two symptoms to continue.")
                continue
            break

        # Extract one or more symptoms using LLM
        extracted = extract_symptoms(user_input)
        new_symptoms = [s for s in extracted if s not in symptoms]

        if new_symptoms:
            symptoms.extend(new_symptoms)
            print(f"🤖 Noted: {', '.join(new_symptoms)}.")
        else:
            print("🤖 I couldn’t identify new symptoms from that. Could you rephrase?")

        print("🤖 Do you have any other symptoms?")

    # === Run Graph Query ===
    graph = GraphConnector()
    context_text = graph.build_context_from_symptoms(symptoms)
    graph.close()

    if "No matching diseases" in context_text:
        print("🤖 I couldn’t find any matching diseases for your symptoms.")
        return

    system_instructions = load_instructions()

    # Final context-aware answer
    prompt = f"""Conversation so far:
{chat_history}

Extracted symptoms: {', '.join(symptoms)}

CONTEXT from knowledge graph:
{context_text}

USER QUESTION:
Based on my symptoms, what diseases might be possible and what precautions or treatments are generally recommended?"""

    response = call_ollama(prompt, system_prompt=system_instructions)

    print("\n🤖 Here’s what I found:\n")
    print(response.strip())


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    medical_chatbot()
