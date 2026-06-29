import pandas as pd
from typing import Dict, Any, List
from src.parsers.base import BaseParser

class CSVParser(BaseParser):
    """
    Parses candidate information from recruiter CSV files.
    Supports flexible column headers and returns a list of raw candidate dictionaries.
    """
    
    # Header aliases to support different CSV schemas
    HEADER_MAPPING = {
        "full_name": ["full_name", "fullname", "name", "candidate_name"],
        "emails": ["email", "emails", "email_address", "mail"],
        "phones": ["phone", "phones", "phone_number", "telephone", "mobile"],
        "location": ["location", "city", "address", "country"],
        "headline": ["headline", "title", "current_role", "role"],
        "years_experience": ["years_experience", "yoe", "experience_years", "experience"],
        "skills": ["skills", "skill_set", "technologies"],
    }
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses the CSV and returns a list of raw candidate dictionaries.
        """
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file {file_path}: {str(e)}")
            
        candidates = []
        for _, row in df.iterrows():
            candidate_raw = self._parse_row(row)
            candidate_raw["source_file"] = file_path
            candidates.append(candidate_raw)
            
        return candidates
        
    def _parse_row(self, row: pd.Series) -> Dict[str, Any]:
        """
        Extracts candidate fields from a CSV row by checking header aliases.
        """
        raw_data: Dict[str, Any] = {}
        row_keys_lower = {str(k).lower().strip(): v for k, v in row.items()}
        
        # Match standard fields using mapping
        for target_field, aliases in self.HEADER_MAPPING.items():
            value = None
            for alias in aliases:
                if alias in row_keys_lower:
                    val = row_keys_lower[alias]
                    if pd.notna(val):
                        value = str(val).strip()
                    break
            
            if value is not None:
                if target_field in ["emails", "phones"]:
                    # Split comma-separated lists
                    raw_data[target_field] = [x.strip() for x in value.split(",") if x.strip()]
                elif target_field == "skills":
                    # Split comma/semicolon-separated skills
                    delimiters = [",", ";", "|"]
                    pattern = "|".join(map(re.escape, delimiters)) if 're' in globals() else ","
                    import re
                    skills_raw = re.split(r'[,;|]', value)
                    raw_data[target_field] = [x.strip() for x in skills_raw if x.strip()]
                elif target_field == "years_experience":
                    try:
                        raw_data[target_field] = float(value)
                    except ValueError:
                        # Extract first number from string e.g. "5 years" -> 5.0
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", value)
                        raw_data[target_field] = float(match.group()) if match else None
                else:
                    raw_data[target_field] = value
            else:
                if target_field in ["emails", "phones", "skills"]:
                    raw_data[target_field] = []
                else:
                    raw_data[target_field] = None
                    
        return raw_data
