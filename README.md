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
├── generate_pdf.py       # Script to generate the Technical Design PDF
├── generate_sample_data.py # Script to prepare mock input files
├── main.py               # Main CLI Pipeline entry point
├── README.md             # Project documentation
└── config.json           # Sample runtime projection config
```

---

## Design Decisions, Tradeoffs & Assumptions

### Design Decisions
- **Deterministic Precedence Merger:** Resume PDF data is prioritised over recruiter-filled CSV details, as candidates author their resumes, while recruiter records are susceptible to transcription errors.
- **Possible Number Validation Fallback:** Fictitious numbers (e.g. 555-0199) fail strict telecoms-plan carrier checks in Google `phonenumbers`. The phone normalizer falls back to `is_possible_number` formatting, preserving mock numbers while enforcing strict validation on real numbers.
- **Fuzzy Skill Merging:** Implemented combining exact matching with fuzzy similarity lookups (`rapidfuzz`) to automatically map syntax variants ("cpp", "C Plus Plus" → "C++").

### Tradeoffs
- **Rule-based PDF Text Parsing vs. LLM Extractors:**
  - *Tradeoff:* Written using deterministic regex and heuristic layout anchors to extract names, experiences, education, and dates. While LLMs (like GPT-4/Claude) excel at extracting unstructured text, rule-based extraction guarantees local execution, 100% determinism, speed, and no external API key dependency.
- **Flat List unioning:** Emails, phones, and skills are unioned across sources. While this maximizes data recovery, it assumes all details pertain to the same candidate.

### Assumptions
1. All candidate inputs fed into a single pipeline invocation represent the same candidate (uniqueness matched via identical emails).
2. PDFs contain parseable text (non-scanned). Future editions will incorporate OCR (Tesseract) fallback.

---

## Dependencies

- **pydantic**: Data parsing and schema validation
- **pandas**: Structured CSV parsing
- **pdfplumber**: PDF text extraction
- **python-dateutil**: Robust date parsing
- **phonenumbers**: E.164 phone formatting
- **rapidfuzz**: Skill matching
- **pytest**: Automated testing
- **reportlab**: PDF Design Doc generation

To install all dependencies:
```bash
pip install pydantic pandas pdfplumber python-dateutil phonenumbers rapidfuzz pytest reportlab
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
