"""
LociLoom Key-Point and Keyword Extractor
Extracts salient, ordered concepts from student notes or topic text.
Uses spaCy (noun chunks, named entities, dependency parsing) + TF-IDF ranking,
with an automatic regex/NLTK fallback when spaCy is unavailable.
Maintains logical chronological order for coherent narrative journeying.
"""
import os
import re
import math
import json
from typing import List, Dict, Any, Optional

# Try loading spaCy model gracefully
_SPACY_NLP = None
try:
    import spacy
    try:
        _SPACY_NLP = spacy.load("en_core_web_sm")
    except Exception:
        # Fallback: model not found in package registry
        _SPACY_NLP = None
except ImportError:
    _SPACY_NLP = None

# Built-in lightweight stop words for fallback extraction
COMMON_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "step", "steps", "called", "known", "process", "system", "uses", "used",
    "first", "second", "third", "next", "finally", "last", "furthermore", "moreover",
    "many", "various", "several", "different", "multiple", "field", "fields",
    "type", "types", "way", "ways", "thing", "things", "aspect", "aspects",
    "lociloom", "palace", "palaces", "station", "stations", "locus", "loci",
    "mnemonic", "mnemonics", "narrative", "associative", "discipline", "architecture", "summary",
    "fact", "facts", "real", "world", "observation", "observations", "finding", "findings",
    "clue", "clues", "ingredient", "ingredients", "exist", "exists", "existing",
    "foundational", "paradigm", "paradigms", "common", "include", "includes", "branch", "branches",
    "each", "every", "all", "some", "any", "across", "start", "starting", "overall"
}

_KNOWN_CONCEPTS_CACHE = None

def _get_known_concepts():
    """Lazily loads known curated concepts from dictionary to boost concept extraction precision."""
    global _KNOWN_CONCEPTS_CACHE
    if _KNOWN_CONCEPTS_CACHE is None:
        try:
            import json
            dict_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "concept_visual_dictionary.json")
            if os.path.exists(dict_path):
                with open(dict_path, "r", encoding="utf-8") as f:
                    _KNOWN_CONCEPTS_CACHE = set(json.load(f).keys())
            else:
                _KNOWN_CONCEPTS_CACHE = set()
        except Exception:
            _KNOWN_CONCEPTS_CACHE = set()
    return _KNOWN_CONCEPTS_CACHE

def sanitize_text(text: str, max_chars: int = 5000) -> str:
    """Sanitizes and caps input text to ensure memory bounds, stripping metadata banners and markdown headers."""
    if not text:
        return ""
    # Strip HTML tags and null bytes
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = cleaned.replace("\x00", "")

    # Strip markdown headers (e.g. ###, ##, #) and markdown bold/italics
    cleaned = re.sub(r'(?m)^\s*#{1,6}\s*', '', cleaned)
    cleaned = re.sub(r'[*_`~]+', ' ', cleaned)

    # Strip potential LociLoom summary export banners if user repastes a summary
    cleaned = re.sub(r'(?i)lociloom\s+memory\s+palace:[^\n]*\n?', '', cleaned)
    cleaned = re.sub(r'(?i)discipline:[^\n]*architecture:[^\n]*\n?', '', cleaned)
    cleaned = re.sub(r'(?i)vivid\s+narrative\s+walk:[^\n]*\n?', '', cleaned)
    cleaned = re.sub(r'(?i)accessible\s+ordered\s+route\s+guide[^\n]*\n?', '', cleaned)
    cleaned = re.sub(r'={10,}', '', cleaned)
    cleaned = re.sub(r'-{10,}', '', cleaned)
    
    return cleaned.strip()[:max_chars]

