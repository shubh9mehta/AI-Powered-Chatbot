"""import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_knowledge_base():
    
    try:
        with open("knowledge_base.txt", "r") as f:
            return f.readlines()  # Read file as a list of lines for searching
    except FileNotFoundError:
        return ["Knowledge base not found. Please ensure 'knowledge_base.txt' exists."]

def search_knowledge_base(query):
    
    knowledge = load_knowledge_base()

    # Search for matching lines in the knowledge base
    relevant_sections = [line for line in knowledge if query.lower() in line.lower()]
    
    # Combine results and limit to 5000 characters (to stay within GPT-3.5 constraints)
    return "\n".join(relevant_sections)[:5000] if relevant_sections else "No relevant data found."

def ask_chatgpt(query):
   
    knowledge_snippet = search_knowledge_base(query)  # Retrieve only relevant sections

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Optimized for better rate limits
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specializing in answering research-related questions at Indiana University (IU). "
                        "Use the provided knowledge base to generate clear, well-structured, and professional responses. "
                        "Your answers should be informative, concise, and free from raw data dumps, SQL queries, or unnecessary technical references. "
                        "If information is missing, provide a helpful and logical answer based on what is available."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Use the following knowledge base to answer the user's question in natural language:\n"
                        f"{knowledge_snippet}\n\n"
                        f"Question: {query}\n\n"
                        f"Provide a detailed, easy-to-understand response. Avoid returning raw data, tables, SQL queries, or technical references unless explicitly requested."
                    )
                }
            ]
        )
        return response.choices[0].message.content

    except openai.error.RateLimitError:
        return "❌ Rate limit exceeded. Try again later."
    except openai.error.AuthenticationError:
        return "❌ Incorrect API Key! Please check your OpenAI API key."
    except openai.error.OpenAIError as e:
        return f"❌ OpenAI API Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

if __name__ == "__main__":
    print("IU Research Chatbot (Type 'exit' to quit)")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        response = ask_chatgpt(user_input)
        print("Chatbot:", response)
"""

import openai
import os
import json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load knowledge base from JSON
def load_knowledge_base():
    """Load the structured knowledge base from a JSON file."""
    try:
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Load pre-trained NLP model for semantic search
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_knowledge_base(query):
    """Find the most relevant sections of the knowledge base using semantic search."""
    knowledge = load_knowledge_base()
    if not knowledge:
        return "No knowledge base found."

    all_texts = []
    data_map = {}

    # Convert JSON structure into a searchable list
    for category, items in knowledge.items():
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

def ask_chatgpt(query):
    """Query OpenAI's GPT-3.5 model with relevant knowledge base data."""
    knowledge_snippet = search_knowledge_base(query)  # Retrieve only relevant sections

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specializing in answering research-related questions at Indiana University (IU). "
                        "Use the provided knowledge base to generate clear, well-structured, and professional responses. "
                        "Your answers should be informative, concise, and free from raw data dumps, SQL queries, or unnecessary technical references. "
                        "If information is missing, provide a helpful and logical answer based on what is available."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Use the following knowledge base to answer the user's question in natural language:\n"
                        f"{knowledge_snippet}\n\n"
                        f"Question: {query}\n\n"
                        f"Provide a detailed, easy-to-understand response."
                    )
                }
            ]
        )
        return response.choices[0].message.content

    except openai.RateLimitError as e:
        print(f"❌ Rate limit exceeded: {str(e)}")
        return "❌ Rate limit exceeded. Please check your OpenAI usage or try again later."
    except openai.AuthenticationError:
        return "❌ Incorrect API Key! Please check your OpenAI API key."
    except openai.InvalidRequestError:
        return "❌ Invalid request. Please rephrase your query."
    except openai.OpenAIError as e:
        return f"❌ OpenAI API Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

if __name__ == "__main__":
    print("IU Research Chatbot (Type 'exit' to quit)")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        response = ask_chatgpt(user_input)
        print("Chatbot:", response)
