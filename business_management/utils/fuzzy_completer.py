from fuzzywuzzy import process
from typing import List

def get_fuzzy_matches(query: str, choices: List[str], limit: int = 10, threshold: int = 40) -> List[str]:
    if not query.strip():
        return choices
    matches = process.extract(query, choices, limit=limit)
    filtered = [match[0] for match in matches if match[1] > threshold]
    return filtered if filtered else choices
