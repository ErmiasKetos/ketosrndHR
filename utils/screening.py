from utils.normalization import normalize_skill


def score_candidate(fields: dict, criteria: list) -> tuple:
    """
    Compute a screening score and summary bullets for a candidate.

    - +1 point for each criterion (keyword/requirement) found in resume text.
    - +0.5 point for each normalized skill matching a criterion.

    Returns:
        score (float): Total score.
        summary (list[str]): Bulleted list of matched items.
    """
    score = 0.0
    summary = []
    text = fields.get('raw_text', '').lower()

    # Match criteria keywords in text
    for crit in criteria:
        crit_low = crit.lower()
        if crit_low in text:
            score += 1.0
            summary.append(f"Matched: {crit}")

    # Match skills with partial weighting
    for skill in fields.get('skills', []):
        norm = normalize_skill(skill)
        if norm.lower() in [c.lower() for c in criteria]:
            score += 0.5
            summary.append(f"Skill: {norm}")

    return score, summary

