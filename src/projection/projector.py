from typing import Dict, Any, Optional, List
from src.schemas.canonical import CandidateProfile

class ProjectionLayer:
    """
    Applies runtime configuration filters and formats to transform the canonical
    CandidateProfile into a customized output dictionary.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
    def project(self, profile: CandidateProfile) -> Dict[str, Any]:
        """
        Transforms a canonical CandidateProfile based on the runtime config.
        """
        # Convert Pydantic model to a raw dictionary
        profile_dict = profile.model_dump()
        
        # 1. Read configuration parameters with defaults
        include_fields = self.config.get("include_fields", None)
        rename_fields = self.config.get("rename_fields", {})
        field_remapping = self.config.get("field_remapping", {})
        include_confidence = self.config.get("include_confidence", True)
        include_provenance = self.config.get("include_provenance", True)
        missing_value_behavior = self.config.get("missing_value_behavior", "null")  # "null" or "exclude"
        
        projected: Dict[str, Any] = {}
        
        # Determine fields to process (either restricted by include_fields or all schema fields)
        canonical_fields = list(profile_dict.keys())
        
        # Filter metadata arrays if explicitly disabled in config
        if not include_confidence:
            if "field_confidence" in canonical_fields:
                canonical_fields.remove("field_confidence")
            if "overall_confidence" in canonical_fields:
                canonical_fields.remove("overall_confidence")
                
        if not include_provenance:
            if "provenance" in canonical_fields:
                canonical_fields.remove("provenance")
                
        # If include_fields is defined, only take fields listed there
        fields_to_process = canonical_fields
        if include_fields is not None:
            # We want to support the user config where they specify target names
            # So if they put a renamed name in include_fields, we should map it back.
            fields_to_process = [f for f in canonical_fields if f in include_fields or rename_fields.get(f) in include_fields or field_remapping.get(f) in include_fields]
            
        for field in canonical_fields:
            if field not in fields_to_process:
                continue
                
            val = profile_dict[field]
            
            # Format/clean nested Pydantic items if they are present in val (like provenance)
            # (already dict form because of model_dump)
            
            # Handle missing values
            is_missing = val is None or (isinstance(val, list) and len(val) == 0) or (isinstance(val, dict) and len(val) == 0)
            
            if is_missing and missing_value_behavior == "exclude":
                continue
                
            # Determine output field name
            output_name = field
            if field in rename_fields:
                output_name = rename_fields[field]
            elif field in field_remapping:
                output_name = field_remapping[field]
                
            projected[output_name] = val
            
        return projected
