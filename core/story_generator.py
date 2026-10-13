"""
LociLoom Vivid Story Generator
Weaves concrete mnemonic objects along ordered palace loci into memorable narratives.
Supports three distinctive psychological encoding styles:
1. Normal: Logical, exploratory, sensory-rich walkthrough
2. Funny: Absurdist, humorous, whimsical slapstick interactions
3. Dramatic: Epic, theatrical, high-stakes cinematic saga
Includes an optional, disabled-by-default LLM mode hook.
"""
import random
from typing import List, Dict, Any, Optional

# Diverse sentence templates linking locus station, previous object, and current object
NORMAL_TEMPLATES = [
    "You step into the {location}, where a {current_obj} catches your eye, representing {concept}.",
    "Moving forward into the {location}, you find a {current_obj} resting quietly, reinforcing {concept}.",
    "As you approach the {location}, the {prev_obj} directs your attention toward a {current_obj}, anchoring {concept}.",
    "Passing through the {location}, you discover a {current_obj} glowing under the ambient light, embodying {concept}.",
    "Arriving at the {location}, you inspect a {current_obj} set deliberately in place to symbolize {concept}.",
    "Next along your path at the {location}, the {current_obj} stands out clearly, fixing {concept} in mind.",
    "Pausing beside the {location}, you interact with a {current_obj}, solidifying {concept} in memory."
]

FUNNY_TEMPLATES = [
    "You stumble clumsily into the {location}, only to get smacked in the shin by a mischievous {current_obj} representing {concept}!",
    "Suddenly in the {location}, a wild {current_obj} starts dancing an awkward salsa to teach you {concept}!",
    "Leaving the {prev_obj} behind, you skid into the {location} where an oversized {current_obj} is wearing a party hat for {concept}!",
    "At the {location}, you trip over a {current_obj} that lets out a squeaky honk, hilariously reminding you of {concept}!",
    "You burst into the {location} and catch a {current_obj} attempting to juggle bananas while shouting about {concept}!",
    "In the {location}, a cheeky {current_obj} shoots confetti straight into the air to celebrate {concept}!",
    "Right in the center of the {location}, a {current_obj} is balancing precariously on a unicycle just to prove {concept}!"
]

DRAMATIC_TEMPLATES = [
    "Thunder rumbles as you breach the {location}, where an ancient {current_obj} pulses with raw arcane power for {concept}!",
    "With heart pounding, you enter the {location} as a {current_obj} ignites in radiant blinding flames, immortalizing {concept}!",
    "Guided by the spectral glow of the {prev_obj}, you storm the {location} where the legendary {current_obj} seals the fate of {concept}!",
    "A deep shadow falls across the {location} until a heroic {current_obj} emerges from the mist to defend {concept}!",
    "At the precipice of the {location}, cosmic lightning strikes a {current_obj}, etching {concept} into eternity!",
    "You cross the threshold of the {location} just as a {current_obj} vibrates violently, unlocking the secrets of {concept}!",
    "Echoes shake the {location} as an awe-inspiring {current_obj} rises into the air, commanding total mastery over {concept}!"
]

def generate_palace_story(assigned_concepts: List[Dict[str, Any]],
                          style: str = "Normal",
                          use_llm: bool = False,
                          llm_api_key: Optional[str] = None) -> str:
    """
    Generates a coherent, vivid multi-station story linking objects in route order.
    Exactly one memorable sentence per location.
    
    If use_llm is True and an API key is provided, an external LLM call could be placed,
    otherwise uses the robust, zero-cost offline rule-based templates.
    """
    if not assigned_concepts:
        return "No concepts found to weave a story."

    # If user explicitly opted into LLM mode, attempt Google Gemini generation first
    if use_llm:
        try:
            from core.gemini_client import generate_gemini_palace_story
            gemini_story = generate_gemini_palace_story(assigned_concepts, style=style, api_key=llm_api_key)
            if gemini_story:
                return gemini_story
        except Exception:
            pass

    style_clean = style.lower().strip()
    if style_clean == "funny":
        templates = FUNNY_TEMPLATES
    elif style_clean == "dramatic":
        templates = DRAMATIC_TEMPLATES
    else:
        templates = NORMAL_TEMPLATES

    story_sentences = []
    prev_obj_name = "initial doorway"

    for idx, c in enumerate(assigned_concepts):
        loc = c.get("location_name", f"Station {idx+1}")
        curr_obj = c.get("visual_object", "symbolic token")
        concept = c.get("concept", f"Concept {idx+1}")

        # Pick a non-repeating template based on index and modulo
        template_pool = [t for t in templates]
        chosen_template = template_pool[idx % len(template_pool)]

        # If it's the first stop and template expects prev_obj, adapt gracefully
        if idx == 0 and "{prev_obj}" in chosen_template:
            chosen_template = templates[0]

        sentence = chosen_template.format(
            location=loc,
            current_obj=curr_obj,
            prev_obj=prev_obj_name,
            concept=concept
        )
        story_sentences.append(sentence)
        prev_obj_name = curr_obj

    return " ".join(story_sentences)
