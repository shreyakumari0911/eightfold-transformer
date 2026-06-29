from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FieldProvenance(BaseModel):
    field: str
    source: str
    method: str
    value: Any = None

class ExperienceItem(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None  # Format: YYYY-MM
    end_date: Optional[str] = None    # Format: YYYY-MM or "Present"
    description: Optional[str] = None

class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None  # Format: YYYY-MM
    end_date: Optional[str] = None    # Format: YYYY-MM

class CandidateProfile(BaseModel):
    candidate_id: str
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    provenance: Dict[str, FieldProvenance] = Field(default_factory=dict)
    field_confidence: Dict[str, float] = Field(default_factory=dict)
    overall_confidence: float = 0.0
