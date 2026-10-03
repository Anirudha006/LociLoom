"""
LociLoom Retrieval Practice Quiz Engine
Generates 4 distinct retrieval practice question types along the memory palace:
1. Type Concept: Free active recall with rapidfuzz forgiving typo matching (threshold >= 75%)
2. Multiple Choice: 4-option discriminative recognition
3. Reverse Question: Maps concept -> corresponding physical locus station
4. Ordering Question: Route sequential positioning and chronological recall
Includes two-tier graduated hints and instant mnemonic feedback.
"""
import random
import re
from typing import List, Dict, Any, Tuple, Optional
from rapidfuzz import fuzz

def evaluate_typed_answer(user_input: str, target_concept: str, threshold: float = 75.0) -> Tuple[bool, float]:
    """
    Evaluates student's typed response using forgiving fuzzy string matching.
    Returns: (is_correct, similarity_score_0_to_100)
    """
    if not user_input or not user_input.strip():
        return (False, 0.0)

    u_clean = re.sub(r'[^a-zA-Z0-9\s]', '', user_input.lower()).strip()
    t_clean = re.sub(r'[^a-zA-Z0-9\s]', '', target_concept.lower()).strip()

    if u_clean == t_clean:
        return (True, 100.0)

    # Calculate token sort and ratio scores
    score_sort = fuzz.token_sort_ratio(u_clean, t_clean)
    score_ratio = fuzz.ratio(u_clean, t_clean)
    best_score = float(max(score_sort, score_ratio))

    return (best_score >= threshold, best_score)

def get_hints(concept: str, visual_object: str, emoji: str = "💡") -> Tuple[str, str]:
    """
    Generates a 2-tier graduated hint:
    - Tier 1: First letter + character mask
    - Tier 2: The visual mnemonic token
    """
    clean = concept.strip()
    first_char = clean[0].upper() if clean else "?"
    words = clean.split()
    
    # Word shape mask
    mask_words = []
    for w in words:
        if len(w) <= 2:
            mask_words.append(w)
        else:
            mask_words.append(w[0] + "_" * (len(w) - 1))
    tier1_hint = f"Starts with '{first_char}' — Word mask: {' '.join(mask_words)} ({len(clean)} chars)"
    
    tier2_hint = f"Mnemonic Landmark: {emoji} {visual_object}"
    return (tier1_hint, tier2_hint)

def generate_quiz_deck(concepts: List[Dict[str, Any]], count: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Synthesizes a randomized deck of retrieval questions across the 4 question types.
    Ensures every concept is tested and question formats are balanced.
    """
    if not concepts:
        return []

    deck = []
    q_types = ["type_concept", "mcq", "reverse", "ordering"]
    all_concept_names = [c["concept_text"] if "concept_text" in c else c.get("concept", "") for c in concepts]
    all_locations = [c.get("location_name", f"Station {i+1}") for i, c in enumerate(concepts)]

    for idx, c in enumerate(concepts):
        concept_name = c["concept_text"] if "concept_text" in c else c.get("concept", f"Concept {idx+1}")
        loc_name = c.get("location_name", f"Station {idx+1}")
        vis_obj = c.get("visual_object", "landmark")
        emoji = c.get("emoji", "📍")
        reason = c.get("visual_reason", "")
        concept_id = c.get("id", idx + 1)
        
        q_type = q_types[idx % len(q_types)]
        tier1, tier2 = get_hints(concept_name, vis_obj, emoji)

        question_data = {
            "concept_id": concept_id,
            "concept_name": concept_name,
            "location_name": loc_name,
            "visual_object": vis_obj,
            "emoji": emoji,
            "visual_reason": reason,
            "order_index": idx,
            "question_type": q_type,
            "tier1_hint": tier1,
            "tier2_hint": tier2,
            "feedback_story": f"In the {loc_name}, remember {emoji} {vis_obj}: {reason}."
        }

        if q_type == "type_concept":
            question_data["prompt"] = f"What key concept was anchored at **{loc_name}** (Stop #{idx+1})?"
            question_data["correct_answer"] = concept_name

        elif q_type == "mcq":
            question_data["prompt"] = f"Which concept did you encounter at **{loc_name}**?"
            question_data["correct_answer"] = concept_name
            # Generate 3 distractors
            distractors = [c_other for c_other in all_concept_names if c_other != concept_name]
            # If not enough concepts, add generic distractors
            if len(distractors) < 3:
                distractors.extend(["Entropy", "Homeostasis", "Recursion", "Velocity"][: 3 - len(distractors)])
            sampled = random.sample(distractors, min(3, len(distractors)))
            options = sampled + [concept_name]
            random.shuffle(options)
            question_data["options"] = options

        elif q_type == "reverse":
            question_data["prompt"] = f"At which location in your palace was **'{concept_name}'** placed?"
            question_data["correct_answer"] = loc_name
            distractors = [l_other for l_other in all_locations if l_other != loc_name]
            if len(distractors) < 3:
                distractors.extend(["Library", "Attic", "Garden Bridge", "Hallway"][: 3 - len(distractors)])
            sampled = random.sample(distractors, min(3, len(distractors)))
            options = sampled + [loc_name]
            random.shuffle(options)
            question_data["options"] = options

        elif q_type == "ordering":
            # Select another station along the route
            other_idx = (idx + random.choice([1, 2, -1])) % len(concepts)
            if other_idx == idx:
                other_idx = (idx + 1) % len(concepts)
            other_loc = all_locations[other_idx]
            
            first_loc = loc_name if idx < other_idx else other_loc
            question_data["prompt"] = f"Between **{loc_name}** and **{other_loc}**, which one comes earlier along your palace route?"
            question_data["correct_answer"] = first_loc
            options = [loc_name, other_loc]
            random.shuffle(options)
            question_data["options"] = options

        deck.append(question_data)

    random.shuffle(deck)
    if count and count < len(deck):
        return deck[:count]
    return deck
