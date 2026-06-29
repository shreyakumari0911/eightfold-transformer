from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import sys

def build_pdf():
    pdf_filename = "Technical_Design.pdf"
    
    # 0.25 inch margins for maximizing space to fit everything on a single page
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter,
        rightMargin=18, 
        leftMargin=18, 
        topMargin=18, 
        bottomMargin=18
    )
    
    styles = getSampleStyleSheet()
    
    # Define color palette
    primary_color = colors.HexColor("#1A365D")    # Slate Navy
    secondary_color = colors.HexColor("#2B6CB0")  # Indigo Blue
    accent_bg = colors.HexColor("#EDF2F7")        # Light Gray-Blue
    text_dark = colors.HexColor("#2D3748")        # Charcoal
    text_light = colors.HexColor("#FFFFFF")
    divider_color = colors.HexColor("#CBD5E0")
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=primary_color,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=secondary_color,
        spaceAfter=8
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=11,
        textColor=primary_color,
        spaceBefore=0,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=text_dark,
        spaceAfter=4
    )
    
    body_bold_style = ParagraphStyle(
        'SectionBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=9,
        textColor=text_light
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        textColor=text_dark
    )
    
    story = []
    
    # Header Banner (using a Table for styling)
    header_data = [
        [
            Paragraph("TECHNICAL DESIGN: MULTI-SOURCE CANDIDATE DATA TRANSFORMER", ParagraphStyle('H1', parent=title_style, textColor=text_light)),
            Paragraph("<b>Author:</b> Senior Staff Engineer<br/><b>Target:</b> Production Release", ParagraphStyle('HSub', parent=body_style, textColor=colors.HexColor("#E2E8F0"), alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[400, 176])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    
    # 2-Column Layout for the document body
    # Left Column content list
    left_flowables = [
        Paragraph("1. System Architecture & Pipeline", section_title_style),
        Paragraph(
            "The system is built on a clean pipeline pattern using SOLID design principles. "
            "It decouples raw data ingestion, text extraction, data normalization, merge resolution, "
            "and runtime projection. The pipeline executes sequentially:<br/>"
            "<b>Input Sources</b> → <b>Detect Source</b> → <b>Parse/Extract</b> → <b>Normalize</b> → "
            "<b>Merge (Conflict Resolution)</b> → <b>Confidence Scoring</b> → <b>Projection Layer</b> → "
            "<b>Schema Validation</b> → <b>JSON Output</b>",
            body_style
        ),
        
        Paragraph("2. Canonical Schema Design", section_title_style),
        Paragraph(
            "The canonical schema represents the single source of truth for candidate data. Defined using "
            "Pydantic models for validation, it maintains strict type constraints:<br/>"
            "• <b>candidate_id:</b> Determinsitic unique identifier.<br/>"
            "• <b>full_name / headline / location / years_experience:</b> Canonical single values.<br/>"
            "• <b>emails / phones / links / skills:</b> Normalized arrays representing union of inputs.<br/>"
            "• <b>experience / education:</b> Structured sub-arrays sorted descending by start date.<br/>"
            "• <b>provenance:</b> Map of fields to their source file, extraction method, and raw values.<br/>"
            "• <b>field_confidence / overall_confidence:</b> Calculated indicators.",
            body_style
        ),
        
        Paragraph("3. Normalization Strategy", section_title_style),
        Paragraph(
            "Normalization is executed on individual source records before merging to ensure consistency:<br/>"
            "• <b>Phones:</b> Standardized to <b>E.164</b> format using the Google <i>phonenumbers</i> library.<br/>"
            "• <b>Dates:</b> Transformed to <b>YYYY-MM</b> format. Relies on <i>python-dateutil</i> to handle formats "
            "('Jan 2018', '2018/01', etc.). Resolves 'Present/Current' to 'Present' and defaults missing months to Jan.<br/>"
            "• <b>Country:</b> Normalized to <b>ISO-3166 alpha-2</b> code by searching location tokens in a compiled dictionary.<br/>"
            "• <b>Skills:</b> Maps synonyms ('C Plus Plus', 'cpp' → 'C++') using exact lookups and fuzzy <i>rapidfuzz</i> matching.",
            body_style
        ),
        
        Paragraph("4. Merge & Conflict Resolution Strategy", section_title_style),
        Paragraph(
            "Merging combines data from multiple inputs using a <b>deterministic precedence policy</b>. "
            "Candidate-authored primary sources (Resume PDF) overwrite third-party secondary sources (Recruiter CSV).<br/>"
            "• <b>Precedence:</b> Resume PDF (Priority 2) > Recruiter CSV (Priority 1) > Unknown (0).<br/>"
            "• <b>Conflict Resolution:</b> For single fields (e.g. name), the value with highest source priority wins. "
            "If a conflict occurs, the winning source and method are recorded in the provenance schema.<br/>"
            "• <b>Arrays & Nesting:</b> Email/phone arrays are unioned and deduplicated. Work history and education sections "
            "are merged by fuzzy matching overlapping intervals (same company/degree + start year) and sorted chronologically.",
            body_style
        )
    ]
    
    # Right Column content list
    right_flowables = [
        Paragraph("5. Explainable Confidence Scoring", section_title_style),
        Paragraph(
            "Confidence scores are computed deterministically per field based on source trustworthiness and "
            "extraction methodologies. Raw scoring assignments:<br/>"
            "• <b>Resume (Direct):</b> 0.95 &nbsp;&nbsp;|&nbsp;&nbsp; <b>CSV (Direct):</b> 0.90<br/>"
            "• <b>Regex Extraction:</b> 0.80 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Heuristics:</b> 0.60 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Unknown:</b> 0.30<br/>"
            "The <b>overall_confidence</b> score is calculated as the mathematical average of all populated field-level confidences.",
            body_style
        ),
        
        Paragraph("6. Provenance Model", section_title_style),
        Paragraph(
            "To guarantee system explainability, the canonical output maps every populated field to its original "
            "provenance record: <code>{field: {source: str, method: str, value: Any}}</code>. "
            "If fields are merged from multiple sources, the winner's metadata is preserved, keeping auditability intact.",
            body_style
        ),
        
        Paragraph("7. Configurable Runtime Projection Layer", section_title_style),
        Paragraph(
            "Keeps the canonical profile separate from external outputs. Configured via <code>config.json</code>:<br/>"
            "• <b>Inclusion/Exclusion:</b> Specify output fields in <code>include_fields</code> list.<br/>"
            "• <b>Field Renaming/Mapping:</b> Maps canonical terms to external targets (e.g., <code>full_name</code> → <code>name</code>).<br/>"
            "• <b>Metadata Toggles:</b> Dynamically enable/disable confidence arrays and provenance tracking.<br/>"
            "• <b>Missing Values:</b> Choose <code>'null'</code> values or <code>'exclude'</code> (omitting empty keys).",
            body_style
        ),
        
        Paragraph("8. Schema Validation & Edge Cases", section_title_style),
        Paragraph(
            "• <b>Validation:</b> Both the canonical profile and the final projected output are validated against Pydantic models. "
            "Validation errors format into readable messages detailing field location, expected type, and actual input.<br/>"
            "• <b>Edge Cases:</b> Gracefully handles empty files, missing fields (resolves to null/omitted), and duplicate candidates "
            "(merged into one canonical record by checking email match prior to execution).",
            body_style
        ),
        
        Paragraph("9. Assumptions & Future Improvements", section_title_style),
        Paragraph(
            "• <b>Assumptions:</b> Input source files are accessible. PDFs contain extractable text (non-scanned). "
            "Profiles sharing an email address belong to the same candidate.<br/>"
            "• <b>Future Enhancements:</b> Support additional parsers (LinkedIn, GitHub JSON, ATS XML). "
            "Integrate OCR (e.g. Tesseract) for scanned PDF resumes. Train ML models for semantic-based section parsing.",
            body_style
        )
    ]
    
    # We place the two columns inside a 1-row table for side-by-side display
    # Set the column widths (sum = letter width 612 - margins 36 = 576)
    left_col_width = 282
    right_col_width = 282
    spacer_width = 12
    
    # Pack flowables into lists
    left_cell_table = Table([[x] for x in left_flowables], colWidths=[left_col_width])
    left_cell_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    right_cell_table = Table([[x] for x in right_flowables], colWidths=[right_col_width])
    right_cell_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    # Master Table containing left and right columns separated by a vertical line
    master_table = Table([[left_cell_table, "", right_cell_table]], colWidths=[left_col_width, spacer_width, right_col_width])
    master_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        # Vertical divider line in the center column
        ('LINEBEFORE', (2,0), (2,-1), 0.5, divider_color),
    ]))
    story.append(master_table)
    
    # Footer Section
    story.append(Spacer(1, 10))
    footer_data = [
        [
            Paragraph("CONFIDENTIAL & PROPRIETARY", ParagraphStyle('F1', parent=body_style, textColor=colors.HexColor("#718096"))),
            Paragraph("Page 1 of 1", ParagraphStyle('F2', parent=body_style, textColor=colors.HexColor("#718096"), alignment=2))
        ]
    ]
    footer_table = Table(footer_data, colWidths=[288, 288])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEABOVE', (0,0), (-1,-1), 0.5, divider_color),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(footer_table)
    
    # Build Document
    doc.build(story)
    print("Technical Design document generated as Technical_Design.pdf successfully!")

if __name__ == "__main__":
    build_pdf()
