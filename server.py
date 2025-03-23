"""import os
import json
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

# Load environment variables
load_dotenv()

# OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load knowledge base
def load_knowledge_base():
    
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

knowledge_base = load_knowledge_base()

# Load pre-trained NLP model for semantic search
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_knowledge_base(query):
    
    if not knowledge_base:
        return "No knowledge base found."

    all_texts = []
    data_map = {}

    # Convert JSON structure into a searchable list
    for category, items in knowledge_base.items():
        for item in items:
            text = " ".join([f"{k}: {v}" for k, v in item.items()])
            all_texts.append(text)
            data_map[text] = item

    # Compute embeddings
    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(all_texts, convert_to_tensor=True)

    # Find the most relevant section using cosine similarity
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=3)
    relevant_sections = [all_texts[hit['corpus_id']] for hit in hits[0]]

    # Combine results
    return "\n\n".join(relevant_sections)[:5000] if relevant_sections else "No relevant data found."

def format_knowledge_snippet(knowledge_snippet):
    
    if not knowledge_snippet:
        return "No relevant information found."

    # Convert structured text into bullet points
    formatted_text = "Here’s what I found:\n\n"
    
    sections = knowledge_snippet.split("\n\n")
    for section in sections:
        lines = section.split("\n")
        formatted_text += "🔹 " + lines[0] + "\n"  # First line as title
        for line in lines[1:]:
            formatted_text += "   - " + line + "\n"
        formatted_text += "\n"  # Space between sections
    
    return formatted_text.strip()

def format_knowledge_snippet(knowledge_snippet):
    
    if not knowledge_snippet:
        return "I couldn't find relevant information in the knowledge base. Let me know if you’d like me to try rephrasing or searching differently!"

    formatted_text = "Here’s what I found:\n\n"

    sections = knowledge_snippet.split("\n\n")
    for section in sections:
        lines = section.split("\n")
        formatted_text += "🔹 " + lines[0] + "\n"  # First line as title
        for line in lines[1:]:
            formatted_text += "   - " + line.strip() + "\n"
        formatted_text += "\n"  # Space between sections
    
    return formatted_text.strip()


def ask_chatgpt(query):
    
    knowledge_snippet = search_knowledge_base(query)
    formatted_knowledge = format_knowledge_snippet(knowledge_snippet)

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specializing in research-related questions at Indiana University (IU). "
                        "Always **start the response with the most important or defining information first**. "
                        "Keep responses **brief, well-structured, and to the point** (no more than 3-4 sentences). "
                        "Avoid unnecessary details or reordering important facts randomly."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is structured information from the knowledge base:\n\n"
                        f"{formatted_knowledge}\n\n"
                        f"Rephrase this response, making sure that **the most crucial fact appears first**. "
                        f"Keep it **concise and logically structured** while maintaining clarity. "
                        f"Do not add any new information beyond what is provided. "
                        f"Question: {query}"
                    )
                }
            ]
        )
        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"❌ OpenAI API Error: {str(e)}"




@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
  
    data = request.json
    user_query = data.get("question", "")

    if not user_query:
        return jsonify({"response": "Please enter a question."})

    response_text = ask_chatgpt(user_query)
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=True)
"""

import os
import json
import openai
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from flask import session
from flask_session import Session
import re

# Load environment variables
load_dotenv()

# OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")



# Initialize Flask app with session support
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = "your_secret_key"  # Change this to a secure random key

# Load knowledge base
def load_knowledge_base():
    """Load the structured knowledge base from a JSON file."""
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

knowledge_base = load_knowledge_base()

# Load pre-trained NLP model for semantic search
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_knowledge_base(query):
    """Find the most relevant sections of the knowledge base using semantic search and return source."""
    if not knowledge_base:
        return "No knowledge base found.", "Unknown Source"

    all_texts = []
    data_map = {}

    # Convert JSON structure into a searchable list with category tracking
    for category, items in knowledge_base.items():
        for item in items:
            text = " ".join([f"{k}: {v}" for k, v in item.items()])
            all_texts.append(text)
            data_map[text] = category  # Store category source

    # Compute embeddings
    query_embedding = model.encode(query, convert_to_tensor=True)
    corpus_embeddings = model.encode(all_texts, convert_to_tensor=True)

    # Find the most relevant section using cosine similarity
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=1)

    if hits and hits[0]:
        best_match_text = all_texts[hits[0][0]['corpus_id']]
        source_category = data_map.get(best_match_text, "Unknown Source")
        return best_match_text, source_category

    return "No relevant data found.", "Unknown Source"

