import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_csv():
    """
    Generates the recruiter.csv sample data file.
    """
    data = [{
        "full_name": "Alex Mercer",
        "email": "alex.mercer@email.com",
        "phone": "555-0199",
        "location": "San Francisco, CA",
        "headline": "Staff Software Engineer",
        "years_experience": "8.0",
        "skills": "cpp, Python, ReactJS, Kubernetes, SQL"
    }]
    df = pd.DataFrame(data)
    df.to_csv("recruiter.csv", index=False)
    print("Created recruiter.csv")

def create_config():
    """
    Generates config.json for custom projection testing.
    """
    config = {
        "include_fields": [
            "candidate_id",
            "name",
            "emails",
            "phones",
            "location",
            "skills",
            "experience",
            "overall_confidence",
            "provenance"
        ],
        "rename_fields": {
            "full_name": "name"
        },
        "include_confidence": True,
        "include_provenance": True,
        "missing_value_behavior": "null"
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("Created config.json")

def create_pdf():
    """
    Generates a structured candidate resume PDF.
    """
    pdf_filename = "sample.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor("#1A365D")  # Slate Navy
    text_color = colors.HexColor("#2D3748")     # Dark Charcoal
    
    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=4
    )
    
    title_style = ParagraphStyle(
        'ResumeTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=8
    )
    
    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=text_color,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'ResumeH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=8
    )
    
    story = []
    
    # Name and title
    story.append(Paragraph("Alex Mercer", name_style))
    story.append(Paragraph("Senior Staff Software Engineer", title_style))
    
    # Contact info
    contact_text = (
        "Email: alex.mercer@email.com &nbsp;&nbsp;|&nbsp;&nbsp; "
        "Phone: +1 555-0199 &nbsp;&nbsp;|&nbsp;&nbsp; "
        "Location: San Francisco, California, USA<br/>"
        "LinkedIn: https://linkedin.com/in/alexmercer &nbsp;&nbsp;|&nbsp;&nbsp; "
        "GitHub: https://github.com/alexmercer"
    )
    story.append(Paragraph(contact_text, contact_style))
    
    # Summary
    story.append(Paragraph("Professional Summary", h1_style))
    story.append(Paragraph(
        "Highly accomplished Senior Software Engineer with over 7 years of experience in architecting, "
        "developing, and scaling complex web applications and backend microservices. Proven expertise "
        "in C++, Python, JavaScript, and AWS cloud infrastructures.",
        body_style
    ))
    
    # Experience
    story.append(Paragraph("Work Experience", h1_style))
    
    job1_header = "<b>Senior Staff Software Engineer</b> at Tech Corp &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Jan 2021 - Present"
    story.append(Paragraph(job1_header, body_style))
    story.append(Paragraph(
        "• Led design and architecture of high-throughput candidate parsing engines, serving millions of active users.<br/>"
        "• Wrote clean, production-grade microservices in Python and C++ to optimize runtime efficiency by 40%.<br/>"
        "• Configured CI/CD pipelines, Docker containers, and monitored cloud environments on AWS.",
        body_style
    ))
    
    job2_header = "<b>Software Engineer II</b> at Web Solutions &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 08/2018 - 12/2020"
    story.append(Paragraph(job2_header, body_style))
    story.append(Paragraph(
        "• Developed responsive user interfaces using ReactJS, Redux, and modern JavaScript standards.<br/>"
        "• Built RESTful API endpoints using NodeJS and Express, integrating MySQL and Redis cache layers.<br/>"
        "• Actively participated in Scrum and Agile sprints, driving product development cycles.",
        body_style
    ))
    
    # Education
    story.append(Paragraph("Education", h1_style))
    edu_text = "<b>B.S. in Computer Science</b><br/>Stanford University, California &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2014 - 2018"
    story.append(Paragraph(edu_text, body_style))
    
    # Skills
    story.append(Paragraph("Technical Skills", h1_style))
    skills_text = (
        "<b>Languages:</b> C Plus Plus, Python, JavaScript, SQL, HTML, CSS<br/>"
        "<b>Frameworks:</b> ReactJS, NodeJS, Express, FastAPI, Docker, Kubernetes<br/>"
        "<b>Tools:</b> AWS, Git, GitHub, Linux, JIRA"
    )
    story.append(Paragraph(skills_text, body_style))
    
    doc.build(story)
    print("Created sample.pdf")

if __name__ == "__main__":
    create_csv()
    create_config()
    create_pdf()
