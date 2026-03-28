import re
from typing import List

# ---------------------------------------------------------------------------
# Comprehensive tech keyword set — 2025/2026 relevant
# All lowercase for matching
# ---------------------------------------------------------------------------
TECH_KEYWORDS = {
    # Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust",
    "kotlin", "swift", "r", "scala", "php", "ruby", "dart",

    # Frontend
    "react", "react.js", "angular", "vue", "vue.js", "next.js", "html", "css",
    "tailwind", "bootstrap", "flutter",

    # Backend
    "node.js", "fastapi", "django", "flask", "spring boot", "express",
    "graphql", "rest api",

    # Databases
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "supabase",
    "firebase", "elasticsearch", "pinecone", "weaviate",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "github actions", "jenkins", "linux",

    # AI / ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "huggingface", "langchain",
    "llamaindex", "openai", "groq", "llm", "rag", "vector database",
    "sentence transformers", "spacy",

    # Data
    "pandas", "numpy", "spark", "kafka", "airflow", "tableau", "power bi",

    # Tools
    "git", "github", "jira", "postman", "figma"
}

# Multi-word phrases need special handling — check as substrings
MULTI_WORD_SKILLS = {s for s in TECH_KEYWORDS if " " in s}
SINGLE_WORD_SKILLS = TECH_KEYWORDS - MULTI_WORD_SKILLS


def extract_skills_text(text: str) -> str:
    """
    Extracts tech skills from a text string.
    Uses regex word-boundary matching for single-word skills
    and substring matching for multi-word phrases.

    Returns a comma-separated sorted string of found skills.
    """
    if not text or not text.strip():
        return ""

    lower_text = text.lower()
    found_skills = set()

    # Single-word skills: use word boundaries to avoid partial matches
    # e.g. "sql" should not match inside "nosql"
    for skill in SINGLE_WORD_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, lower_text):
            found_skills.add(skill)

    # Multi-word skills: substring match is fine
    for phrase in MULTI_WORD_SKILLS:
        if phrase in lower_text:
            found_skills.add(phrase)

    # Normalize to title case for display
    normalized = {s.title() for s in found_skills}

    return ", ".join(sorted(normalized))


def get_skills_list(text: str) -> List[str]:
    """
    Same as extract_skills_text but returns a list instead of a string.
    Useful for the frontend or for passing to the LLM.
    """
    result = extract_skills_text(text)
    return [s.strip() for s in result.split(",")] if result else []