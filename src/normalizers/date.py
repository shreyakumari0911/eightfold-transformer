import re
import datetime
# pyrefly: ignore [missing-import]
from dateutil import parser
from typing import Optional

def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date strings to YYYY-MM format.
    Handles 'Present' / 'Current', year-only values, and standard formats.
    """
    if not date_str:
        return None
        
    val = date_str.strip()
    val_lower = val.lower()
    
    if val_lower in ["present", "current", "now", "ongoing", "till date", "till now"]:
        return "Present"
        
    # Check if the string matches a simple 4-digit year (e.g., "2020")
    if re.match(r"^\d{4}$", val):
        return f"{val}-01"
        
    try:
        # Use a fixed default date (Jan 1, 2000) so missing parts (like month)
        # resolve deterministically to January, rather than using the current system date.
        default_dt = datetime.datetime(2000, 1, 1)
        parsed = parser.parse(val, default=default_dt, fuzzy=True)
        return parsed.strftime("%Y-%m")
    except Exception:
        pass
        
    return None
