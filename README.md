# Multi-Source Candidate Data Transformer

A production-grade Python solution to ingest, parse, normalize, merge, and resolve conflicts from multiple candidate data sources (such as Recruiter CSV files and Resume PDFs) into a canonical candidate profile. Decoupled using clean architecture principles, it incorporates confidence scoring, provenance tracking, dynamic projection, and schema validation.

---

## Architecture Overview

The system implements the **Canonical Pipeline** pattern and is decoupled into isolated modules following SOLID principles:

```
Input File(s)
    ↓
Parser/Extractor (PDF/CSV) -> Raw extracted key-value dictionaries
    ↓
Normalizer (Phone to E.164, Date to YYYY-MM, Country to ISO-3166, Skills Canonical Map)
    ↓
Merger (Combines multiple profiles, handles conflicts using Precedence Rules)
    ↓
Confidence & Provenance Engine (Explainable scoring, tracks field-level extraction lineage)
    ↓
Projection Layer (Dynamic runtime schema restructuring)
    ↓
Schema Validation (Validates schemas via Pydantic)
    ↓
Output JSON File
```

### Folder Structure
```
eightfold/
├── src/
│   ├── confidence/       # Field and overall confidence scoring models
│   ├── merger/           # Profile merging and conflict resolution logic
│   ├── normalizers/      # Phone, date, country, and skill normalizers
│   ├── parsers/          # Base, CSV, and PDF parsed text readers
│   ├── projection/       # Configurable runtime output formatter
│   ├── schemas/          # Pydantic schema schemas
│   ├── tests/            # Pytest test suite
│   └── validation/       # Schema validators
├── sample_data/          # Subdirectory containing generated mock data
├── generate_pdf.py       # Script to generate the Technical Design PDF
├── generate_sample_data.py # Script to prepare mock input files
├── main.py               # Main CLI Pipeline entry point
├── requirements.txt      # Project library dependencies list
├── README.md             # Project documentation
└── config.json           # Sample runtime projection config
```

---

## Design Decisions, Tradeoffs & Assumptions

### Design Decisions
- **Deterministic Precedence Merger:** Resume PDF data is prioritized over recruiter-filled CSV details, as candidates author their resumes, while recruiter records are susceptible to transcription errors.
- **Possible Number Validation Fallback:** Fictitious numbers (e.g. 555-0199) fail strict telecoms-plan carrier checks in Google `phonenumbers`. The phone normalizer falls back to `is_possible_number` formatting, preserving mock numbers while enforcing strict validation on real numbers.
- **Fuzzy Skill Merging:** Implemented combining exact matching with fuzzy similarity lookups (`rapidfuzz`) to automatically map syntax variants ("cpp", "C Plus Plus" → "C++").
- **Structured Location & Link Mapping:** Resolves raw location tokens into distinct fields (`city`, `region`, `country`) and partitions extracted link URLs into structured dictionary platforms (`linkedin`, `github`, `portfolio`, `other`).

### Tradeoffs
- **Rule-based PDF Text Parsing vs. LLM Extractors:**
  - *Tradeoff:* Written using deterministic regex and heuristic layout anchors to extract names, experiences, education, and dates. While LLMs (like GPT-4/Claude) excel at extracting unstructured text, rule-based extraction guarantees local execution, 100% determinism, speed, and no external API key dependency.
- **Flat List unioning:** Emails, phones, and skills are unioned across sources. While this maximizes data recovery, it assumes all details pertain to the same candidate.

### Assumptions
1. All candidate inputs fed into a single pipeline invocation represent the same candidate (uniqueness matched via identical emails).
2. PDFs contain parseable text (non-scanned). Future editions will incorporate OCR (Tesseract) fallback.

---

## Setup & Installation

### Setup Instructions
1. Clone or copy the repository to your local workspace.
2. Install the required libraries via `requirements.txt`.

### Install Command
```bash
pip install -r requirements.txt
```

---

## How to Run & Demo

### 1. Generate Sample Data
Run the sample data script to produce a demo resume (`sample.pdf`), a recruiter CSV (`recruiter.csv`), and a projection config (`config.json`):
```bash
python generate_sample_data.py
```

### 2. Generate Technical Design PDF
Run the document generator to produce the one-page Technical Design PDF (`Technical_Design.pdf`):
```bash
python generate_pdf.py
```

### 3. Run Pipeline CLI (Standard Output)
Run the pipeline to output the merged JSON profile directly to stdout:
```bash
python main.py --resume sample.pdf --csv recruiter.csv
```

### 4. Run Pipeline CLI (Projected File Output)
Execute using the projection configuration and write the output directly to a file (`result.json`):
```bash
python main.py --resume sample.pdf --csv recruiter.csv --config config.json --output result.json
```

---

## Running Automated Tests

Run the full pytest suite:
```bash
pytest src/tests/
```
The test suite validates phone/date/skills normalizations, merge precedence rules, confidence calculations, projection toggles, missing value behaviors, and malformed input handles.

---

## Example Output JSON

Below is an example of the standard output JSON produced by the transformer pipeline:

```json
{
  "candidate_id": "f06f048e-3acd-495c-9979-c5ba369cc436",
  "full_name": "Alex Mercer",
  "emails": [
    "alex.mercer@email.com"
  ],
  "phones": [
    "+15550199"
  ],
  "location": {
    "city": "San Francisco",
    "region": "CA",
    "country": "US"
  },
  "links": {
    "linkedin": "https://linkedin.com/in/alexmercer",
    "github": "https://github.com/alexmercer",
    "portfolio": null,
    "other": []
  },
  "headline": "Senior Staff Software Engineer",
  "years_experience": 7.8,
  "skills": [
    "C++",
    "Python",
    "JavaScript",
    "SQL",
    "Html",
    "Css",
    "React",
    "Node.js",
    "Express",
    "Fastapi",
    "Docker",
    "Kubernetes",
    "AWS",
    "Git",
    "Linux",
    "Jira",
    "MySQL",
    "Redis",
    "Ci/Cd",
    "Restful",
    "Scrum",
    "Agile"
  ],
  "experience": [
    {
      "job_title": "Senior Staff Software Engineer",
      "company": "Tech Corp",
      "start_date": "2021-01",
      "end_date": "Present",
      "description": "• Led design and architecture of high-throughput candidate parsing engines..."
    },
    {
      "job_title": "Software Engineer II",
      "company": "Web Solutions",
      "start_date": "2018-08",
      "end_date": "2020-12",
      "description": "• Developed responsive user interfaces using ReactJS..."
    }
  ],
  "education": [
    {
      "degree": "B.S",
      "institution": "Stanford University, California 2014 - 2018",
      "field_of_study": "Computer Science\nStanford University",
      "start_date": "2014-01",
      "end_date": "2018-01"
    }
  ],
  "provenance": [
    {
      "field": "full_name",
      "source": "sample.pdf",
      "method": "heuristic",
      "value": "Alex Mercer"
    },
    {
      "field": "location",
      "source": "recruiter.csv",
      "method": "csv_direct",
      "value": "San Francisco, CA"
    }
  ],
  "overall_confidence": 0.72
}
```
