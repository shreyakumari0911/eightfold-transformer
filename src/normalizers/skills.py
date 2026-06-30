from typing import List
# pyrefly: ignore [missing-import]
from rapidfuzz import process, fuzz

# Canonical skills mapping dictionary
SKILL_SYNONYMS = {
    # C++
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    
    # Python
    "python": "Python",
    "py": "Python",
    
    # JavaScript
    "javascript": "JavaScript",
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    
    # TypeScript
    "typescript": "TypeScript",
    "ts": "TypeScript",
    
    # Node.js
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    
    # React
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    
    # C#
    "c#": "C#",
    "csharp": "C#",
    "c sharp": "C#",
    
    # AWS
    "aws": "AWS",
    "amazon web services": "AWS",
    
    # SQL
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    
    # Docker
    "docker": "Docker",
    
    # Kubernetes
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    
    # Git
    "git": "Git",
    "github": "Git",
}

# The set of unique canonical skill names
CANONICAL_SKILLS = list(set(SKILL_SYNONYMS.values()))

def normalize_skill(skill_str: str) -> str:
    """
    Normalizes a single skill string to its canonical representation.
    First checks the exact synonyms map (case-insensitive),
    and then falls back to fuzzy matching with rapidfuzz if no exact match is found.
    """
    cleaned = skill_str.strip().lower()
    if not cleaned:
        return skill_str
        
    # 1. Check direct synonym mapping
    if cleaned in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned]
        
    # 2. Fuzzy match against all synonyms keys (higher accuracy target)
    synonym_keys = list(SKILL_SYNONYMS.keys())
    match = process.extractOne(cleaned, synonym_keys, scorer=fuzz.ratio)
    if match:
        matched_synonym, score, _ = match
        if score >= 85:  # High confidence threshold
            return SKILL_SYNONYMS[matched_synonym]
            
    # 3. Fuzzy match against canonical names directly
    match_canonical = process.extractOne(cleaned, CANONICAL_SKILLS, scorer=fuzz.ratio)
    if match_canonical:
        matched_canonical, score, _ = match_canonical
        if score >= 85:
            return matched_canonical
            
    # Capitalize first letter of each word if not matched to preserve nice formatting
    return skill_str.strip().title()

def normalize_skills(skills_list: List[str]) -> List[str]:
    """
    Normalizes a list of skills, removing duplicates and empty values.
    """
    normalized = []
    seen = set()
    for skill in skills_list:
        if not skill:
            continue
        norm = normalize_skill(skill)
        if norm.lower() not in seen:
            seen.add(norm.lower())
            normalized.append(norm)
    return normalized
