import re
import pandas as pd


def clean_data(df) -> pd.DataFrame:
    requred_columns = ['Timestamp', 'Downtime Minutes', 'Notes']
    for col in requred_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df['Notes'] = df['Notes'].fillna('').astype(str)
    df['Notes'] = df['Notes'].apply(clean_html)
    df['Notes'] = df['Notes'].apply(remove_labels_and_parenthetical)
    df['Notes'] = df['Notes'].apply(normalize_whitespace)
    df['Notes'] = df['Notes'].str.lower().str.strip()

    df['Timestamp'] = pd.to_datetime(df["Timestamp"], errors='coerce')
    df['Downtime Minutes'] = pd.to_numeric(df['Downtime Minutes'], errors='coerce').fillna(0).astype(int)
    return df


def clean_html(text):
    if not isinstance(text, str):
        return text
    text_without_tags = re.sub('<.*?>', '', text)
    text_cleaned = re.sub('&[a-z]+;|&#[0-9]+;', '', text_without_tags)
    return text_cleaned


def remove_labels_and_parenthetical(text):
    if not isinstance(text, str):
        return text

    patterns = [
        r'(?:problem|fix/change)\s*:',
        r'problem\s*:\s*fix/change\s*:$',
        r'(?:Issue\s*:|Root Cause\s*:|Notes\s*:)\s*',
        r'\((?:Updated via TechCenter|created via web)\)\s*'
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text


def normalize_whitespace(text):
    if not isinstance(text, str):
        return text
    return re.sub(r'\s+', ' ', text).strip()
