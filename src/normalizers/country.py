from typing import Optional
import re

# Comprehensive mapping of common countries and their abbreviations to ISO-3166 alpha-2 codes.
COUNTRY_MAP = {
    "united states": "US", "usa": "US", "united states of america": "US", "u.s.a.": "US", "us": "US",
    "india": "IN", "ind": "IN",
    "united kingdom": "GB", "uk": "GB", "u.k.": "GB", "great britain": "GB", "england": "GB", "scotland": "GB",
    "canada": "CA", "can": "CA",
    "germany": "DE", "deutschland": "DE", "de": "DE",
    "france": "FR", "fra": "FR",
    "australia": "AU", "aus": "AU",
    "singapore": "SG", "sgp": "SG", "sg": "SG",
    "japan": "JP", "jpn": "JP",
    "china": "CN", "chn": "CN",
    "brazil": "BR", "bra": "BR",
    "netherlands": "NL", "nld": "NL", "holland": "NL",
    "switzerland": "CH", "che": "CH",
    "sweden": "SE", "swe": "SE",
    "spain": "ES", "esp": "ES",
    "italy": "IT", "ita": "IT",
    "russia": "RU", "rus": "RU",
    "south africa": "ZA", "zaf": "ZA",
    "mexico": "MX", "mex": "MX",
    "new zealand": "NZ", "nzl": "NZ",
    "ireland": "IE", "irl": "IE",
}

def normalize_country(country_str: str) -> Optional[str]:
    """
    Normalize country strings to ISO-3166 alpha-2 code.
    If a full location string is passed, attempts to find a country name/abbreviation.
    """
    if not country_str:
        return None
        
    cleaned = country_str.strip().lower()
    
    # Try exact match first
    if cleaned in COUNTRY_MAP:
        return COUNTRY_MAP[cleaned]
        
    # If it is a full location string (e.g. "San Francisco, CA, USA" or "Bangalore, India")
    # check the tokens, especially the last token after commas.
    parts = [p.strip().lower() for p in re.split(r'[,|]', country_str)]
    for part in reversed(parts):
        # Remove trailing periods
        part_clean = part.replace(".", "").strip()
        if part_clean in COUNTRY_MAP:
            return COUNTRY_MAP[part_clean]
            
    # Fuzzy matching token check inside the text
    for name, code in COUNTRY_MAP.items():
        if re.search(r'\b' + re.escape(name) + r'\b', cleaned):
            return code
            
    # If the string itself is already a valid 2-letter uppercase code, return it.
    if len(country_str) == 2 and country_str.isalpha():
        return country_str.upper()
        
    return None
