import logging


class JobEmbeddingService:
    def __init__(self, model, repository):
        self.model = model
        self.repository = repository
        self.req_headers = [
            "qualifications", "basic qualifications", "requirements",
            "what you'll need", "skills", "experience"
        ]
        self.resp_headers = [
            "what you'll accomplish", "responsibilities",
            "what you'll do", "the role", "job duties"
        ]

    def safe_encode(self, text: str):
        """Encode text to vector — handles both numpy array and list returns."""
        encoded = self.model.encode(text)
        return encoded.tolist() if hasattr(encoded, "tolist") else list(encoded)

    def extract_sections(self, text):
        sections = {"requirements": "", "responsibilities": ""}
        if not text:
            return sections

        lines = text.split('\n')
        current_section = None

        for line in lines:
            clean_line = line.strip().lower()
            if not clean_line:
                continue
            if any(header in clean_line for header in self.req_headers):
                current_section = "requirements"
                continue
            elif any(header in clean_line for header in self.resp_headers):
                current_section = "responsibilities"
                continue
            if current_section:
                sections[current_section] += line + " "

        return sections

    def process_unembedded_jobs(self):
        jobs = self.repository.get_unembedded_jobs()

        if not jobs:
            print("No new jobs to process.")
            return

        for job in jobs:
            try:
                description = (job.get('description') or "").strip()
                title = (job.get('title') or "").strip()

                # Hard skip — no description means nothing to embed
                # These will be caught by the SQL delete above
                if not description:
                    print(f"⚠️  Skipping '{title}' — no description, will be cleaned up")
                    continue

                print(f"Processing: {title}...")

                sections = self.extract_sections(description)
                req_text = sections['requirements'].strip() or description
                resp_text = sections['responsibilities'].strip() or description

                updates = {
                    "title_embedding": self.safe_encode(title),
                    "requirements_embedding": self.safe_encode(req_text),
                    "qualifications_embedding": self.safe_encode(req_text),
                    "responsibilities_embedding": self.safe_encode(resp_text),
                    "description_embedding": self.safe_encode(description)
                }

                self.repository.update_job_embeddings(job['id'], updates)
                print(f"✅ Successfully embedded: {title}")

            except Exception as e:
                print(f"❌ Error processing '{job.get('title', 'unknown')}': {e}")
                continue