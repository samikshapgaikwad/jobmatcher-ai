import re
import spacy
from resume_pipeline.text_extraction import extract_text

# Load spaCy model once at module level
# Run first: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------------------------
# Header keyword map — lowercase, order matters (first match wins)
# ---------------------------------------------------------------------------
HEADER_MAP = {
    "skills": [
        "technical skill", "programming language", "framework",
        "technologies", "tools", "tech stack", "core competencies"
    ],
    "experience": [
        "experience", "work experience", "internship",
        "projects", "work history", "professional experience"
    ],
    "education": [
        "education", "academic", "qualification", "degree"
    ],
    "achievements": [
        "achievement", "accomplishment", "award",
        "honor", "honour", "certification"
    ],
    "extracurricular": [
        "extra-curricular", "extracurricular", "volunteering",
        "scholarship", "leadership", "activity", "club"
    ]
}


def _extract_email(text: str) -> str:
    """Regex-based email extraction — more reliable than pyresparser."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> str:
    """Extracts Indian and international phone numbers."""
    match = re.search(
        r"(\+91[\s\-]?)?[6-9]\d{9}|(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}",
        text
    )
    return match.group(0).strip() if match else None


def _extract_name(text: str) -> str:
    """
    Uses spaCy NER to find PERSON entities.
    Falls back to the first non-empty line of the resume
    (which is almost always the candidate's name).
    """
    # Try spaCy NER first
    doc = nlp(text[:500])  # Only scan the top of the resume
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    # Fallback: first non-empty line
    for line in text.split("\n"):
        clean = line.strip()
        if clean and len(clean.split()) <= 5:  # Names are short
            return clean

    return None


def _parse_sections(text: str) -> dict:
    """
    Splits resume text into sections using keyword-based header detection.
    Handles uppercase, mixed case, and noisy headers.
    """
    sections = {k: [] for k in HEADER_MAP.keys()}
    lines = text.split("\n")
    current_section = None

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        clean_lower = clean.lower()
        found_header = False

        # Only treat short lines as potential headers (avoids mid-sentence matches)
        if len(clean) < 40:
            for section_key, keywords in HEADER_MAP.items():
                if any(k in clean_lower for k in keywords):
                    current_section = section_key
                    found_header = True
                    break

        if found_header:
            continue

        if current_section:
            sections[current_section].append(clean)

    # Join lines cleanly with single space
    return {k: " ".join(v) for k, v in sections.items()}


def parse_resume_metadata(file_path: str) -> dict:
    """
    Main function. Parses a resume PDF or DOCX into structured metadata.
    Uses spaCy + regex for extraction — no pyresparser dependency.
    """
    raw_text = extract_text(file_path)

    if not raw_text or not raw_text.strip():
        raise ValueError(f"Could not extract text from resume: {file_path}")

    sections = _parse_sections(raw_text)

    return {
        "name": _extract_name(raw_text),
        "email": _extract_email(raw_text),
        "phone": _extract_phone(raw_text),
        "raw_text": raw_text,
        "skills_text": sections["skills"],
        "experience_text": sections["experience"],
        "education_text": sections["education"],
        "achievements_text": sections["achievements"],
        "extracurricular_text": sections["extracurricular"]
    }