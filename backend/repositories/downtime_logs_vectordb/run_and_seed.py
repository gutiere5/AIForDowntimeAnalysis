import pandas as pd
import re

def clean_html(text):
    """Remove HTML tags and entities from text."""
    if isinstance(text, str):
        text = re.sub('<.*?>', '', text)
        text = re.sub('&[a-z]+;|&#[0-9]+;', '', text)
    return text

def remove_labels_and_parenthetical(text):
    """Remove specific boilerplate labels and parenthetical notes from text."""
    if isinstance(text, str):
        text = re.sub(r'(?:problem|fix/change)\s*:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'problem\s*:\s*fix/change\s*:$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(?:Issue\s*:|Root Cause\s*:|Notes\s*:)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\((?:Updated via TechCenter|created via web)\)\s*', '', text, flags=re.IGNORECASE)
    return text

def normalize_whitespace(text):
    """Normalize whitespace in text."""
    if isinstance(text, str):
        text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_notes(text):
    """Apply all cleaning functions to the notes text."""
    text = clean_html(text)
    text = remove_labels_and_parenthetical(text)
    text = normalize_whitespace(text)
    return text

def seed_database(csv_path='downtime.csv'):
    """Read downtime logs from CSV, clean the notes, and prepare the DataFrame."""

    columns_to_keep = ['Timestamp', 'Downtime Minutes', 'Notes', 'Line']
    df = pd.read_csv(csv_path, usecols=columns_to_keep)
    df['Notes'] = df['Notes'].fillna('').astype(str).str.strip().str.lower()
    df['Notes'] = df['Notes'].apply(clean_notes)
    df['Timestamp'] = pd.to_datetime(df["Timestamp"])
    df['Downtime Minutes'] = df['Downtime Minutes'].astype(int)

    return df







