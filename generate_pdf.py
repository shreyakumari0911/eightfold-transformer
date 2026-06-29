from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf():
    pdf_filename = "Technical_Design.pdf"
    
    # Minimal margins to guarantee single-page layout without cramming
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter,
        rightMargin=20, 
        leftMargin=20, 
        topMargin=20, 
        bottomMargin=20
    )
    
    styles = getSampleStyleSheet()
    
    # Modern, professional color palette (Slate & Blue)
    navy_dark = colors.HexColor("#0F172A")       # Slate 900
    blue_medium = colors.HexColor("#1D4ED8")     # Blue 700
    text_dark = colors.HexColor("#334155")       # Slate 700
    bg_accent = colors.HexColor("#F8FAFC")       # Slate 50
    divider_color = colors.HexColor("#E2E8F0")   # Slate 200
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.white,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#94A3B8"),
        spaceAfter=0
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=navy_dark,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.5,
        textColor=text_dark,
        spaceAfter=3
    )
    
    diagram_style = ParagraphStyle(
        'DiagramText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=blue_medium,
        alignment=1  # Centered
    )
    
    story = []
    
    # 1. Header Banner
    header_data = [
        [
            Paragraph("TECHNICAL DESIGN: MULTI-SOURCE CANDIDATE DATA TRANSFORMER", title_style),
            Paragraph("<b>Author:</b> Shreya Kumari &nbsp;&bull;&nbsp; shreyasingh091102@gmail.com<br/><b>Assignment:</b> Eightfold Candidate Transformer", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 212])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), navy_dark),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    
    # 2. Pipeline Diagram Box
    diagram_data = [[
        Paragraph(
            "<b>Pipeline Diagram:</b> &nbsp; Input &rarr; Detect Source &rarr; Parse &rarr; Normalize &rarr; Merge &rarr; Confidence &rarr; Projection &rarr; Validation &rarr; JSON Output", 
            diagram_style
        )
    ]]
    diagram_table = Table(diagram_data, colWidths=[572])
    diagram_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_accent),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 0.5, divider_color),
    ]))
    story.append(diagram_table)
    story.append(Spacer(1, 6))
    
    # 3. Left and Right Columns
    left_flowables = [
        Paragraph("1. System Architecture & Pipeline", section_title_style),
        Paragraph(
            "Built on a decoupled pipeline pattern executing sequentially:<br/>"
            "&bull; <b>Ingestion:</b> Identifies and validates unstructured (PDF) and structured (CSV) source file paths.<br/>"
            "&bull; <b>Parsing & Normalization:</b> Extracts fields and formats them to target standards prior to consolidation.<br/>"
            "&bull; <b>Consolidation:</b> Executes conflict resolution policies and computes lineage metadata.<br/>"
            "&bull; <b>Presentation:</b> Customizes schema projection shapes and formats values for validation.",
            body_style
        ),
        
        Paragraph("2. Canonical Schema Design", section_title_style),
        Paragraph(
            "Defines the single source of truth for candidate attributes via strict Pydantic schemas:<br/>"
            "&bull; <b>candidate_id:</b> Unique deterministic string generated per candidate.<br/>"
            "&bull; <b>location:</b> Structured sub-schema containing <i>city</i>, <i>region</i>, and <i>country</i>.<br/>"
            "&bull; <b>links:</b> Categorized endpoints mapping <i>linkedin</i>, <i>github</i>, <i>portfolio</i>, and <i>other</i> URL lists.<br/>"
            "&bull; <b>history:</b> Structured arrays for <i>experience</i> and <i>education</i> chronologically ordered.<br/>"
            "&bull; <b>metadata:</b> Lists tracking <i>provenance</i> logs and <i>field_confidence</i> levels.",
            body_style
        ),
        
        Paragraph("3. Normalization Strategy", section_title_style),
        Paragraph(
            "Standardizes attributes individually before merging to ensure deterministic outcomes:<br/>"
            "&bull; <b>Phones:</b> Formatted to <b>E.164</b> using the Google <i>phonenumbers</i> library. Mock numbers fall back to possible structures to ensure robust handling.<br/>"
            "&bull; <b>Dates:</b> Standardized to <b>YYYY-MM</b>. Relies on <i>python-dateutil</i> to parse free-text inputs, resolving current timelines to 'Present'.<br/>"
            "&bull; <b>Country:</b> Maps inputs to <b>ISO-3166-1 alpha-2</b>. Translates common US states (e.g. 'CA' &rarr; 'US') and defaults unresolved fields.<br/>"
            "&bull; <b>Skills:</b> Resolves skills (e.g., 'cpp', 'C Plus Plus' &rarr; 'C++') using exact synonym mappings and fuzzy matching (`rapidfuzz`).",
            body_style
        ),
        
        Paragraph("4. Merge & Conflict Resolution Strategy", section_title_style),
        Paragraph(
            "Combines multiple candidate sources using a priority-based precedence logic:<br/>"
            "&bull; <b>Precedence hierarchy:</b> Resume PDF (Priority 2) &gt; Recruiter CSV (Priority 1) &gt; Unknown (0).<br/>"
            "&bull; <b>Conflict Policy:</b> Single-value fields are resolved by taking the value from the highest priority source.<br/>"
            "&bull; <b>Array Unioning:</b> Deduplicates lists (emails, phones) and aggregates skills.<br/>"
            "&bull; <b>Timeline Alignment:</b> Overlapping experiences (same company & start year) are consolidated and sorted by start date.",
            body_style
        )
    ]
    
    right_flowables = [
        Paragraph("5. Explainable Confidence Scoring", section_title_style),
        Paragraph(
            "Assigns explicit confidences representing the quality and certainty of the data:<br/>"
            "&bull; <b>Resume (Direct):</b> 0.95 confidence weight.<br/>"
            "&bull; <b>CSV (Direct):</b> 0.90 confidence weight.<br/>"
            "&bull; <b>Regex extraction:</b> 0.80 confidence weight.<br/>"
            "&bull; <b>Heuristics fallback:</b> 0.60 confidence weight.<br/>"
            "&bull; <b>Unknown:</b> 0.30 fallback weight.<br/>"
            "&bull; <b>Overall score:</b> Mathematical average of populated field-level confidence ratings.",
            body_style
        ),
        
        Paragraph("6. Provenance Model", section_title_style),
        Paragraph(
            "Ensures full audit lineage by tracking extraction lineage for every field:<br/>"
            "&bull; Stores <b>field</b> name, <b>source</b> filename, and extraction <b>method</b>.<br/>"
            "&bull; Lineage is recorded dynamically for all values, tracking the winning source for resolved conflicts.",
            body_style
        ),
        
        Paragraph("7. Configurable Runtime Projection Layer", section_title_style),
        Paragraph(
            "<b>Runtime Config:</b> Supports field inclusion, field renaming, normalization rules, provenance/confidence toggles, and configurable missing-value behavior without code changes.<br/>"
            "&bull; <b>Field Selection:</b> Restructure output using <code>include_fields</code> list.<br/>"
            "&bull; <b>Field Aliasing:</b> Rename fields dynamically (e.g. <code>full_name</code> &rarr; <code>name</code>).<br/>"
            "&bull; <b>Metadata Filtering:</b> Enables toggling metadata lists (confidence, provenance).<br/>"
            "&bull; <b>Missing Fields:</b> Handles missing data by outputting <code>'null'</code> values or <code>'exclude'</code> (removing empty keys).",
            body_style
        ),
        
        Paragraph("8. Schema Validation & Edge Cases", section_title_style),
        Paragraph(
            "&bull; <b>Validation:</b> Standardizes inputs using Pydantic. Reports syntax and formatting errors as readable messages.<br/>"
            "&bull; <b>Edge cases:</b> Gracefully handles empty source files, missing credentials, duplicate candidate records, and malformed files.",
            body_style
        ),
        
        Paragraph("9. Assumptions & Future Enhancements", section_title_style),
        Paragraph(
            "&bull; <b>Assumptions:</b> Raw text is extractable from PDFs. Candidates sharing primary emails represent the same entity.<br/>"
            "&bull; <b>Future Enhancements:</b> Support additional parsers (LinkedIn, GitHub JSON, ATS XML). Integrate OCR (Tesseract) for scanned resumes.",
            body_style
        )
    ]
    
    # Column width specifications (Total width = letter 612 - margin 40 = 572)
    left_col_width = 280
    right_col_width = 280
    spacer_width = 12
    
    left_cell_table = Table([[x] for x in left_flowables], colWidths=[left_col_width])
    left_cell_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    right_cell_table = Table([[x] for x in right_flowables], colWidths=[right_col_width])
    right_cell_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    master_table = Table([[left_cell_table, "", right_cell_table]], colWidths=[left_col_width, spacer_width, right_col_width])
    master_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LINEBEFORE', (2,0), (2,-1), 0.5, divider_color),
    ]))
    story.append(master_table)
    
    # 4. Minimalist Page Footer
    story.append(Spacer(1, 6))
    footer_data = [
        [
            Paragraph("TECHNICAL DESIGN &bull; MULTI-SOURCE CANDIDATE TRANSFORMER", ParagraphStyle('F1', parent=body_style, fontSize=6.5, textColor=colors.HexColor("#94A3B8"))),
            Paragraph("Page 1 of 1", ParagraphStyle('F2', parent=body_style, fontSize=6.5, textColor=colors.HexColor("#94A3B8"), alignment=2))
        ]
    ]
    footer_table = Table(footer_data, colWidths=[286, 286])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEABOVE', (0,0), (-1,-1), 0.5, divider_color),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(footer_table)
    
    # Build PDF
    doc.build(story)
    print("Technical Design document generated as Technical_Design.pdf successfully!")

if __name__ == "__main__":
    build_pdf()
