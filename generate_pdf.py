from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf():
    pdf_filename = "Technical_Design.pdf"
    
    # Highly compact A4 page layout (margins: 18 pt) to fit everything on exactly one page
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=A4,
        rightMargin=18, 
        leftMargin=18, 
        topMargin=18, 
        bottomMargin=18
    )
    
    styles = getSampleStyleSheet()
    
    # Dark modern corporate theme (Slate Navy & Royal Blue)
    navy_primary = colors.HexColor("#0F172A")    # Slate 900
    blue_accent = colors.HexColor("#1D4ED8")     # Blue 700
    text_color = colors.HexColor("#334155")      # Slate 700
    bg_accent = colors.HexColor("#F8FAFC")       # Slate 50
    divider_color = colors.HexColor("#E2E8F0")   # Slate 200
    
    # Typography configuration
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.white,
        spaceAfter=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#94A3B8"),
        spaceAfter=0
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10.5,
        textColor=navy_primary,
        spaceBefore=3,
        spaceAfter=2,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'SectionBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=9,
        textColor=text_color,
        spaceAfter=2
    )
    
    diagram_style = ParagraphStyle(
        'DiagramText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8.5,
        textColor=blue_accent,
        alignment=1  # Centered
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor("#475569")
    )
    
    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.2,
        leading=7.8,
        textColor=text_color
    )
    
    story = []
    
    # 1. Main Header Title Banner
    header_data = [
        [
            Paragraph("TECHNICAL ABSTRACT: MULTI-SOURCE CANDIDATE DATA TRANSFORMER", title_style),
            Paragraph("<b>Author:</b> Shreya Kumari &nbsp;&bull;&nbsp; shreyasingh091102@gmail.com<br/><b>Assignment:</b> Eightfold Candidate Transformer", subtitle_style)
        ]
    ]
    # Total printable width = 559 pt (A4 width 595 - margin 36)
    header_table = Table(header_data, colWidths=[359, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), navy_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    
    # 2. Pipeline flow diagram block
    pipeline_data = [[
        Paragraph(
            "<b>Pipeline:</b> Input Sources &rarr; Detect Source &rarr; Parse &amp; Extract &rarr; Normalize &rarr; Merge &rarr; Confidence &amp; Provenance &rarr; Projection &rarr; Validation &rarr; JSON Output", 
            diagram_style
        )
    ]]
    pipeline_table = Table(pipeline_data, colWidths=[559])
    pipeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_accent),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.5, divider_color),
    ]))
    story.append(pipeline_table)
    story.append(Spacer(1, 4))
    
    # Left Column Elements
    left_flowables = [
        Paragraph("1. Problem Statement", section_title_style),
        Paragraph(
            "Recruitment workflows ingest candidate data from highly fragmented sources, "
            "ranging from unstructured resume PDFs to structured recruiter CSVs. This pipeline "
            "addresses this fragmentation by parsing, normalising, resolving conflicts, and merging "
            "these inputs deterministically into a single canonical Pydantic profile.",
            body_style
        ),
        
        Paragraph("2. System Architecture", section_title_style),
        Paragraph(
            "The system is built on a clean pipeline pattern using SOLID design principles:<br/>"
            "&bull; <b>Ingestion:</b> Evaluates input files and routes to dedicated parsers.<br/>"
            "&bull; <b>Parsing Layer:</b> Extracts text blocks via <code>pdfplumber</code> and rows via <code>pandas</code>.<br/>"
            "&bull; <b>Normalization Layer:</b> Applies E.164, YYYY-MM, ISO-3166-1, and skill synonyms.<br/>"
            "&bull; <b>Merger Layer:</b> Implements precedence rules and resolves data conflicts.<br/>"
            "&bull; <b>Scoring & Provenance:</b> Audits lineage and computes confidence levels.<br/>"
            "&bull; <b>Projection Layer:</b> Restructures schemas dynamically per client output needs.",
            body_style
        ),
        
        Paragraph("3. Canonical Schema", section_title_style),
        Paragraph(
            "Defined strictly using Pydantic models to guarantee contract integrity:<br/>"
            "&bull; <b>candidate_id:</b> Deterministic string identifier generated per profile.<br/>"
            "&bull; <b>location:</b> Structured details containing <i>city</i>, <i>region</i>, and <i>country</i>.<br/>"
            "&bull; <b>links:</b> Endpoint map storing <i>linkedin</i>, <i>github</i>, <i>portfolio</i>, and <i>other</i> lists.<br/>"
            "&bull; <b>history:</b> Structured experience and education items chronologically sorted.<br/>"
            "&bull; <b>audit:</b> Flat lists logging field <i>provenance</i> and <i>field_confidence</i> weights.",
            body_style
        ),
        
        Paragraph("4. Normalization Strategy", section_title_style),
        Paragraph(
            "Preprocesses individual profiles before merging to guarantee consistency. The core normalization rules are mapped below:",
            body_style
        )
    ]
    
    # 4. Normalization Strategy Table
    norm_table_data = [
        [Paragraph("<b>Field</b>", table_header_style), Paragraph("<b>Target Format</b>", table_header_style), Paragraph("<b>Method / Library</b>", table_header_style)],
        [Paragraph("Phones", table_body_style), Paragraph("E.164 format", table_body_style), Paragraph("<code>phonenumbers</code> library", table_body_style)],
        [Paragraph("Dates", table_body_style), Paragraph("YYYY-MM format", table_body_style), Paragraph("<code>python-dateutil</code> parser", table_body_style)],
        [Paragraph("Country", table_body_style), Paragraph("ISO-3166 alpha-2", table_body_style), Paragraph("Token matching lookup", table_body_style)],
        [Paragraph("Skills", table_body_style), Paragraph("Canonical synonyms", table_body_style), Paragraph("Exact maps + <code>rapidfuzz</code>", table_body_style)]
    ]
    norm_table = Table(norm_table_data, colWidths=[50, 100, 120])
    norm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), divider_color),
        ('GRID', (0,0), (-1,-1), 0.5, divider_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    left_flowables.append(norm_table)
    
    # Right Column Elements
    right_flowables = [
        Paragraph("5. Merge & Conflict Resolution", section_title_style),
        Paragraph(
            "Consolidates profiles using a strict source precedence hierarchy:<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>Resume PDF (Priority 2) &rarr; Recruiter CSV (Priority 1) &rarr; Unknown (0)</b><br/>"
            "&bull; <b>Precedence Policy:</b> Single fields select values from the highest priority source.<br/>"
            "&bull; <b>Array Fields:</b> Union and deduplicate emails, phones, and skills lists.<br/>"
            "&bull; <b>Work History:</b> Combines experience/education timelines, groups duplicates (same company & start year), and sorts chronologically.",
            body_style
        ),
        
        Paragraph("6. Explainable Confidence", section_title_style),
        Paragraph(
            "Assigns explicit certainty weights indicating source reliability. Confidences are mapped as follows:",
            body_style
        )
    ]
    
    # 6. Confidence Scoring Table
    conf_table_data = [
        [Paragraph("<b>Extraction Method</b>", table_header_style), Paragraph("<b>Score</b>", table_header_style)],
        [Paragraph("Resume PDF direct extraction", table_body_style), Paragraph("0.95", table_body_style)],
        [Paragraph("Recruiter CSV direct parsing", table_body_style), Paragraph("0.90", table_body_style)],
        [Paragraph("Regex extraction patterns", table_body_style), Paragraph("0.80", table_body_style)],
        [Paragraph("Heuristics and text alignment rules", table_body_style), Paragraph("0.60", table_body_style)],
        [Paragraph("Unknown sources / default values", table_body_style), Paragraph("0.30", table_body_style)]
    ]
    conf_table = Table(conf_table_data, colWidths=[180, 90])
    conf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), divider_color),
        ('GRID', (0,0), (-1,-1), 0.5, divider_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    right_flowables.append(conf_table)
    right_flowables.append(Spacer(1, 2))
    
    right_flowables.extend([
        Paragraph("7. Provenance", section_title_style),
        Paragraph(
            "Preserves data lineage by capturing metadata for every field value:<br/>"
            "&bull; Tracks <b>field</b> name, <b>source</b> filename, and extraction <b>method</b>.<br/>"
            "&bull; Audit records are aggregated in a query-friendly flat list layout.",
            body_style
        ),
        
        Paragraph("8. Runtime Projection Layer", section_title_style),
        Paragraph(
            "<b>Runtime Config:</b> Supports field inclusion, field renaming, normalization rules, "
            "provenance/confidence toggles, and configurable missing-value behavior without code changes.<br/>"
            "&bull; <b>Aliasing & Filters:</b> Uses <code>rename_fields</code> mapping and <code>include_fields</code> lists.<br/>"
            "&bull; <b>Missing Fields:</b> Toggles output between <code>'null'</code> and <code>'exclude'</code> (removing empty keys).",
            body_style
        ),
        
        Paragraph("9. Validation & Edge Cases", section_title_style),
        Paragraph(
            "&bull; <b>Pydantic Validation:</b> Validates projected schema contracts. Synthesizes errors into detailed trace messages.<br/>"
            "&bull; <b>Edge cases:</b> Gracefully handles empty source files, missing credentials, duplicate candidates, and malformed files.",
            body_style
        ),
        
        Paragraph("10. Assumptions & Future Improvements", section_title_style),
        Paragraph(
            "&bull; <b>Assumptions:</b> Raw text is extractable from PDFs. Candidates sharing primary emails represent the same entity.<br/>"
            "&bull; <b>Future Enhancements:</b> Support additional parsers (LinkedIn, GitHub JSON, ATS XML). Integrate OCR (Tesseract) for scanned resumes.",
            body_style
        )
    ])
    
    # 2-Column layout table structure (Total width = A4 width 595 - margins 36 = 559 pt)
    left_col_width = 273
    right_col_width = 273
    spacer_width = 13
    
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
    
    # 5. Minimalist Page Footer
    story.append(Spacer(1, 4))
    footer_data = [
        [
            Paragraph("TECHNICAL DESIGN ABSTRACT &bull; CANDIDATE TRANSFORMER", ParagraphStyle('F1', parent=body_style, fontSize=6, textColor=colors.HexColor("#94A3B8"))),
            Paragraph("Page 1 of 1", ParagraphStyle('F2', parent=body_style, fontSize=6, textColor=colors.HexColor("#94A3B8"), alignment=2))
        ]
    ]
    footer_table = Table(footer_data, colWidths=[279, 280])
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