def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences using regex boundary detection."""
    # Handles basic periods, exclamation points, and question marks
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 5]
    if not sentences and text.strip():
        sentences = [text.strip()]
    return sentences

def extract_concepts_spacy(text: str, max_concepts: int = 8) -> List[Dict[str, Any]]:
    """Extracts concepts using spaCy noun chunks, NER, and TF-IDF relevance."""
    global _SPACY_NLP
    if _SPACY_NLP is None:
        return extract_concepts_fallback(text, max_concepts)

    doc = _SPACY_NLP(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 5]
    if not sentences:
        sentences = [text]

    # Calculate token frequencies for basic TF weighting
    word_freq = {}
    for token in doc:
        w = token.lemma_.lower()
        if not token.is_stop and not token.is_punct and len(w) > 2:
            word_freq[w] = word_freq.get(w, 0) + 1

    candidate_spans = []

    known_concepts = _get_known_concepts()

    # 1. Noun chunks
    for chunk in doc.noun_chunks:
        raw_words = chunk.text.lower().strip().split()
        lemma_words = chunk.lemma_.lower().strip().split()
        words = []
        for rw, lw in zip(raw_words, lemma_words):
            target = "data" if rw in ("data", "datum") else lw
            if target not in COMMON_STOP_WORDS and len(target) > 2:
                words.append(target)
        if words and len(words) <= 4:
            cand = " ".join(words)
            raw_cand = " ".join([rw for rw in raw_words if rw not in COMMON_STOP_WORDS and len(rw) > 2])
            # Find the sentence containing this chunk
            supporting_sent = chunk.sent.text.strip()
            start_pos = chunk.start_char
            # Score based on frequency and token positions
            score = sum(word_freq.get(w, 1) for w in words) * (1.2 if len(words) > 1 else 1.0)
            
            # Substantially prioritize concepts recognized in verified curriculum dictionary
            if known_concepts:
                if cand in known_concepts:
                    score += 40.0
                elif raw_cand in known_concepts:
                    cand = raw_cand
                    score += 40.0

            candidate_spans.append({
                "concept": cand,
                "start_char": start_pos,
                "sentence": supporting_sent,
                "score": score
            })

    # 2. Named entities
    for ent in doc.ents:
        clean = ent.lemma_.lower().strip()
        words = [w for w in clean.split() if w not in COMMON_STOP_WORDS and len(w) > 2]
        if words and len(words) <= 4:
            cand = " ".join(words)
            supporting_sent = ent.sent.text.strip()
            score = sum(word_freq.get(w, 1) for w in words) * 1.5
            candidate_spans.append({
                "concept": cand,
                "start_char": ent.start_char,
                "sentence": supporting_sent,
                "score": score
            })

    return _filter_and_rank_candidates(candidate_spans, sentences, max_concepts)

def extract_concepts_fallback(text: str, max_concepts: int = 8) -> List[Dict[str, Any]]:
    """
    Robust fallback keyword extraction using regex and TF-IDF heuristic
    when spaCy is unavailable or offline.
    """
    sentences = split_into_sentences(text)
    candidate_spans = []

    # Tokenize words per sentence
    total_words = []
    for s_idx, sent in enumerate(sentences):
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', sent.lower())
        meaningful = [w for w in tokens if w not in COMMON_STOP_WORDS]
        total_words.extend(meaningful)

        # Look for multi-word phrases (bigrams and trigrams)
        for i in range(len(meaningful)):
            # 1-gram
            candidate_spans.append({
                "concept": meaningful[i],
                "start_char": s_idx * 1000 + i,
                "sentence": sent,
                "score": 1.0
            })
            # 2-gram
            if i + 1 < len(meaningful):
                candidate_spans.append({
                    "concept": f"{meaningful[i]} {meaningful[i+1]}",
                    "start_char": s_idx * 1000 + i,
                    "sentence": sent,
                    "score": 1.4
                })

    # Calculate frequencies
    freq = {}
    for w in total_words:
        freq[w] = freq.get(w, 0) + 1

    for c in candidate_spans:
        words = c["concept"].split()
        c["score"] *= sum(freq.get(w, 1) for w in words)

    return _filter_and_rank_candidates(candidate_spans, sentences, max_concepts)

def _filter_and_rank_candidates(candidates: List[Dict[str, Any]],
                                sentences: List[str],
                                max_concepts: int) -> List[Dict[str, Any]]:
    """Deduplicates candidates and selects top-N, preserving chronological appearance."""
    if not candidates:
        # Fallback for ultra-short notes
        clean_words = [s for s in sentences if s]
        return [{
            "concept": s[:30],
            "supporting_sentence": s,
            "score": 1.0
        } for s in clean_words[:max_concepts]]

    # Deduplicate by concept string, keeping highest score and earliest appearance
    unique_concepts = {}
    for c in candidates:
        text = c["concept"].strip()
        if not text or len(text) < 3 or text.lower() in COMMON_STOP_WORDS:
            continue
        # Avoid sub-string redundancies (e.g. 'plant' if 'emerald plant' already exists)
        if text not in unique_concepts or c["score"] > unique_concepts[text]["score"]:
            unique_concepts[text] = c

    # Sort all candidates by relevance score descending
    sorted_by_score = sorted(unique_concepts.values(), key=lambda x: x["score"], reverse=True)

    # Pick top-N candidates
    top_candidates = sorted_by_score[:max_concepts]

    # Re-sort chosen candidates by earliest chronological appearance in the text
    # This is crucial for Method of Loci so the story walks logically through the notes!
    chronological = sorted(top_candidates, key=lambda x: x["start_char"])

    results = []
    for item in chronological:
        c_clean = re.sub(r'^[#*_\-`~>:\s]+', '', item["concept"]).strip()
        c_clean = re.sub(r'[#*_\-`~>:\s]+$', '', c_clean).strip()
        if not c_clean:
            continue
        results.append({
            "concept": c_clean.title(),
            "supporting_sentence": item["sentence"],
            "score": round(item["score"], 2)
        })

    # Ensure we return at least 3 concepts if input has multiple sentences
    if len(results) < 3 and len(sentences) >= 3:
        for s in sentences:
            if len(results) >= max_concepts:
                break
            first_phrase = s.split(',')[0].split(';')[0][:25].strip()
            if first_phrase and not any(r["concept"].lower() == first_phrase.lower() for r in results):
                results.append({
                    "concept": first_phrase.title(),
                    "supporting_sentence": s,
                    "score": 0.5
                })

    return results

def extract_key_concepts(text: str, max_concepts: int = 8) -> List[Dict[str, Any]]:
    """Public interface for key-point extraction."""
    clean = sanitize_text(text)
    if not clean:
        return []
    
    if _SPACY_NLP is not None:
        try:
            return extract_concepts_spacy(clean, max_concepts)
        except Exception:
            return extract_concepts_fallback(clean, max_concepts)
    else:
        return extract_concepts_fallback(clean, max_concepts)
