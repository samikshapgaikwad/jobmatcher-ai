import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

_groq_client = None


def get_groq_client(temperature: float = 0.2) -> ChatGroq:
    """
    Lazy singleton Groq client.
    Reused across nodes to avoid re-initializing on every call.
    temperature=0.2 for structured tasks (scoring, gap analysis)
    temperature=0.7 for generative tasks (cover letters)
    """
    global _groq_client

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing GROQ_API_KEY. Add it to your .env file.\n"
            "Get a free key at: https://console.groq.com"
        )

    # Return cached client if temperature matches, else create new
    if _groq_client is None or _groq_client.temperature != temperature:
        _groq_client = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            api_key=api_key,
            max_tokens=2048
        )

    return _groq_client


def get_creative_client() -> ChatGroq:
    """Preset for generative tasks — cover letters, summaries."""
    return get_groq_client(temperature=0.7)


def get_analytical_client() -> ChatGroq:
    """Preset for structured tasks — scoring, gap analysis, JSON output."""
    return get_groq_client(temperature=0.2)