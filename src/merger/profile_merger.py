from typing import List, Dict, Any, Optional
from src.schemas.canonical import CandidateProfile, ExperienceItem, EducationItem, FieldProvenance
from src.confidence.scoring import calculate_field_confidence, calculate_overall_confidence
import uuid

class ProfileMerger:
    """
    Deterministically merges candidate profile records from multiple sources.
    Resolves conflicts based on source priority (e.g., Resume > Recruiter CSV).
    Tracks provenance and computes field/overall confidence scores.
    """
    
    def __init__(self, priority_map: Optional[Dict[str, int]] = None):
        # Default priority map: Resume (PDF) > Recruiter CSV
        self.priority_map = priority_map or {
            "pdf": 2,
            "csv": 1,
            "json": 1,
            "unknown": 0
        }
        
    def get_source_priority(self, source_file: str) -> int:
        """
        Determines the priority of a source based on its filename/extension.
        """
        source_lower = source_file.lower()
        if source_lower.endswith(".pdf"):
            return self.priority_map.get("pdf", 2)
        elif source_lower.endswith(".csv"):
            return self.priority_map.get("csv", 1)
        elif source_lower.endswith(".json"):
            return self.priority_map.get("json", 1)
        return self.priority_map.get("unknown", 0)

    def merge_profiles(self, normalized_profiles: List[Dict[str, Any]]) -> CandidateProfile:
        """
        Merges a list of normalized candidate profile dicts into a single canonical CandidateProfile.
        Assumes all input profiles belong to the same candidate.
        """
        if not normalized_profiles:
            raise ValueError("Cannot merge an empty list of profiles.")
            
        # Determine candidate ID: we can hash or use a deterministic candidate ID if present,
        # or generate a UUID if none is found. Let's look for candidate_id in inputs.
        candidate_id = None
        for p in normalized_profiles:
            if p.get("candidate_id"):
                candidate_id = p["candidate_id"]
                break
        if not candidate_id:
            candidate_id = str(uuid.uuid4())
            
        # Sort profiles by priority ascending (so higher priority overwrites during loop)
        # or handle conflicts explicitly. Let's do explicit conflict handling.
        
        # Initialize fields
        merged_name = None
        merged_location = None
        merged_headline = None
        merged_years_exp = None
        
        # Provenance trackers
        provenance: Dict[str, FieldProvenance] = {}
        field_confidence: Dict[str, float] = {}
        
        # Track winning source details for single fields
        single_fields = ["full_name", "location", "headline", "years_experience"]
        winning_sources: Dict[str, Dict[str, Any]] = {}
        
        for field in single_fields:
            winner_val = None
            winner_priority = -1
            winner_source = None
            winner_method = None
            
            for profile in normalized_profiles:
                val = profile.get(field)
                if val is not None and val != "":
                    source = profile.get("source_file", "unknown")
                    priority = self.get_source_priority(source)
                    # Heuristic to determine the method
                    method = "direct_resume" if source.endswith(".pdf") else "csv_direct"
                    if field == "years_experience" and source.endswith(".pdf"):
                        method = "heuristic" # YOE was calculated via heuristics
                    elif field in ["full_name", "headline", "location"] and source.endswith(".pdf"):
                        method = "heuristic"
                        
                    # If this source has higher priority, it wins
                    if priority > winner_priority:
                        winner_val = val
                        winner_priority = priority
                        winner_source = source
                        winner_method = method
                        
            if winner_val is not None:
                winning_sources[field] = {
                    "val": winner_val,
                    "source": winner_source,
                    "method": winner_method
                }
                provenance[field] = FieldProvenance(
                    field=field,
                    source=winner_source,
                    method=winner_method,
                    value=winner_val
                )
                field_confidence[field] = calculate_field_confidence(winner_source, winner_method)
            else:
                provenance[field] = FieldProvenance(field=field, source="N/A", method="N/A", value=None)
                
        # Merge lists (emails, phones, links, skills) - union them
        emails_union: List[str] = []
        phones_union: List[str] = []
        links_union: List[str] = []
        skills_union: List[str] = []
        
        email_sources = []
        phone_sources = []
        link_sources = []
        skill_sources = []
        
        for profile in normalized_profiles:
            source = profile.get("source_file", "unknown")
            method = "regex" if source.endswith(".pdf") else "csv_direct"
            
            # Emails
            for email in profile.get("emails", []):
                if email not in emails_union:
                    emails_union.append(email)
                    email_sources.append((source, method))
            # Phones
            for phone in profile.get("phones", []):
                if phone not in phones_union:
                    phones_union.append(phone)
                    phone_sources.append((source, method))
            # Links
            for link in profile.get("links", []):
                if link not in links_union:
                    links_union.append(link)
                    link_sources.append((source, method))
            # Skills
            for skill in profile.get("skills", []):
                if skill not in skills_union:
                    skills_union.append(skill)
                    skill_sources.append((source, method))
                    
        # For array fields, provenance is recorded with the primary contributing source
        # or a combination. Let's record provenance mapping to the highest priority contributor.
        for field, union_list, sources_list in [
            ("emails", emails_union, email_sources),
            ("phones", phones_union, phone_sources),
            ("links", links_union, link_sources),
            ("skills", skills_union, skill_sources)
        ]:
            if union_list:
                # Find highest priority source among contributors
                best_source = "unknown"
                best_method = "unknown"
                best_priority = -1
                for src, meth in sources_list:
                    prio = self.get_source_priority(src)
                    if prio > best_priority:
                        best_priority = prio
                        best_source = src
                        best_method = meth
                        
                provenance[field] = FieldProvenance(
                    field=field,
                    source=best_source,
                    method=best_method,
                    value=union_list
                )
                field_confidence[field] = calculate_field_confidence(best_source, best_method)
            else:
                provenance[field] = FieldProvenance(field=field, source="N/A", method="N/A", value=[])
                
        # Merge experience (deduplicate jobs by company + job_title + approximate dates)
        merged_experience = self._merge_experience(normalized_profiles)
        if merged_experience:
            # Experience provenance based on highest priority contributor
            best_source = "unknown"
            best_priority = -1
            for profile in normalized_profiles:
                if profile.get("experience"):
                    src = profile.get("source_file", "unknown")
                    prio = self.get_source_priority(src)
                    if prio > best_priority:
                        best_priority = prio
                        best_source = src
            provenance["experience"] = FieldProvenance(
                field="experience",
                source=best_source,
                method="heuristic_parsing" if best_source.endswith(".pdf") else "csv_direct",
                value=merged_experience
            )
            field_confidence["experience"] = calculate_field_confidence(best_source, "heuristic" if best_source.endswith(".pdf") else "csv_direct")
        else:
            provenance["experience"] = FieldProvenance(field="experience", source="N/A", method="N/A", value=[])
            
        # Merge education (deduplicate by degree + institution)
        merged_education = self._merge_education(normalized_profiles)
        if merged_education:
            best_source = "unknown"
            best_priority = -1
            for profile in normalized_profiles:
                if profile.get("education"):
                    src = profile.get("source_file", "unknown")
                    prio = self.get_source_priority(src)
                    if prio > best_priority:
                        best_priority = prio
                        best_source = src
            provenance["education"] = FieldProvenance(
                field="education",
                source=best_source,
                method="heuristic_parsing" if best_source.endswith(".pdf") else "csv_direct",
                value=merged_education
            )
            field_confidence["education"] = calculate_field_confidence(best_source, "heuristic" if best_source.endswith(".pdf") else "csv_direct")
        else:
            provenance["education"] = FieldProvenance(field="education", source="N/A", method="N/A", value=[])
            
        # Compute location details
        winner_loc_str = winning_sources.get("location", {}).get("val")
        location_obj = None
        if winner_loc_str:
            from src.normalizers.country import normalize_country
            from src.schemas.canonical import LocationDetails
            country = normalize_country(winner_loc_str)
            
            # List of US states & abbreviations
            US_STATES = {
                "ca", "ny", "tx", "wa", "ma", "il", "fl", "pa", "oh", "ga", "nc", "mi", "va", "nj",
                "california", "new york", "texas", "washington", "massachusetts", "illinois",
                "florida", "pennsylvania", "ohio", "georgia", "north carolina", "michigan", "virginia", "new jersey"
            }
            
            city = None
            region = None
            parts = [p.strip() for p in winner_loc_str.split(",")]
            if len(parts) >= 3:
                city = parts[0]
                region = parts[1]
            elif len(parts) == 2:
                city = parts[0]
                region = parts[1]
                part_lower = parts[1].lower()
                if part_lower in US_STATES:
                    country = "US"
                else:
                    resolved_country_part = normalize_country(parts[1])
                    if resolved_country_part and resolved_country_part == country:
                        region = None
            elif len(parts) == 1:
                resolved_country_part = normalize_country(parts[0])
                if resolved_country_part:
                    country = resolved_country_part
                else:
                    city = parts[0]
                    
            location_obj = LocationDetails(city=city, region=region, country=country)
            
        # Compute links details object
        linkedin = None
        github = None
        portfolio = None
        other = []
        for link in links_union:
            link_lower = link.lower()
            if "linkedin.com" in link_lower:
                linkedin = link
            elif "github.com" in link_lower:
                github = link
            elif any(k in link_lower for k in ["portfolio", "personal", "website"]):
                portfolio = link
            else:
                other.append(link)
                
        from src.schemas.canonical import LinkDetails
        links_obj = LinkDetails(
            linkedin=linkedin,
            github=github,
            portfolio=portfolio,
            other=other
        )

        # Compute overall confidence
        overall_confidence = calculate_overall_confidence(field_confidence)
        
        # Instantiate and return canonical CandidateProfile
        return CandidateProfile(
            candidate_id=candidate_id,
            full_name=winning_sources.get("full_name", {}).get("val"),
            emails=emails_union,
            phones=phones_union,
            location=location_obj,
            links=links_obj,
            headline=winning_sources.get("headline", {}).get("val"),
            years_experience=winning_sources.get("years_experience", {}).get("val"),
            skills=skills_union,
            experience=[ExperienceItem(**job) for job in merged_experience],
            education=[EducationItem(**edu) for edu in merged_education],
            provenance=list(provenance.values()),
            field_confidence=field_confidence,
            overall_confidence=overall_confidence
        )
        
    def _merge_experience(self, normalized_profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merges work experience items, deduplicating records from multiple sources.
        """
        all_jobs: List[Dict[str, Any]] = []
        for profile in normalized_profiles:
            source = profile.get("source_file", "unknown")
            priority = self.get_source_priority(source)
            for job in profile.get("experience", []):
                # Copy and annotate with source priority for comparison
                job_copy = job.copy()
                job_copy["_priority"] = priority
                all_jobs.append(job_copy)
                
        if not all_jobs:
            return []
            
        # Deduplication logic
        merged: List[Dict[str, Any]] = []
        for job in all_jobs:
            # Look for duplicate in merged
            duplicate_found = False
            for existing in merged:
                # Same company (fuzzy match) and either same job title or date overlap
                co_match = self._is_same_company(job.get("company"), existing.get("company"))
                title_match = self._is_same_title(job.get("job_title"), existing.get("job_title"))
                
                if co_match and (title_match or job.get("start_date") == existing.get("start_date")):
                    duplicate_found = True
                    # Keep the one with higher priority
                    if job["_priority"] > existing["_priority"]:
                        # Merge text fields if missing in winner
                        for k in ["job_title", "company", "start_date", "end_date", "description"]:
                            if job.get(k):
                                existing[k] = job[k]
                        existing["_priority"] = job["_priority"]
                    else:
                        # Winner is existing, but update missing values from job if needed
                        for k in ["job_title", "company", "start_date", "end_date", "description"]:
                            if not existing.get(k) and job.get(k):
                                existing[k] = job[k]
                    break
            if not duplicate_found:
                merged.append(job)
                
        # Clean private annotations
        for m in merged:
            m.pop("_priority", None)
            
        # Sort by start date descending
        def sort_key(x):
            start = x.get("start_date")
            return start if start else "0000-00"
            
        merged.sort(key=sort_key, reverse=True)
        return merged
        
    def _merge_education(self, normalized_profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merges education records, deduplicating records.
        """
        all_edu: List[Dict[str, Any]] = []
        for profile in normalized_profiles:
            source = profile.get("source_file", "unknown")
            priority = self.get_source_priority(source)
            for edu in profile.get("education", []):
                edu_copy = edu.copy()
                edu_copy["_priority"] = priority
                all_edu.append(edu_copy)
                
        if not all_edu:
            return []
            
        merged: List[Dict[str, Any]] = []
        for edu in all_edu:
            duplicate_found = False
            for existing in merged:
                inst_match = self._is_same_institution(edu.get("institution"), existing.get("institution"))
                deg_match = self._is_same_degree(edu.get("degree"), existing.get("degree"))
                
                if inst_match and (deg_match or edu.get("start_date") == existing.get("start_date")):
                    duplicate_found = True
                    if edu["_priority"] > existing["_priority"]:
                        for k in ["degree", "institution", "field_of_study", "start_date", "end_date"]:
                            if edu.get(k):
                                existing[k] = edu[k]
                        existing["_priority"] = edu["_priority"]
                    else:
                        for k in ["degree", "institution", "field_of_study", "start_date", "end_date"]:
                            if not existing.get(k) and edu.get(k):
                                existing[k] = edu[k]
                    break
            if not duplicate_found:
                merged.append(edu)
                
        for m in merged:
            m.pop("_priority", None)
            
        # Sort by start date descending
        def sort_key(x):
            start = x.get("start_date")
            return start if start else "0000-00"
            
        merged.sort(key=sort_key, reverse=True)
        return merged

    # Helper helper checks for fuzzy matching duplicates
    def _is_same_company(self, co1: Optional[str], co2: Optional[str]) -> bool:
        if not co1 or not co2:
            return False
        c1, c2 = co1.lower().strip(), co2.lower().strip()
        # Remove common business suffixes
        for suffix in [" inc", " corp", " co", " ltd", " corporation", " limited"]:
            c1 = c1.replace(suffix, "")
            c2 = c2.replace(suffix, "")
        return c1 == c2 or c1 in c2 or c2 in c1
        
    def _is_same_title(self, t1: Optional[str], t2: Optional[str]) -> bool:
        if not t1 or not t2:
            return False
        return t1.lower().strip() == t2.lower().strip()
        
    def _is_same_institution(self, inst1: Optional[str], inst2: Optional[str]) -> bool:
        if not inst1 or not inst2:
            return False
        i1, i2 = inst1.lower().strip(), inst2.lower().strip()
        return i1 == i2 or i1 in i2 or i2 in i1
        
    def _is_same_degree(self, d1: Optional[str], d2: Optional[str]) -> bool:
        if not d1 or not d2:
            return False
        # Normalize degrees for simple check (e.g. BS, Bachelor, B.S.)
        def clean_deg(d):
            d_clean = d.lower().replace(".", "").replace("s", "").replace("r", "") # bs / ba / MS -> b / m
            if "bachelor" in d_clean: return "b"
            if "master" in d_clean: return "m"
            if "doctor" in d_clean or "phd" in d_clean: return "phd"
            return d_clean
        return clean_deg(d1) == clean_deg(d2)
