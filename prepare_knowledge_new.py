"""from pathlib import Path
import pandas as pd
import json
import hashlib
from datetime import datetime
import re
from docx import Document
from concurrent.futures import ThreadPoolExecutor, as_completed

# Use the current working directory
base_path = Path(".")

# Configuration for Excel files
file_info = {
    "Copy of News Posts.xlsx": ["News Posts"],
    "Copy of Data Catalog.xlsx": ["Data Catalog"],
    "Copy of Governance Groups.xlsx": ["Governance Groups"],
    "Copy of Frequently Asked Questions.xlsx": ["FAQ Questions"],
    "Copy of Working Groups.xlsx": ["Working Groups"],
    "Copy of People Database.xlsx": ["People"],
    "Copy of Resource Catalog.xlsx": ["Resource Catalog"]
}

# Function to safely get cell content
def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

# Function to generate a unique ID for an entry
def generate_entry_id(entry):
    return hashlib.md5(json.dumps(entry, sort_keys=True).encode()).hexdigest()

# Function to clean and structure data consistently
def process_excel_to_structured_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.dropna(how='all').dropna(axis=1, how='all')

    entries = []
    for _, row in df.iterrows():
        if all(pd.isna(row[col]) for col in df.columns[:3]):
            continue

        entry_data = {col: safe_str(row[col]) for col in df.columns if not pd.isna(row[col])}
        entry = {
            "_source": sheet_name,
            "_file": file_path.name,
            "_id": generate_entry_id(entry_data),
            "_last_updated": datetime.now().isoformat(),
            "data": entry_data
        }
        entries.append(entry)
    return entries

# Function to process a single file
def process_file(file, sheets):
    file_path = base_path / file
    if not file_path.exists():
        return []

    entries = []
    for sheet in sheets:
        sheet_entries = process_excel_to_structured_data(file_path, sheet)
        if sheet_entries:
            entries.extend(sheet_entries)
    return entries

# Function to process the webinar transcript
def process_webinar_transcript():
    doc_path = base_path / "Spring 2025 Webinar Transcripts.docx"
    document = Document(doc_path)

    sessions = []
    current_session = None
    current_speakers = set()

    # Regex pattern to match speaker lines (e.g., John: ... or Dr. Smith: ...)
    speaker_pattern = re.compile(r"^([A-Z][A-Za-z .'-]+):\s*(.+)")

    # Combine all paragraphs into a single text block
    full_text = "\n".join([para.text.strip() for para in document.paragraphs if para.text.strip()])

    # Split the text into paragraphs based on double newlines or periods
    paragraphs = re.split(r"\.\s+|\n{2,}", full_text)

    # Process each paragraph
    for para in paragraphs:
        text = para.strip()

        # Skip empty lines
        if not text:
            continue

        # Debug: Print the current paragraph text
        print(f"Processing paragraph: {text}")

        # Identify session titles (e.g., "Your Data & the IRB")
        if re.match(r"^[A-Z][A-Za-z &]+$", text):
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
            print(f"New session started: {text}")

        # Identify and extract speaker and text
        elif match := speaker_pattern.match(text):
            speaker = match.group(1).strip()
            speech = match.group(2).strip()

            current_session["transcript"].append({
                "speaker": speaker,
                "text": speech
            })
            current_speakers.add(speaker)
            print(f"Added dialogue: {speaker}: {speech}")

        # Append to last speaker’s text if it's a continuation line
        elif current_session and current_session["transcript"]:
            current_session["transcript"][-1]["text"] += " " + text.strip()
            print(f"Continued dialogue: {text}")

    # Save the final session
    if current_session:
        current_session["speakers"] = list(current_speakers)
        sessions.append(current_session)

    return sessions

# Main function to process all files and transcript
def main():
    knowledge_entries = []

    # Process Excel files in parallel
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, file, sheets): file for file, sheets in file_info.items()}
        for future in as_completed(futures):
            entries = future.result()
            if entries:
                knowledge_entries.extend(entries)

    # Process webinar transcript
    webinar_sessions = process_webinar_transcript()

    # Create structured knowledge base with categories
    knowledge_base = {}
    for entry in knowledge_entries:
        category = entry["_source"]
        if category not in knowledge_base:
            knowledge_base[category] = []
        knowledge_base[category].append(entry)

    # Add webinar transcript to the knowledge base
    knowledge_base["Webinar_Transcripts"] = webinar_sessions

    # Save to combined_knowledge_base.json (replacing existing content)
    output_path = base_path / "combined_knowledge_base.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

    print(f"✅ Knowledge base saved to {output_path}")

if __name__ == "__main__":
    main()"""

from pathlib import Path
import pandas as pd
import json
import hashlib
from datetime import datetime
import re
import docx2txt
import spacy
from collections import Counter
from nltk.tokenize import sent_tokenize
from concurrent.futures import ThreadPoolExecutor, as_completed

