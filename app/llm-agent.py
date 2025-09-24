from pathlib import Path
from typing import List, Dict, Any
import logging

# LangChain / Ollama imports
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

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

OLLAMA_MODEL = "llama3.1:latest"  # adjust if your local Ollama model differs

# -------------------------
# Helpers
# -------------------------
def load_instructions() -> str:
    if not INSTRUCTIONS_PATH.exists():
        return (
            "You are a helpful medical assistant. Provide clear, concise answers and disclaimers."
        )
    return INSTRUCTIONS_PATH.read_text(encoding="utf-8")

# -------------------------
# GraphConnector wrapper as Tools
# -------------------------
class GraphToolWrapper:
    def __init__(self, graph: GraphConnector):
        self.graph = graph

    def diseases_by_symptoms(self, symptoms: List[str]) -> str:
        """Return nicely formatted string with all matching diseases and details."""
        return self.graph.build_context_from_symptoms(symptoms)


# -------------------------
# Build the LLM + Chain
# -------------------------
def build_llm_chain(ollama_model_name: str = OLLAMA_MODEL) -> RunnableSequence:
    """Future-proof LLM chain using RunnableSequence."""
    llm = OllamaLLM(model=ollama_model_name)
    system_prompt = load_instructions()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )

    # Runnable pipeline: prompt → LLM
    return prompt | llm


# -------------------------
# Build Tools & Agent
# -------------------------
def build_agent(graph: GraphConnector) -> Any:
    wrapper = GraphToolWrapper(graph)

    # Define tools using @tool decorator for LangGraph compatibility
    @tool
    def graph_query_by_symptoms(symptoms: str) -> str:
        """Provide a list of diseases with full details for the given symptoms.
        Input can be comma-separated string of symptoms."""
        symptom_list = (
            symptoms if isinstance(symptoms, list) else [s.strip() for s in symptoms.split(",")]
        )
        return wrapper.diseases_by_symptoms(symptom_list)

    @tool
    def dummy_agent(query: str) -> str:
        """Dummy tool that returns a placeholder response."""
        return f"DUMMY_AGENT_RESULT: This is a placeholder tool. Query was: {query}"

    llm_chain = build_llm_chain()

    # Future-proof agent using LangGraph ReAct agent
    agent = create_react_agent(
        llm_chain,
        [graph_query_by_symptoms, dummy_agent]
    )
    return agent


# -------------------------
# High-level API: ask function (RAG + LLM)
# -------------------------
def ask_user_question(user_question: str, symptoms: List[str]) -> str:
    """RAG helper: query graph, then run response generation via LLM."""
    system_instructions = load_instructions()
    graph = GraphConnector()
    try:
        context_text = graph.build_context_from_symptoms(symptoms)

        chain = build_llm_chain()
        response = chain.invoke(
            {
                "input": f"""{system_instructions}

CONTEXT:
{context_text}

USER QUESTION:
{user_question}"""
            }
        )
        return response
    finally:
        graph.close()


# -------------------------
# Example Usage
# -------------------------
if __name__ == "__main__":
    graph = GraphConnector()
    agent = build_agent(graph)

    # === Direct RAG Example ===
    print("=== RAG Example ===")
    ans = ask_user_question(
        "What could be causing these symptoms and what should I do next?",
        ["fever", "cough"]
    )
    print(ans)

    # === Agent Example ===
    print("\n=== Agent Example: ask agent to use graph tool ===")
    agent_input = "Find diseases for symptoms: fever, cough. Summarize and recommend next steps."
    agent_result = agent.invoke({"messages": [("human", agent_input)]})
    print("\nAgent result:\n", agent_result)

    graph.close()
