import json
import spacy
import docx2txt
import re
from collections import Counter
from nltk.tokenize import sent_tokenize

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# File paths
transcript_path = "Spring 2025 Webinar Transcripts.docx"
knowledge_base_path = "knowledge_base.json"

# Function to clean text
def clean_text(text):
    text = text.replace("\n", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    return text

# Improved function to extract topics, speakers, and key takeaways
def generate_summary(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]

    # Predefined meaningful topics for accuracy
    predefined_topics = [
        "Institutional Review Board (IRB)", "Data Governance", "Secure My Research",
        "Key Institutional Policies", "Research Compliance Strategies",
        "IT Support for Researchers", "Research Data Librarians", "Discovering Data Resources"
    ]
    detected_topics = [topic for topic in predefined_topics if topic.lower() in text.lower()]

    # Extract and filter real speaker names (avoiding incorrect extractions)
    known_speakers = set()
    for entity in doc.ents:
        if entity.label_ == "PERSON" and len(entity.text.split()) == 2:  # Ensure full names
            known_speakers.add(entity.text)

    # Remove incorrectly detected speakers (organizations, tools, locations)
    invalid_speakers = {"Red Cap", "Gill Institute", "I.U. Bloomington"}
    filtered_speakers = list(known_speakers - invalid_speakers)

    # Extract key takeaways using meaningful contextual clues
    key_points = [sentence for sentence in sentences if any(
        keyword in sentence.lower() for keyword in ["discuss", "focus on", "important", "highlight", "explain", "compliance", "policy"]
    )][:5]  # Limit to 5 takeaways

    # Construct structured summary
    summary = {
        "main_topics": detected_topics if detected_topics else ["Research Data Management"],
        "speakers": filtered_speakers,
        "key_takeaways": key_points
    }
    return summary

# Function to extract structured Q&A pairs
def extract_qna(text):
    sentences = sent_tokenize(text)
    qna = []
    current_question = None
    current_answer = []

    for sentence in sentences:
        if sentence.strip().endswith("?"):  # Detect questions
            if current_question and current_answer:
                qna.append({"question": current_question, "answer": " ".join(current_answer)})
            current_question = sentence.strip()
            current_answer = []
        else:
            current_answer.append(sentence.strip())

    if current_question and current_answer:  # Append last Q&A pair
        qna.append({"question": current_question, "answer": " ".join(current_answer)})
    
    return qna

# Load transcript and clean text
transcript_text = docx2txt.process(transcript_path)
cleaned_text = clean_text(transcript_text)

# Generate structured summary with improved topic and speaker extraction
structured_summary = generate_summary(cleaned_text)

# Format structured JSON for webinar transcript
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

# Load existing knowledge base
try:
    with open(knowledge_base_path, "r", encoding="utf-8") as f:
        knowledge_base = json.load(f)
except FileNotFoundError:
    knowledge_base = {}

# **Replace** the existing "webinar_transcripts" section instead of appending
knowledge_base["webinar_transcripts"] = [webinar_data]

# Save the updated knowledge base
with open(knowledge_base_path, "w", encoding="utf-8") as f:
    json.dump(knowledge_base, f, indent=4, ensure_ascii=False)

print("✅ Webinar transcript successfully **updated with correct topics and speakers**!")
