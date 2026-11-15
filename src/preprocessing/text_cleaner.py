"""
AutoSense Text Preprocessing Module
Implements domain-aware text cleaning for automobile customer reviews:
1. Normalizes whitespace and text encodings.
2. Expands common English contractions while preserving negations ('not', 'never', 'no').
3. Strips HTML tags and URLs.
4. Preserves automotive numbers and technical specs (e.g. 1.5L, 20kmpl, 5-speed, 6th gear).
5. Retains meaningful punctuation (!, ?) while removing arbitrary noise.
"""
import re
import html

CONTRACTIONS = {
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "cannot",
    "couldn't": "could not",
    "won't": "will not",
    "wouldn't": "would not",
    "hasn't": "has not",
    "haven't": "have not",
    "hadn't": "had not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "it's": "it is",
    "that's": "that is",
    "what's": "what is",
    "there's": "there is",
    "i'm": "i am",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have"
}

def clean_automobile_text(text: str, lower: bool = True) -> str:
    """
    Cleans an automotive review string with negation and spec preservation.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
        
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # Expand contractions (lowercasing words for matching)
    words = text.split()
    expanded_words = []
    for w in words:
        clean_w = w.lower()
        if clean_w in CONTRACTIONS:
            expanded_words.append(CONTRACTIONS[clean_w])
        else:
            expanded_words.append(w)
    text = ' '.join(expanded_words)
    
    # Optional lowercase
    if lower:
        text = text.lower()
        
    # Standardize multiple exclamation/question marks to single
    text = re.sub(r'!+', ' ! ', text)
    text = re.sub(r'\?+', ' ? ', text)
    
    # Remove special control characters but preserve alphanumeric, punctuation, units
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'\-/%]', ' ', text)
    
    # Normalize multiple whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
