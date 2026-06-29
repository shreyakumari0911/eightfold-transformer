import pytest
from src.normalizers.phone import normalize_phone
from src.normalizers.date import normalize_date
from src.normalizers.skills import normalize_skill, normalize_skills
from src.merger.profile_merger import ProfileMerger
from src.projection.projector import ProjectionLayer
from src.validation.validator import validate_canonical_profile
from src.schemas.canonical import CandidateProfile, LocationDetails, FieldProvenance

# 1. Phone Normalization Tests
def test_phone_normalization():
    assert normalize_phone("+1 555-555-5555") == "+15555555555"
    assert normalize_phone("555-555-5555", default_region="US") == "+15555555555"
    assert normalize_phone("invalid_phone_number") is None
    assert normalize_phone("") is None

# 2. Date Normalization Tests
def test_date_normalization():
    assert normalize_date("Jan 2020") == "2020-01"
    assert normalize_date("2020/05/12") == "2020-05"
    assert normalize_date("2021") == "2021-01"
    assert normalize_date("Present") == "Present"
    assert normalize_date("current") == "Present"
    assert normalize_date("now") == "Present"
    assert normalize_date("invalid-date-string") is None

# 3. Skill Normalization Tests
def test_skill_normalization():
    assert normalize_skill("C Plus Plus") == "C++"
    assert normalize_skill("cpp") == "C++"
    assert normalize_skill("C++") == "C++"
    assert normalize_skill("javascript") == "JavaScript"
    assert normalize_skill("JS") == "JavaScript"
    assert normalize_skill("nodejs") == "Node.js"
    assert normalize_skill("ReactJS") == "React"
    assert normalize_skill("Python") == "Python"
    assert normalize_skill("kubernetes") == "Kubernetes"
    # Fallback to Title case for unknown skills
    assert normalize_skill("some novel tech skill") == "Some Novel Tech Skill"

def test_skills_list_normalization():
    raw_skills = ["cpp", "Python", "JS", "ReactJS", "python", "C++"]
    normalized = normalize_skills(raw_skills)
    # Deduplicated and canonicalized: C++, Python, JavaScript, React
    assert len(normalized) == 4
    assert "C++" in normalized
    assert "Python" in normalized
    assert "JavaScript" in normalized
    assert "React" in normalized

# 4. Conflict Resolution & Merging Tests
def test_conflict_resolution():
    profile_pdf = {
        "source_file": "resume.pdf",
        "full_name": "Alex Mercer",
        "headline": "Senior Staff Software Engineer",
        "location": "San Francisco, USA",
        "emails": ["alex.mercer@email.com"],
        "phones": ["+15555555555"],
        "skills": ["C++", "Python"],
        "experience": [],
        "education": []
    }
    profile_csv = {
        "source_file": "recruiter.csv",
        "full_name": "Alex M.",
        "headline": "Staff Software Engineer",
        "location": "SF, CA",
        "emails": ["alex.mercer@email.com"],
        "phones": ["555-555-5555"],
        "skills": ["Python", "React"],
        "experience": [],
        "education": []
    }
    
    merger = ProfileMerger()
    merged = merger.merge_profiles([profile_pdf, profile_csv])
    
    # PDF values should win for single fields
    assert merged.full_name == "Alex Mercer"
    assert merged.headline == "Senior Staff Software Engineer"
    assert merged.location.raw == "San Francisco, USA"
    assert merged.location.country_code == "US"
    
    # Emails and phones should union (and phones normalize)
    assert "alex.mercer@email.com" in merged.emails
    assert "+15555555555" in merged.phones
    
    # Provenance check
    full_name_prov = next((p for p in merged.provenance if p.field == "full_name"), None)
    assert full_name_prov is not None
    assert full_name_prov.source == "resume.pdf"
    assert full_name_prov.method == "heuristic"
    
    # Confidence scoring verification
    assert merged.overall_confidence >= 0.70
    assert merged.field_confidence["full_name"] == 0.60  # heuristic on pdf
    assert merged.field_confidence["emails"] == 0.80      # regex email

# 5. Projection Layer Tests
def test_projection_layer():
    profile = CandidateProfile(
        candidate_id="123",
        full_name="Alex Mercer",
        emails=["alex@email.com"],
        phones=["+15555555555"],
        location=LocationDetails(raw="San Francisco, US", country_code="US"),
        links={"linkedin": "https://linkedin.com/in/alexmercer"},
        skills=["Python", "C++"],
        overall_confidence=0.85
    )
    
    config = {
        "include_fields": ["name", "emails", "overall_confidence"],
        "rename_fields": {
            "full_name": "name"
        },
        "include_confidence": True,
        "include_provenance": False,
        "missing_value_behavior": "null"
    }
    
    projector = ProjectionLayer(config)
    projected = projector.project(profile)
    
    # Check that rename succeeded
    assert "name" in projected
    assert projected["name"] == "Alex Mercer"
    assert "full_name" not in projected
    
    # Check inclusions/exclusions
    assert "emails" in projected
    assert "overall_confidence" in projected
    assert "phones" not in projected
    assert "skills" not in projected
    assert "provenance" not in projected

# 6. Missing Values Tests
def test_missing_values_behavior():
    profile = CandidateProfile(
        candidate_id="123",
        full_name="Alex Mercer",
        emails=["alex@email.com"],
        headline=None,  # missing field
        skills=[]       # empty list
    )
    
    # Scenario A: Behavior is "null" (keep keys, set to null/empty)
    config_null = {
        "include_fields": ["candidate_id", "full_name", "headline", "skills"],
        "missing_value_behavior": "null"
    }
    projected_null = ProjectionLayer(config_null).project(profile)
    assert "headline" in projected_null
    assert projected_null["headline"] is None
    assert "skills" in projected_null
    assert projected_null["skills"] == []
    
    # Scenario B: Behavior is "exclude" (remove empty/null keys)
    config_exclude = {
        "include_fields": ["candidate_id", "full_name", "headline", "skills"],
        "missing_value_behavior": "exclude"
    }
    projected_exclude = ProjectionLayer(config_exclude).project(profile)
    assert "headline" not in projected_exclude
    assert "skills" not in projected_exclude
    assert projected_exclude["full_name"] == "Alex Mercer"

# 7. Malformed Inputs Tests
def test_malformed_input():
    from src.parsers.csv_parser import CSVParser
    from src.parsers.pdf_parser import PDFParser
    
    csv_parser = CSVParser()
    pdf_parser = PDFParser()
    
    # Running parser on non-existent files should raise ValueError
    with pytest.raises(ValueError):
        csv_parser.parse("non_existent_file.csv")
        
    with pytest.raises(ValueError):
        pdf_parser.parse("non_existent_file.pdf")

# 8. Duplicate Candidate Tests
def test_duplicate_candidate():
    profile_csv_1 = {
        "source_file": "recruiter_1.csv",
        "full_name": "Alex Mercer",
        "emails": ["alex.mercer@email.com"],
        "skills": ["Python", "Django"],
        "experience": [],
        "education": []
    }
    profile_csv_2 = {
        "source_file": "recruiter_2.csv",
        "full_name": "Alex Mercer",
        "emails": ["alex.mercer@email.com"],
        "skills": ["Python", "Flask"],
        "experience": [],
        "education": []
    }
    
    merger = ProfileMerger()
    merged = merger.merge_profiles([profile_csv_1, profile_csv_2])
    
    # Verify candidate lists are unioned and deduplicated
    assert "Python" in merged.skills
    assert "Django" in merged.skills
    assert "Flask" in merged.skills
    assert len(merged.skills) == 3
