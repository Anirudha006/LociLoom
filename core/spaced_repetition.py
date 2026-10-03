"""
LociLoom Spaced Repetition Engine (SM-2)
Implements Dr. Piotr Wozniak's SuperMemo-2 (SM-2) algorithm from scratch.
Calculates Ease Factor (EF), interval progression, repetitions count,
and future revision due dates based on retrieval quality (0 to 5).
"""
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any, Optional

DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3

def calculate_sm2(quality: int,
                  repetitions: int,
                  previous_interval: int,
                  previous_ease_factor: float = DEFAULT_EASE_FACTOR) -> Tuple[int, int, float]:
    """
    Core mathematical formulation of SM-2.
    
    Parameters:
    - quality: Integer from 0 (complete blackout) to 5 (perfect recall)
    - repetitions: Consecutive successful reviews count
    - previous_interval: Previous interval length in days
    - previous_ease_factor: Current difficulty multiplier (EF >= 1.3)
    
    Returns:
    - (new_repetitions, new_interval_days, new_ease_factor)
    """
    q = max(0, min(5, int(quality)))

    # Calculate new ease factor
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    delta_ef = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
    new_ef = round(max(MIN_EASE_FACTOR, previous_ease_factor + delta_ef), 2)

    if q >= 3:
        # Successful recall
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = int(round(previous_interval * new_ef))
        new_repetitions = repetitions + 1
    else:
        # Failure / lapse: reset repetitions and start over at 1 day
        new_repetitions = 0
        new_interval = 1

    return (new_repetitions, max(1, new_interval), new_ef)

def score_to_sm2_quality(correct: bool, hints_used: int = 0, response_time: float = 5.0) -> int:
    """
    Translates active quiz retrieval performance into standard SM-2 0-5 quality score.
    - Correct without hints, fast (<7s) -> 5
    - Correct without hints, normal -> 4
    - Correct with 1 hint -> 3
    - Correct with 2 hints -> 2
    - Incorrect, but tried -> 1
    - Total blank / timeout -> 0
    """
    if not correct:
        return 1 if hints_used > 0 or response_time > 2.0 else 0
    
    if hints_used == 0:
        return 5 if response_time <= 7.0 else 4
    elif hints_used == 1:
        return 3
    else:
        return 2

def schedule_next_review(quality: int,
                         repetitions: int,
                         previous_interval: int,
                         previous_ease_factor: float = DEFAULT_EASE_FACTOR,
                         reference_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculates next review interval and calendar due date.
    Returns dictionary ready for database persistence.
    """
    reps, interval, ef = calculate_sm2(
        quality=quality,
        repetitions=repetitions,
        previous_interval=previous_interval,
        previous_ease_factor=previous_ease_factor
    )

    if reference_date:
        try:
            base_dt = datetime.fromisoformat(reference_date[:10])
        except Exception:
            base_dt = datetime.now(timezone.utc)
    else:
        base_dt = datetime.now(timezone.utc)

    next_due_dt = base_dt + timedelta(days=interval)
    next_due_str = next_due_dt.strftime("%Y-%m-%d")

    return {
        "repetitions": reps,
        "interval_days": interval,
        "ease_factor": ef,
        "next_due": next_due_str
    }
