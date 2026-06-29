from typing import Dict, Any, Tuple
from pydantic import ValidationError
from src.schemas.canonical import CandidateProfile

def validate_canonical_profile(profile_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates a candidate profile dictionary against the canonical Pydantic schema.
    Returns (True, "") if valid, or (False, "<readable_errors>") if invalid.
    """
    try:
        # Attempt to parse/validate using the Pydantic model
        CandidateProfile(**profile_data)
        return True, ""
    except ValidationError as e:
        # Formulate a readable error report
        errors_summary = []
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            input_val = error.get("input", "N/A")
            errors_summary.append(f"Field '{loc}': {msg} (Provided value: {input_val})")
            
        readable_error_msg = "\n".join(errors_summary)
        return False, readable_error_msg

def validate_projected_profile(projected_data: Dict[str, Any], config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates that the projected output profile matches expected constraints.
    Checks basic requirements like candidate_id (or renamed equivalent) presence, 
    only if it was not explicitly excluded by the inclusion configuration.
    """
    include_fields = config.get("include_fields", None)
    
    # Look for the candidate identifier under any alias
    id_aliases = ["candidate_id"]
    if "rename_fields" in config:
        for k, v in config["rename_fields"].items():
            if k == "candidate_id":
                id_aliases.append(v)
    if "field_remapping" in config:
        for k, v in config["field_remapping"].items():
            if k == "candidate_id":
                id_aliases.append(v)
                
    # If include_fields is specified and candidate_id is not in it, we do not require it.
    if include_fields is not None:
        id_is_included = any(alias in include_fields for alias in id_aliases)
        if not id_is_included:
            return True, ""
            
    has_id = any(alias in projected_data for alias in id_aliases)
    if not has_id:
        return False, f"Validation Error: Projected profile is missing a candidate identifier field (expected one of: {id_aliases})"
        
    return True, ""
