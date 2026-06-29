from typing import Dict, List, Any
from src.schemas.canonical import FieldProvenance

# Method-based confidence levels as specified by user requirements
CONFIDENCE_LEVELS = {
    "direct_resume": 0.95,
    "csv_direct": 0.90,
    "regex": 0.80,
    "heuristic": 0.60,
    "unknown": 0.30
}

def calculate_field_confidence(source: str, method: str) -> float:
    """
    Determine the confidence score for an extracted value based on the source and extraction method.
    """
    method_lower = method.lower()
    source_lower = source.lower()
    
    # 1. Direct Resume extraction (structured resume fields, if any, or high confidence)
    if "resume" in source_lower and "direct" in method_lower:
        return CONFIDENCE_LEVELS["direct_resume"]
        
    # 2. CSV directly parsed fields
    if "csv" in source_lower and ("direct" in method_lower or "csv" in method_lower):
        return CONFIDENCE_LEVELS["csv_direct"]
        
    # 3. Regex extraction
    if "regex" in method_lower:
        return CONFIDENCE_LEVELS["regex"]
        
    # 4. Heuristics extraction
    if "heuristic" in method_lower:
        return CONFIDENCE_LEVELS["heuristic"]
        
    # 5. Fallbacks based on method name matches
    if "direct" in method_lower:
        return 0.90
    if "parse" in method_lower:
        return 0.75
        
    return CONFIDENCE_LEVELS["unknown"]

def calculate_overall_confidence(field_confidences: Dict[str, float]) -> float:
    """
    Computes overall confidence score from field confidences.
    Uses a simple average of all populated field confidence scores.
    """
    if not field_confidences:
        return 0.0
        
    total_score = sum(field_confidences.values())
    count = len(field_confidences)
    
    return round(total_score / count, 3)