# Use the current working directory
base_path = Path(".")

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Configuration for Excel files
file_info = {
    "Copy of News Posts.xlsx": ["News Posts"],
    "Copy of Data Catalog.xlsx": ["Data Catalog"],
    "Copy of Governance Groups.xlsx": ["Governance Groups"],
    "Copy of Frequently Asked Questions.xlsx": ["FAQ Questions"],
    "Copy of Working Groups.xlsx": ["Working Groups"],
    "Copy of People Database.xlsx": ["People"],
    "Copy of Resource Catalog.xlsx": ["Resource Catalog"]
}

# Function to safely get cell content
def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

# Function to generate a unique ID for an entry
def generate_entry_id(entry):
    return hashlib.md5(json.dumps(entry, sort_keys=True).encode()).hexdigest()

# Function to clean and structure data consistently
def process_excel_to_structured_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.dropna(how='all').dropna(axis=1, how='all')

    entries = []
    for _, row in df.iterrows():
        if all(pd.isna(row[col]) for col in df.columns[:3]):
            continue

        entry_data = {col: safe_str(row[col]) for col in df.columns if not pd.isna(row[col])}
        entry = {
            "_source": sheet_name,
            "_file": file_path.name,
            "_id": generate_entry_id(entry_data),
            "_last_updated": datetime.now().isoformat(),
            "data": entry_data
        }
        entries.append(entry)
    return entries

# Function to process a single Excel file
def process_file(file, sheets):
    file_path = base_path / file
    if not file_path.exists():
        return []

    entries = []
    for sheet in sheets:
        sheet_entries = process_excel_to_structured_data(file_path, sheet)
        if sheet_entries:
            entries.extend(sheet_entries)
    return entries

# Clean text for NLP processing
def clean_text(text):
    text = text.replace("\n", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    return text

# Extract structured summary from transcript
def generate_summary(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    predefined_topics = [
        "Institutional Review Board (IRB)", "Data Governance", "Secure My Research",
        "Key Institutional Policies", "Research Compliance Strategies",
        "IT Support for Researchers", "Research Data Librarians", "Discovering Data Resources"
    ]
    detected_topics = [topic for topic in predefined_topics if topic.lower() in text.lower()]

    known_speakers = set()
    for entity in doc.ents:
        if entity.label_ == "PERSON" and len(entity.text.split()) == 2:
            known_speakers.add(entity.text)

    invalid_speakers = {"Red Cap", "Gill Institute", "I.U. Bloomington"}
    filtered_speakers = list(known_speakers - invalid_speakers)

    key_points = [sentence for sentence in sentences if any(
        keyword in sentence.lower() for keyword in ["discuss", "focus on", "important", "highlight", "explain", "compliance", "policy"]
    )][:5]

    summary = {
        "main_topics": detected_topics if detected_topics else ["Research Data Management"],
        "speakers": filtered_speakers,
        "key_takeaways": key_points
    }
    return summary

# Extract Q&A pairs from transcript
def extract_qna(text):
    sentences = sent_tokenize(text)
    qna = []
    current_question = None
    current_answer = []

    for sentence in sentences:
        if sentence.strip().endswith("?"):
            if current_question and current_answer:
                qna.append({"question": current_question, "answer": " ".join(current_answer)})
            current_question = sentence.strip()
            current_answer = []
        else:
            current_answer.append(sentence.strip())

    if current_question and current_answer:
        qna.append({"question": current_question, "answer": " ".join(current_answer)})

    return qna

# Function to process the webinar transcript using NLP logic
def process_webinar_transcript():
    transcript_path = base_path / "Spring 2025 Webinar Transcripts.docx"
    transcript_text = docx2txt.process(str(transcript_path))
    cleaned_text = clean_text(transcript_text)
    structured_summary = generate_summary(cleaned_text)

    webinar_data = {
        "topic": "Research Data Webinar",
        "date": "Spring 2025",
        "summary": {
            "overview": "This webinar covered key topics on research data governance, IRB processes, compliance strategies, and IT support services.",
            "main_topics": structured_summary["main_topics"],
            "speakers": structured_summary["speakers"],
            "key_takeaways": structured_summary["key_takeaways"]
        },
        "qna": extract_qna(cleaned_text)
    }

    return [webinar_data]

# Main function to process all files and transcript
def main():
    knowledge_entries = []

    # Process Excel files in parallel
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, file, sheets): file for file, sheets in file_info.items()}
        for future in as_completed(futures):
            entries = future.result()
            if entries:
                knowledge_entries.extend(entries)

    # Process webinar transcript with NLP logic
    webinar_data = process_webinar_transcript()

    # Create structured knowledge base with categories
    knowledge_base = {}
    for entry in knowledge_entries:
        category = entry["_source"]
        if category not in knowledge_base:
            knowledge_base[category] = []
        knowledge_base[category].append(entry)

    # Replace webinar section with new content
    knowledge_base["Webinar_Transcripts"] = webinar_data

    # Save to combined_knowledge_base.json (replacing existing content)
    output_path = base_path / "combined_knowledge_base.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

    print(f"✅ Knowledge base saved to {output_path}")

if __name__ == "__main__":
    main()
