import phonenumbers
from typing import Optional

def normalize_phone(phone_str: str, default_region: str = "US") -> Optional[str]:
    """
    Normalize phone numbers to E.164 format.
    Example: "+1 555-555-5555" -> "+15555555555"
    """
    if not phone_str:
        return None
    
    # Strip basic prefix labels if extracted raw
    cleaned = phone_str.strip()
    for prefix in ["Phone:", "Tel:", "Mobile:", "Cell:"]:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
            
    try:
        # If the phone string doesn't start with '+' and doesn't contain a country code,
        # it will be parsed using the default region.
        parsed = phonenumbers.parse(cleaned, default_region)
        if phonenumbers.is_valid_number(parsed) or phonenumbers.is_possible_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        
        # Fallback: try parsing as is if it has a leading plus even if invalid for region
        if cleaned.startswith("+"):
            parsed_any = phonenumbers.parse(cleaned, None)
            if phonenumbers.is_valid_number(parsed_any) or phonenumbers.is_possible_number(parsed_any):
                return phonenumbers.format_number(parsed_any, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass
    
    return None
