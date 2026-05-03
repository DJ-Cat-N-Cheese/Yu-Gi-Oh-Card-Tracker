import re

def clean_name_fallback(clean_name, ygo_service):
    parts = clean_name.split(' - ')
    for i in range(len(parts), 0, -1):
        candidate = ' - '.join(parts[:i]).strip()
        matched = ygo_service.search_by_name(candidate, language='en')
        if matched:
            return matched
    return None
