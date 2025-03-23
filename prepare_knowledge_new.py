from pathlib import Path
import pandas as pd
import json

# Use the current working directory
base_path = Path(".")

file_info = {
    "Copy of News Posts.xlsx": ["News Posts"],
    "Copy of Data Catalog.xlsx": ["Data Catalog"],
    "Copy of Governance Groups.xlsx": ["Governance Groups"],
    "Copy of Frequently Asked Questions.xlsx": ["FAQ Questions"],
    "Copy of Working Groups.xlsx": ["Working Groups"],
    "Copy of People Database.xlsx": ["People"],
    "Copy of Resource Catalog.xlsx": ["Resource Catalog"]
}

# Base path
base_path = Path("")

# Function to safely get cell content
def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

# Store cleaned entries here
knowledge_entries = []

# Process each file and sheet
for file, sheets in file_info.items():
    for sheet in sheets:
        try:
            df = pd.read_excel(base_path / file, sheet_name=sheet)
            for _, row in df.iterrows():
                content = " ".join([f"{col}: {safe_str(row[col])}" for col in df.columns if not pd.isna(row[col])])
                entry = {
                    "source": sheet,
                    "title": safe_str(row[df.columns[0]])[:100],  # first column as title (truncated)
                    "content": content,
                    "tags": [],
                    "url": None
                }
                knowledge_entries.append(entry)
        except Exception as e:
            print(f"Error processing {file} - {sheet}: {e}")

# Save combined JSON to local folder
output_path = base_path / "combined_knowledge_base.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(knowledge_entries, f, indent=2)

print(f"✅ Knowledge base saved to {output_path}")