"""def ask_chatgpt(query):
    
    # Retrieve knowledge snippet and its source
    knowledge_snippet, source_category = search_knowledge_base(query)

    # Convert source category into a readable format (e.g., "news_posts" → "News Posts")
    formatted_source_category = source_category.replace("_", " ").title()

    # Retrieve or initialize chat history
    if "chat_history" not in session:
        session["chat_history"] = [
            {"role": "system", "content": (
                "You are an AI assistant for Indiana University Research Data Commons (IURDC) members. "
                "Your role is to answer research questions, draft emails, and create research proposals using the knowledge base. "
                "Ensure responses are clear, relevant, and aligned with the user's request."
            )}
        ]

    # Retrieve or set chatbot mode
    if "chat_mode" not in session:
        session["chat_mode"] = "general"  # Default mode

    # Check for mode change command and prevent repeated confirmations
    if "switch to email mode" in query.lower():
        if session["chat_mode"] != "email":
            session["chat_mode"] = "email"
            return "✅ You are now in **Email Mode**. I will only draft emails."
        else:
            return "You are already in **Email Mode**."
    
    if "switch to proposal mode" in query.lower():
        if session["chat_mode"] != "proposal":
            session["chat_mode"] = "proposal"
            return "✅ You are now in **Proposal Mode**. I will only generate structured research proposals."
        else:
            return "You are already in **Proposal Mode**."
    
    if "switch to general mode" in query.lower():
        if session["chat_mode"] != "general":
            session["chat_mode"] = "general"
            return "✅ You are now in **General Mode**. You can ask me anything."
        else:
            return "You are already in **General Mode**."

    # Define mode-specific behavior
    if session["chat_mode"] == "email":
        task_instruction = (
            "You are in **Email Mode**. Draft a **professional email** with:\n"
            "- A subject line\n"
            "- A greeting\n"
            "- A structured body with clear information\n"
            "- A closing and signature placeholder.\n"
            "Do NOT answer general questions in this mode."
        )
    elif session["chat_mode"] == "proposal":
        task_instruction = (
            "You are in **Proposal Mode**. Create a well-structured research proposal with:\n"
            "- A title\n"
            "- An objective section\n"
            "- A research approach/methodology section\n"
            "- Expected outcomes and impact.\n"
            "Do NOT answer general questions in this mode."
        )
    else:
        task_instruction = (
            "You are in **General Mode**. Analyze the user's question carefully, even if it has grammatical mistakes. "
            "Provide a useful and structured response using the knowledge base. If information is missing, use logical reasoning "
            "to generate a helpful response instead of providing unnecessary details."
        )

    session["chat_history"].append({"role": "user", "content": query})

    # Keep only the last 10 interactions to prevent excessive token usage
    session["chat_history"] = session["chat_history"][-10:]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session["chat_history"] + [
                {"role": "system", "content": f"Relevant information extracted from the knowledge base:\n{knowledge_snippet}"},
                {"role": "system", "content": task_instruction}
            ],
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # Append bot response to chat history
        session["chat_history"].append({"role": "assistant", "content": bot_response})

        # Append the formatted source at the end
        final_response = f"{bot_response}\n\n**Source:** {formatted_source_category}"

        return final_response

    except openai.OpenAIError as e:
        return f"❌ OpenAI API Error: {str(e)}"
"""

def format_response_text(text):
    """Formats chatbot response text for better readability with paragraphs and bullet points."""
    
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

    # Add proper paragraph spacing (replace single line breaks with double for clear separation)
    text = text.replace("\n", "\n\n")

    # Convert lists (- or •) into properly spaced bullet points
    text = re.sub(r"\n- ", r"\n• ", text)
    text = re.sub(r"\n\* ", r"\n• ", text)

    return text.strip()


