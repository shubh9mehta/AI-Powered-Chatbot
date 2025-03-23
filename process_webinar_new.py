import json
import re
from docx import Document

# Load the .docx file
doc_path = "Spring 2025 Webinar Transcripts.docx"
document = Document(doc_path)

# Initialize variables
sessions = []
current_session = None
current_speakers = set()

# Regex pattern to match speaker lines (e.g., John: ... or Dr. Smith: ...)
speaker_pattern = re.compile(r"^([A-Z][A-Za-z .'-]+):\s*(.+)")

# Process each paragraph
for para in document.paragraphs:
    text = para.text.strip()

    # Skip empty lines
    if not text:
        continue

    # Identify session titles (all caps with "SESSION" or similar keyword)
    if re.match(r"^[A-Z0-9 :\-]{5,}$", text) and "SESSION" in text:
        # Save previous session if it exists
        if current_session:
            current_session["speakers"] = list(current_speakers)
            sessions.append(current_session)

        # Start a new session
        current_session = {
            "session_title": text.strip(),
            "speakers": [],
            "transcript": []
        }
        current_speakers = set()

    # Identify and extract speaker and text
    elif match := speaker_pattern.match(text):
        speaker = match.group(1).strip()
        speech = match.group(2).strip()

        current_session["transcript"].append({
            "speaker": speaker,
            "text": speech
        })
        current_speakers.add(speaker)

    # Append to last speaker’s text if it's a continuation line
    elif current_session and current_session["transcript"]:
        current_session["transcript"][-1]["text"] += " " + text.strip()

# Save the final session
if current_session:
    current_session["speakers"] = list(current_speakers)
    sessions.append(current_session)

# Save to JSON
output_file = "structured_webinar_transcript.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sessions, f, indent=2, ensure_ascii=False)

print(f"✅ Transcript converted and saved to: {output_file}")
