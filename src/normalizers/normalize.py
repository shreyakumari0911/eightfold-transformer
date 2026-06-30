from typing import Dict, Any
from src.normalizers.phone import normalize_phone
from src.normalizers.date import normalize_date
from src.normalizers.country import normalize_country
from src.normalizers.skills import normalize_skills

def normalize_raw_profile(raw_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a single candidate's raw profile.
    Applies normalization rules to phone numbers, dates, countries, and skills.
    """
    normalized = raw_profile.copy()
    
    # 1. Normalize name (just strip)
    if raw_profile.get("full_name"):
        normalized["full_name"] = raw_profile["full_name"].strip()
        
    # 2. Normalize emails (lowercase, strip)
    normalized["emails"] = [
        email.strip().lower() 
        for email in raw_profile.get("emails", []) 
        if email.strip()
    ]
    
    # 3. Normalize phones (E.164)
    normalized["phones"] = []
    for phone in raw_profile.get("phones", []):
        norm_phone = normalize_phone(phone)
        if norm_phone:
            normalized["phones"].append(norm_phone)
        else:
            # Keep raw phone if normalization fails, or filter it out?
            # Let's filter out invalid phones to be strict, or keep them if they are digits.
            # To be safe, keep the normalized one if parsed, otherwise discard if malformed.
            pass
    # Deduplicate phones while keeping order
    normalized["phones"] = list(dict.fromkeys(normalized["phones"]))
            
    # 4. Normalize location
    # If location is available, try to resolve country to ISO-3166.
    # We will format location to be 'City, State, ISO-Country' if we can extract it,
    # or just keep the original location but replace the country token with normalized country code.
    if raw_profile.get("location"):
        loc = raw_profile["location"].strip()
        country_code = normalize_country(loc)
        if country_code:
            # Replace country string at the end with code if possible, or append it
            # For simplicity, we can keep the original location, but if the original is just the country,
            # we normalize it.
            normalized["location"] = loc
            normalized["country_code"] = country_code
        else:
            normalized["location"] = loc
            normalized["country_code"] = None
    else:
        normalized["country_code"] = None

    # 5. Normalize skills (canonical mapping)
    normalized["skills"] = normalize_skills(raw_profile.get("skills", []))
    
    # 6. Normalize work experience dates
    normalized["experience"] = []
    for job in raw_profile.get("experience", []):
        job_norm = job.copy()
        job_norm["start_date"] = normalize_date(job.get("start_date"))
        job_norm["end_date"] = normalize_date(job.get("end_date"))
        # Clean title & company
        if job.get("job_title"):
            job_norm["job_title"] = job["job_title"].strip()
        if job.get("company"):
            job_norm["company"] = job["company"].strip()
        normalized["experience"].append(job_norm)
        
    # 7. Normalize education dates
    normalized["education"] = []
    for edu in raw_profile.get("education", []):
        edu_norm = edu.copy()
        edu_norm["start_date"] = normalize_date(edu.get("start_date"))
        edu_norm["end_date"] = normalize_date(edu.get("end_date"))
        if edu.get("degree"):
            edu_norm["degree"] = edu["degree"].strip()
        if edu.get("institution"):
            edu_norm["institution"] = edu["institution"].strip()
        normalized["education"].append(edu_norm)
        
    return normalized