def ask_chatgpt(query):
    """Query OpenAI's GPT-3.5 model based on the current mode (General, Email, or Proposal) and allow edits to previous responses."""
    
    # Retrieve knowledge snippet and its source
    knowledge_snippet, source_category = search_knowledge_base(query)

    # Convert source category into a readable format (e.g., "news_posts" → "News Posts")
    formatted_source_category = source_category.replace("_", " ").title()

    # Retrieve or initialize chat history
    if "chat_history" not in session:
        session["chat_history"] = [
            {"role": "system", "content": (
                "You are an advanced AI assistant for Indiana University Research Data Commons (IURDC) members. "
                "Your task is to generate insightful, structured, and highly relevant responses using the knowledge base. "
                "DO NOT copy directly from the knowledge base. Instead, analyze, summarize, and structure your responses clearly."
            )}
        ]

    # Retrieve or set chatbot mode
    if "chat_mode" not in session:
        session["chat_mode"] = "general"  # Default mode

    # **Allow Checking Mode**
    if "what mode am i in" in query.lower():
        current_mode = session["chat_mode"].capitalize()
        return f"ℹ️ You are currently in <strong>{current_mode} Mode</strong>. Here’s what you can do:\n\n" \
               f"• **General Mode**: Ask anything related to IURDC.\n" \
               f"• **Email Mode**: Request a professional email draft.\n" \
               f"• **Proposal Mode**: Ask for a structured research proposal."

    # **ALLOW EDITING PREVIOUS RESPONSE**
    if "edit" in query.lower() or "add" in query.lower() or "modify" in query.lower():
        if "last_response" in session:
            previous_response = session["last_response"]
            task_instruction = (
                f"You are in <strong>{session['chat_mode'].capitalize()} Mode</strong>. "
                f"The user wants to **edit or add** something to their previous response. "
                f"Here is what they originally got:\n\n{previous_response}\n\n"
                f"Modify this response according to their latest request, ensuring that it is clear, concise, and follows the correct structure."
            )
        else:
            return "⚠️ No previous response found to edit. Please ask a new request."
    
    # **STRICTLY ENFORCE MODE SWITCHING ONLY WHEN REQUESTED**
    if "switch to email mode" in query.lower():
        if session["chat_mode"] != "email":
            session["chat_mode"] = "email"
            return "✅ You are now in <strong>Email Mode</strong>. I will only draft emails."
        return "You are already in <strong>Email Mode</strong>."
    
    if "switch to proposal mode" in query.lower():
        if session["chat_mode"] != "proposal":
            session["chat_mode"] = "proposal"
            return "✅ You are now in <strong>Proposal Mode</strong>. I will only generate structured research proposals."
        return "You are already in <strong>Proposal Mode</strong>."
    
    if "switch to general mode" in query.lower():
        if session["chat_mode"] != "general":
            session["chat_mode"] = "general"
            return "✅ You are now in <strong>General Mode</strong>. You can ask me anything."
        return "You are already in <strong>General Mode</strong>."

    # **STRICT MODE BEHAVIOR ENFORCEMENT**
    if session["chat_mode"] == "email":
        if "email" not in query.lower():
            return "⚠️ You are in <strong>Email Mode</strong>. Please ask me to draft an email. If you need general answers, switch to <strong>General Mode</strong>."

        task_instruction = (
            "Draft a <strong>highly professional email</strong> based on the knowledge base. "
            "Ensure that the email is clear, concise, and structured properly with:\n\n"
            "• A subject line\n"
            "• A greeting\n"
            "• A structured body summarizing key points\n"
            "• A closing and signature placeholder.\n\n"
            "Use knowledge from the database, but DO NOT copy directly—structure it smartly."
        )
    
    elif session["chat_mode"] == "proposal":
        if "proposal" not in query.lower():
            return "⚠️ You are in <strong>Proposal Mode</strong>. Please ask me to create a research proposal. If you need general answers, switch to <strong>General Mode</strong>."

        task_instruction = (
            "Write a well-structured <strong>research proposal</strong> using information from the knowledge base. "
            "The proposal should explain WHY funding or support is required based on what is already available. "
            "Ensure it includes:\n\n"
            "• A strong title\n"
            "• A clear objective outlining WHY additional funding or resources are needed\n"
            "• A research approach that explains HOW the funding/resources will be used\n"
            "• The expected outcomes and impact\n\n"
            "DO NOT copy knowledge base text—process it smartly."
        )
    
    else:
        task_instruction = (
            "Analyze the user's question, even if it has grammatical mistakes, and provide a clear and structured answer "
            "using the knowledge base. Summarize the information instead of copying it directly. "
            "Make sure your response is insightful and well-organized."
        )

    session["chat_history"].append({"role": "user", "content": query})

    # Keep only the last 10 interactions to prevent excessive token usage
    session["chat_history"] = session["chat_history"][-10:]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session["chat_history"] + [
                {"role": "system", "content": f"Relevant knowledge extracted (analyze & summarize, DO NOT copy):\n{knowledge_snippet}"},
                {"role": "system", "content": task_instruction}
            ],
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # Store last response for editing
        session["last_response"] = bot_response

        # Format response for readability
        formatted_response = format_response_text(bot_response)

        # Append the formatted source at the end
        final_response = f"{formatted_response}\n\n<strong>Source:</strong> {formatted_source_category}"

        return final_response

    except openai.OpenAIError as e:
        return f"❌ <strong>OpenAI API Error:</strong> {str(e)}"

@app.route("/")
def index():
    """Serve the chatbot HTML page."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests from the frontend."""
    data = request.json
    user_query = data.get("question", "")

    if not user_query:
        return jsonify({"response": "Please enter a question."})

    response_text = ask_chatgpt(user_query)
    return jsonify({"response": response_text})

@app.route("/reset", methods=["POST"])
def reset_chat():
    """Reset the chat history."""
    session.pop("chat_history", None)
    return jsonify({"response": "Chat history reset successfully."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

