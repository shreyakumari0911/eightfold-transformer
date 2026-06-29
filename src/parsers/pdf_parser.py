import pdfplumber
import re
from typing import Dict, Any, List, Optional
from src.parsers.base import BaseParser
import datetime

class PDFParser(BaseParser):
    """
    Parses candidate resume PDFs.
    Uses pdfplumber to extract text, followed by rule-based regex and heuristic
    extractors to populate the candidate fields.
    """
    
    # Regex patterns
    EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
    PHONE_REGEX = re.compile(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    )
    LINK_REGEX = re.compile(
        r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*'
    )
    # Common date range formats: "Jan 2018 - Present", "08/2015 - 12/2019", "2010 to 2012", etc.
    DATE_RANGE_REGEX = re.compile(
        r'\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2})?[-/\s]*\d{4}\s*(?:-|to|–|—)\s*(?:present|current|now|(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\d{1,2})?[-/\s]*\d{4})\b',
        re.IGNORECASE
    )
    
    # Skills list to scan for (common keywords in tech)
    COMMON_TECH_SKILLS = [
        "python", "javascript", "typescript", "c++", "cpp", "c plus plus", "c#", "csharp",
        "java", "go", "golang", "ruby", "php", "swift", "rust", "scala", "kotlin",
        "html", "css", "html5", "css3", "sass", "less",
        "react", "reactjs", "react.js", "angular", "vue", "vuejs", "svelte", "nextjs",
        "node", "nodejs", "node.js", "express", "django", "flask", "fastapi", "spring", "rails",
        "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "ansible",
        "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch",
        "git", "github", "gitlab", "ci/cd", "jenkins", "graphql", "rest api", "restful",
        "scrum", "agile", "jira", "machine learning", "ml", "deep learning", "nlp", "ai"
    ]
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses a PDF resume file and returns a dictionary of extracted raw fields.
        """
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Failed to read PDF file {file_path}: {str(e)}")
            
        if not text.strip():
            raise ValueError(f"No text extracted from PDF file {file_path}")
            
        raw_data = self._extract_fields_from_text(text)
        raw_data["source_file"] = file_path
        return raw_data
        
    def _extract_fields_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extracts candidate fields from raw text using regex and heuristics.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Extract Name
        # Heuristic: First short line that doesn't look like an email/phone/link/header
        full_name = None
        for line in lines[:5]:
            words = line.split()
            # Checks: word count 2-4, no digits, no @, not containing common noise
            if 2 <= len(words) <= 4 and not any(char.isdigit() for char in line):
                if "@" not in line and not any(k in line.lower() for k in ["resume", "cv", "page", "summary", "contact"]):
                    full_name = line
                    break
        
        # 2. Extract Emails
        emails = self.EMAIL_REGEX.findall(text)
        emails = list(dict.fromkeys([e.lower() for e in emails]))  # deduplicate
        
        # 3. Extract Phones
        phones = self.PHONE_REGEX.findall(text)
        phones = list(dict.fromkeys([p.strip() for p in phones]))
        
        # 4. Extract Links
        links = self.LINK_REGEX.findall(text)
        # Filter for typical relevant links (github, linkedin, portfolio, personal sites)
        links = [l for l in links if any(k in l.lower() for k in ["linkedin", "github", "portfolio", "git", "personal", "cv", "resume"]) or len(l) < 100]
        links = list(dict.fromkeys(links))
        
        # 5. Headline
        # Heuristic: Second line if name was first, or first line below name that is short
        headline = None
        if full_name and full_name in lines:
            idx = lines.index(full_name)
            if idx + 1 < len(lines):
                candidate_hl = lines[idx + 1]
                if len(candidate_hl.split()) <= 6 and not any(k in candidate_hl.lower() for k in ["email", "phone", "contact", "address", "http"]):
                    headline = candidate_hl
                    
        # 6. Extract Location
        # Heuristic: Scan lines around contact details or search for specific city patterns
        location = self._heuristic_extract_location(lines)
        
        # 7. Extract Skills
        skills = self._heuristic_extract_skills(text)
        
        # 8. Extract Experience & Education Sections
        experience = self._extract_experience(text)
        education = self._extract_education(text)
        
        # 9. Compute Years of Experience based on parsed job date ranges
        years_experience = self._calculate_years_experience(experience)
        
        return {
            "full_name": full_name,
            "emails": emails,
            "phones": phones,
            "links": links,
            "headline": headline,
            "location": location,
            "skills": skills,
            "experience": experience,
            "education": education,
            "years_experience": years_experience
        }
        
    def _heuristic_extract_location(self, lines: List[str]) -> Optional[str]:
        """
        Attempts to locate a location string from candidate header lines.
        """
        # Look for patterns like "City, State", "City, Country"
        location_pattern = re.compile(r'^[a-zA-Z\s\.\'-]+,\s*[a-zA-Z\s\.\'-]{2,}(?:,\s*[a-zA-Z\s\.\'-]+)?$')
        
        # Scan first 10 lines
        for line in lines[:10]:
            if "@" in line or any(k in line.lower() for k in ["phone", "http", "www", "github", "linkedin"]):
                continue
            if location_pattern.match(line):
                return line
        return None
        
    def _heuristic_extract_skills(self, text: str) -> List[str]:
        """
        Scans resume text for common technical keywords.
        Also attempts to extract comma-separated items from a designated 'Skills' section.
        """
        skills_found = []
        text_lower = text.lower()
        
        # Try finding a skills section
        skills_section_match = re.search(
            r'(?:skills|technical skills|skills & expertise|expertise|technologies)(?:\s*:|\n)(.*?)(?:\n\n|\n[A-Z][a-z]+|\Z)',
            text_lower,
            re.DOTALL
        )
        if skills_section_match:
            section_text = skills_section_match.group(1)
            # Split by commas, semicolons, bullets
            items = re.split(r'[,;•\n|]', section_text)
            for item in items:
                cleaned_item = item.strip()
                if cleaned_item and len(cleaned_item) < 30 and not any(x in cleaned_item for x in ["experience", "years", "using", "advanced"]):
                    skills_found.append(cleaned_item)
                    
        # Supplement with standard tech keyword scanning (to be safe)
        for skill in self.COMMON_TECH_SKILLS:
            # Word boundary check, escaping special chars like c++
            pattern = r'\b' + re.escape(skill) + r'\b'
            if skill in ["c++", "c#", "node.js", "react.js"]:
                pattern = re.escape(skill)
            if re.search(pattern, text_lower):
                # Find original case match from list if possible
                skills_found.append(skill)
                
        # Unique list, keeping order
        seen = set()
        unique_skills = []
        for s in skills_found:
            s_lower = s.lower()
            if s_lower not in seen:
                seen.add(s_lower)
                # Map to proper casing
                unique_skills.append(s)
                
        return unique_skills
        
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts work experience records from the resume.
        Splits by experience section header and parses job segments.
        """
        text_lines = text.split("\n")
        exp_start = -1
        exp_end = len(text_lines)
        
        # Find start of Experience section
        for i, line in enumerate(text_lines):
            line_clean = line.strip().lower()
            if line_clean in ["experience", "work experience", "professional experience", "employment history", "employment"]:
                exp_start = i
                break
                
        if exp_start == -1:
            return []
            
        # Find next section to mark end of experience
        for i in range(exp_start + 1, len(text_lines)):
            line_clean = text_lines[i].strip().lower()
            if line_clean in ["education", "academic background", "skills", "projects", "certifications", "interests"]:
                exp_end = i
                break
                
        exp_lines = text_lines[exp_start + 1:exp_end]
        exp_text = "\n".join(exp_lines)
        
        # Split by jobs using date range matches as anchors
        jobs: List[Dict[str, Any]] = []
        date_ranges = list(self.DATE_RANGE_REGEX.finditer(exp_text))
        
        if not date_ranges:
            return []
            
        for idx, match in enumerate(date_ranges):
            start_pos = match.start()
            # The job ends where the next job's date range begins, or at the end of the text
            end_pos = date_ranges[idx + 1].start() if idx + 1 < len(date_ranges) else len(exp_text)
            
            job_segment = exp_text[start_pos:end_pos].strip()
            # The line containing the date range and lines immediately surrounding it
            segment_lines = [l.strip() for l in job_segment.split("\n") if l.strip()]
            
            if not segment_lines:
                continue
                
            date_str = match.group(0)
            
            # The rest of the job description is everything below the first 1-2 lines of the segment
            description = "\n".join(segment_lines[1:]) if len(segment_lines) > 1 else None
            
            # Heuristic for Job Title and Company
            # Look at the first line of the segment or the line just before the date range in exp_text
            # In job_segment, the date string is on the first line. Let's parse that line.
            header_line = segment_lines[0]
            # Strip the date range from header_line
            info_part = header_line.replace(date_str, "").strip()
            # If info_part is empty, check if we can look at the text before the match
            if not info_part:
                # Find lines preceding this date range match in exp_text (max 2 lines)
                before_text = exp_text[:start_pos].strip()
                before_lines = [l.strip() for l in before_text.split("\n") if l.strip()]
                if before_lines:
                    info_part = before_lines[-1]
            
            # Split info_part into job_title and company
            job_title = None
            company = None
            if info_part:
                # Typical delimiters: "at", "@", "|", ",", "-"
                split_patterns = [r'\bat\b', r'@', r'\|', r',', r'-']
                split_match = None
                for pat in split_patterns:
                    match_split = re.search(pat, info_part, re.IGNORECASE)
                    if match_split:
                        split_match = match_split
                        break
                if split_match:
                    left = info_part[:split_match.start()].strip()
                    right = info_part[split_match.end():].strip()
                    job_title = left
                    company = right
                else:
                    words = info_part.split()
                    if len(words) > 2:
                        job_title = " ".join(words[:len(words)//2])
                        company = " ".join(words[len(words)//2:])
                    else:
                        job_title = info_part
            
            # Separate start and end date
            dates = [d.strip() for d in re.split(r'-|to|–|—', date_str, flags=re.IGNORECASE)]
            start_date = dates[0] if len(dates) > 0 else None
            end_date = dates[1] if len(dates) > 1 else None
            
            jobs.append({
                "job_title": job_title,
                "company": company,
                "start_date": start_date,
                "end_date": end_date,
                "description": description
            })
            
        return jobs
        
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts education records from the resume.
        Splits by education section header and parses educational segments.
        """
        text_lines = text.split("\n")
        edu_start = -1
        edu_end = len(text_lines)
        
        # Find start of Education section
        for i, line in enumerate(text_lines):
            line_clean = line.strip().lower()
            if line_clean in ["education", "academic background", "academics", "academic credentials"]:
                edu_start = i
                break
                
        if edu_start == -1:
            return []
            
        # Find next section to mark end of education
        for i in range(edu_start + 1, len(text_lines)):
            line_clean = text_lines[i].strip().lower()
            if line_clean in ["experience", "work experience", "skills", "projects", "certifications"]:
                edu_end = i
                break
                
        edu_lines = text_lines[edu_start + 1:edu_end]
        edu_text = "\n".join(edu_lines)
        edu_segments = [s.strip() for s in edu_text.split("\n\n") if s.strip()]
        
        education_items = []
        
        # Degree regex mapping
        degree_patterns = [
            r'\b(?:B\.?S\.?|B\.?A\.?|Bachelor[s]?)\b',
            r'\b(M\.?S\.?|M\.?A\.?|Master[s]?)\b',
            r'\b(?:Ph\.?D\.?|Doctorate)\b',
            r'\b(?:Associate[s]? Degree|B\.?Tech|M\.?Tech|Diploma)\b'
        ]
        
        for segment in edu_segments:
            lines = [l.strip() for l in segment.split("\n") if l.strip()]
            if not lines:
                continue
                
            first_line = lines[0]
            
            # Find degree in first/second line
            degree = None
            for pat in degree_patterns:
                match = re.search(pat, segment, re.IGNORECASE)
                if match:
                    degree = match.group(0)
                    break
                    
            # Heuristic for institution and field of study
            institution = None
            field_of_study = None
            
            # Match date in segment
            dates_found = re.findall(r'\b\d{4}\b', segment)
            start_date = dates_found[0] + "-01" if len(dates_found) > 0 else None
            end_date = dates_found[1] + "-01" if len(dates_found) > 1 else (dates_found[0] + "-01" if len(dates_found) > 0 else None)
            
            # Institution name heuristic (lines containing "University", "College", "School", "Institute")
            for line in lines:
                if any(x in line.lower() for x in ["university", "college", "school", "institute", "academy"]):
                    institution = line
                    break
            
            if not institution and lines:
                institution = lines[0]
                
            # Field of study heuristic (lines containing "in ", "Major: ", "Field: ", "specialization ")
            field_match = re.search(r'(?:in|major in|major:)\s+([a-zA-Z\s&]+)', segment, re.IGNORECASE)
            if field_match:
                field_of_study = field_match.group(1).strip()
            
            education_items.append({
                "degree": degree,
                "institution": institution,
                "field_of_study": field_of_study,
                "start_date": start_date,
                "end_date": end_date
            })
            
        return education_items
        
    def _calculate_years_experience(self, experience: List[Dict[str, Any]]) -> float:
        """
        Heuristic: Sums the durations of all parsed job experiences.
        """
        total_months = 0
        from src.normalizers.date import normalize_date
        
        for job in experience:
            start_str = normalize_date(job.get("start_date"))
            end_str = normalize_date(job.get("end_date"))
            
            if not start_str:
                continue
                
            try:
                start_yr, start_mo = map(int, start_str.split("-"))
                
                if not end_str or end_str == "Present":
                    now = datetime.datetime.now()
                    end_yr, end_mo = now.year, now.month
                else:
                    end_yr, end_mo = map(int, end_str.split("-"))
                    
                months = (end_yr - start_yr) * 12 + (end_mo - start_mo)
                if months > 0:
                    total_months += months
            except Exception:
                pass
                
        years = total_months / 12.0
        return round(years, 1)
