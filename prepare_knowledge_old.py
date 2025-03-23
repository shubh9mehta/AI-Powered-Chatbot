"""import pandas as pd

# File paths for all Excel files
file_paths = {
    "news_posts": "Copy of News Posts.xlsx",
    "data_catalog": "Copy of Data Catalog.xlsx",
    "governance_groups": "Copy of Governance Groups.xlsx",
    "faq": "Copy of Frequently Asked Questions.xlsx",
    "working_groups": "Copy of Working Groups.xlsx",
    "people_database": "Copy of People Database.xlsx",
    "resource_catalog": "Copy of Resource Catalog.xlsx",
}

def format_dataframe_as_text(df, name):
    
    text = f"\n=== {name.upper().replace('_', ' ')} ===\n\n"
    
    for _, row in df.iterrows():
        row_text = "\n".join([f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])])
        text += row_text + "\n------------------------\n"
    
    return text

knowledge_base = []

# Load each Excel file and convert it into structured text format
for name, path in file_paths.items():
    try:
        df = pd.read_excel(path)
        print(f"✅ Successfully loaded: {name}")
        print(f"📌 Columns: {df.columns.tolist()}")  # Debugging column names
        formatted_text = format_dataframe_as_text(df, name)
        knowledge_base.append(formatted_text)
    except Exception as e:
        print(f"❌ Error loading {name}: {e}")

# Save the combined knowledge base into a text file
with open("knowledge_base.txt", "w") as f:
    f.write("\n\n".join(knowledge_base))

print("✅ Knowledge base prepared successfully!")
"""

import pandas as pd
import json

# File paths for all Excel files
file_paths = {
    "news_posts": "Copy of News Posts.xlsx",
    "data_catalog": "Copy of Data Catalog.xlsx",
    "governance_groups": "Copy of Governance Groups.xlsx",
    "faq": "Copy of Frequently Asked Questions.xlsx",
    "working_groups": "Copy of Working Groups.xlsx",
    "people_database": "Copy of People Database.xlsx",
    "resource_catalog": "Copy of Resource Catalog.xlsx",
}

def format_dataframe_as_dict(df, name):
    """Convert a DataFrame into a structured dictionary format, handling timestamps."""
    structured_data = []

    for _, row in df.iterrows():
        entry = {}
        for col in df.columns:
            if pd.notna(row[col]):
                value = row[col]

                # Convert Timestamp to string
                if isinstance(value, pd.Timestamp):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")  # Format date/time

                entry[col] = value

        structured_data.append(entry)

    return {name: structured_data}

def save_json(data, filename="knowledge_base.json"):
    """Save the structured knowledge base as a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Load each Excel file and convert it into structured JSON format
knowledge_base = {}

for name, path in file_paths.items():
    try:
        df = pd.read_excel(path)
        print(f"✅ Successfully loaded: {name}")
        formatted_data = format_dataframe_as_dict(df, name)
        knowledge_base.update(formatted_data)
    except Exception as e:
        print(f"❌ Error loading {name}: {e}")

# Save the combined knowledge base into a JSON file
save_json(knowledge_base)

print("✅ Knowledge base prepared successfully!")
