from dateutil import parser

# Mapping of common skill name variants to standardized names
SKILL_MAPPING = {
    "ms office": "Microsoft Office",
    "excel": "Microsoft Excel",
    # Add additional mappings as needed
}

def normalize_date(date_str: str) -> str:
    """
    Convert various date string formats to 'YYYY-MM'.
    If parsing fails, returns the original string.
    """
    try:
        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m")
    except Exception:
        return date_str


def normalize_skill(skill: str) -> str:
    """
    Standardize a skill name using the SKILL_MAPPING dictionary.
    Unknown skills are returned trimmed.
    """
    key = skill.strip().lower()
    return SKILL_MAPPING.get(key, skill.strip())

