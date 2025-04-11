import os
import json
import re
import openai
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from sentence_transformers import SentenceTransformer, util

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "your_secret_key"
Session(app)

# Load knowledge base
def load_knowledge_base(filepath="combined_knowledge_base.json"):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

knowledge_base = load_knowledge_base()

# Load semantic model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Semantic search over knowledge base
def search_knowledge_base(query, top_k=3):
    if not knowledge_base:
        return [("No knowledge base found.", "Unknown Source")]

    all_texts = []
    source_map = {}

    for category, items in knowledge_base.items():
        for item in items:
            text = json.dumps(item, ensure_ascii=False)
            all_texts.append(text)
            source_map[text] = category

    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(all_texts, convert_to_tensor=True)

    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)

    results = []
    for hit in hits[0]:
        matched = all_texts[hit["corpus_id"]]
        category = source_map.get(matched, "Unknown Source")
        results.append((matched, category))

    return results

# Clean and format chatbot response
def format_response_text(text):
    text = re.sub(r"\\1", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("\n\n", "<br><br>")
    text = text.replace("\n", "<br>")
    text = re.sub(r"<br>[-\*]\s*", r"<br>• ", text)
    text = re.sub(r"^\s*[-\*]\s*", "• ", text)
    return text.strip()

# Extract emails and links from sources
def extract_contacts_from_sources(results):
    emails = set()
    urls = set()

    for text, _ in results:
        emails.update(re.findall(r"[\w\.-]+@[\w\.-]+", text))
        urls.update(re.findall(r"https?://\S+", text))

    return list(emails), list(urls)

# Save each chat interaction to logs
def log_chat_history(user_query, bot_response):
    os.makedirs("logs", exist_ok=True)

    if "log_filename" not in session:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        session["log_filename"] = f"logs/chat_session_{timestamp}.json"
        session["log_data"] = []

    session["log_data"].append({
        "query": user_query,
        "response": bot_response,
        "timestamp": datetime.now().isoformat()
    })

    with open(session["log_filename"], "w", encoding="utf-8") as f:
        json.dump(session["log_data"], f, indent=2, ensure_ascii=False)

# Core function to generate answer from ChatGPT
def ask_chatgpt(query):
    results = search_knowledge_base(query)
    context_text = "\n---\n".join([f"From {cat}:\n{txt}" for txt, cat in results])
    source_summary = ", ".join(set(cat for _, cat in results))

    if "chat_history" not in session:
        session["chat_history"] = [{
            "role": "system",
            "content": (
                "You are an intelligent assistant for Indiana University Research Data Commons (IURDC). "
                "Answer using summarized, factual information based on the references. Avoid copying raw data."
            )
        }]

    if "chat_mode" not in session:
        session["chat_mode"] = "general"

    if "what mode am i in" in query.lower():
        return f"You are in <strong>{session['chat_mode'].capitalize()} Mode</strong>."

    instructions = {
        "general": (
            "Answer the question clearly using the knowledge base. Use logic and do not copy directly."
        ),
        "email": (
            "Draft a professional email using the sources. Include: subject, greeting, body, and closing."
        ),
        "proposal": (
            "Generate a structured research proposal with title, objectives, method, and outcomes."
        )
    }
    task_instruction = instructions.get(session["chat_mode"], instructions["general"])

    session["chat_history"].append({"role": "user", "content": query})
    session["chat_history"] = session["chat_history"][-10:]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=session["chat_history"] + [
                {"role": "system", "content": f"Relevant sources:\n{context_text}"},
                {"role": "system", "content": task_instruction}
            ],
        )
        reply = response.choices[0].message.content.strip()
        session["chat_history"].append({"role": "assistant", "content": reply})
        session["last_response"] = reply

        formatted = format_response_text(reply)

        # Extract emails and URLs from sources
        emails, urls = extract_contacts_from_sources(results)
        extras = ""
        if emails or urls:
            extras += "<br><br><strong>Useful Contacts:</strong>"
            if emails:
                extras += "<br>Email(s): " + ", ".join(f'<a href="mailto:{email}">{email}</a>' for email in emails)
            if urls:
                extras += "<br>Website(s): " + ", ".join(f'<a href="{url}" target="_blank">{url}</a>' for url in urls)

        final_response = f"{formatted}<br><br><strong>Sources:</strong> {source_summary}{extras}"
        log_chat_history(query, final_response)

        return final_response

    except openai.OpenAIError as e:
        return f"\u274c <strong>OpenAI API Error:</strong> {str(e)}"

# Flask routes
@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"response": "Please enter a question."})
    return jsonify({"response": ask_chatgpt(user_input)})

@app.route("/reset", methods=["POST"])
def reset_chat():
    session.pop("chat_history", None)
    return jsonify({"response": "Chat history reset successfully."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
