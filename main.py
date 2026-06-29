import argparse
import json
import os
import sys
from typing import List, Dict, Any

from src.parsers.pdf_parser import PDFParser
from src.parsers.csv_parser import CSVParser
from src.normalizers.normalize import normalize_raw_profile
from src.merger.profile_merger import ProfileMerger
from src.projection.projector import ProjectionLayer
from src.validation.validator import validate_canonical_profile, validate_projected_profile
from src.schemas.canonical import CandidateProfile

def setup_logger():
    """
    Sets up simple stdout logging.
    """
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("TransformerPipeline")

def run_pipeline(resume_path: str = None, csv_path: str = None, config_path: str = None, output_path: str = None):
    logger = setup_logger()
    logger.info("Initializing Multi-Source Candidate Data Transformer Pipeline...")
    
    # 1. Input Verification & Source Detection
    if not resume_path and not csv_path:
        logger.error("Error: At least one input source (--resume or --csv) must be provided.")
        sys.exit(1)
        
    raw_profiles: List[Dict[str, Any]] = []
    
    # 2. Parsing & Field Extraction
    if resume_path:
        if not os.path.exists(resume_path):
            logger.error(f"Resume file not found: {resume_path}")
            sys.exit(1)
        logger.info(f"Source Detected: PDF Resume -> {resume_path}")
        logger.info(f"Parsing and extracting fields from PDF...")
        try:
            pdf_parser = PDFParser()
            raw_pdf_profile = pdf_parser.parse(resume_path)
            raw_profiles.append(raw_pdf_profile)
            logger.info("PDF resume parsed successfully.")
        except Exception as e:
            logger.error(f"Error parsing PDF resume: {str(e)}")
            sys.exit(1)
            
    if csv_path:
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            sys.exit(1)
        logger.info(f"Source Detected: Recruiter CSV -> {csv_path}")
        logger.info(f"Parsing and extracting rows from CSV...")
        try:
            csv_parser = CSVParser()
            raw_csv_profiles = csv_parser.parse(csv_path)
            raw_profiles.extend(raw_csv_profiles)
            logger.info(f"CSV file parsed successfully. Extracted {len(raw_csv_profiles)} record(s).")
        except Exception as e:
            logger.error(f"Error parsing Recruiter CSV: {str(e)}")
            sys.exit(1)
            
    # 3. Normalization
    logger.info("Normalizing extracted candidate data (Phones, Dates, Country, Skills)...")
    normalized_profiles = []
    for raw_prof in raw_profiles:
        norm_prof = normalize_raw_profile(raw_prof)
        normalized_profiles.append(norm_prof)
        
    # 4. Merger & Conflict Resolution
    # We group inputs by candidate. In a real system, we'd group by email/name.
    # For this CLI demonstration, we assume all inputs belong to the same candidate and merge them.
    logger.info("Merging profiles and resolving conflicts (Precedence: Resume > CSV)...")
    try:
        merger = ProfileMerger()
        merged_profile: CandidateProfile = merger.merge_profiles(normalized_profiles)
        logger.info("Profiles merged successfully.")
    except Exception as e:
        logger.error(f"Error merging profiles: {str(e)}")
        sys.exit(1)
        
    # 5. Schema Validation (Canonical Model)
    logger.info("Validating merged profile against canonical schema...")
    canonical_dict = merged_profile.model_dump()
    is_valid_canonical, err_msg_canonical = validate_canonical_profile(canonical_dict)
    if not is_valid_canonical:
        logger.error(f"Canonical Validation Failed:\n{err_msg_canonical}")
        sys.exit(1)
    logger.info("Canonical schema validation passed.")
    
    # 6. Projection Layer
    config = {}
    if config_path:
        if not os.path.exists(config_path):
            logger.error(f"Config file not found: {config_path}")
            sys.exit(1)
        logger.info(f"Loading projection config: {config_path}")
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse config JSON: {str(e)}")
            sys.exit(1)
    else:
        logger.info("No projection config provided. Using default canonical projection.")
        
    logger.info("Projecting canonical profile to output structure...")
    projector = ProjectionLayer(config)
    projected_output = projector.project(merged_profile)
    
    # 7. Projected Output Schema Validation
    logger.info("Validating projected profile output...")
    is_valid_projected, err_msg_projected = validate_projected_profile(projected_output, config)
    if not is_valid_projected:
        logger.error(f"Projected Schema Validation Failed:\n{err_msg_projected}")
        sys.exit(1)
    logger.info("Projected schema validation passed.")
    
    # 8. Output Serialization
    output_json = json.dumps(projected_output, indent=2)
    if output_path:
        logger.info(f"Writing final JSON output to {output_path}...")
        try:
            with open(output_path, "w") as f:
                f.write(output_json)
            logger.info("Pipeline completed successfully!")
        except Exception as e:
            logger.error(f"Failed to write output file: {str(e)}")
            sys.exit(1)
    else:
        logger.info("Pipeline completed successfully! Printing final JSON output:")
        print(output_json)

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer Pipeline")
    parser.add_argument("--resume", help="Path to resume PDF file")
    parser.add_argument("--csv", help="Path to recruiter CSV file")
    parser.add_argument("--config", help="Path to projection configuration JSON file")
    parser.add_argument("--output", help="Path to output result JSON file")
    
    args = parser.parse_args()
    run_pipeline(
        resume_path=args.resume,
        csv_path=args.csv,
        config_path=args.config,
        output_path=args.output
    )

if __name__ == "__main__":
    main()
