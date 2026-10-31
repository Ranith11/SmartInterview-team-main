import os
import sys
import re
from PIL import Image

from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(REPO_ROOT, "docs", "final_deliverables")
os.makedirs(OUT_DIR, exist_ok=True)

def format_inline_md(text):
    if not text:
        return ""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`(.*?)`', r'<font face="Courier"><b>\1</b></font>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    return text


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SmartInterview — Academic Review & Technical Defense")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            self.drawString(54, 36, "Confidential — Keshav Memorial Institute of Technology (KMIT)")
            self.drawRightString(558, 36, f"Page {self._pageNumber} of {page_count}")
            self.line(54, 48, 558, 48)
        self.restoreState()


class LandscapeSlideCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#A0AEC0"))
        
        # Top right team badge
        self.drawRightString(740, 580, "SMARTINTERVIEW | TEAM G-1392 | CSE (AI & ML)")
        
        # Bottom footer line
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(50, 42, 742, 42)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(50, 30, "Keshav Memorial Institute of Technology | Dept of CSE (AI & ML)")
        self.drawRightString(742, 30, f"Slide {self._pageNumber} of {page_count}")
        self.restoreState()


# ==============================================================================
# 1. BUILD PRESENTATION PDF (Landscape 16:9 Slides)
# ==============================================================================
def build_presentation_pdf():
    pdf_path = os.path.join(REPO_ROOT, "SmartInterview_Presentation_Final.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=(792, 612), # 11 x 8.5 landscape
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=15
    )
    
    slide_body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )
    
    slide_bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11.5,
        leading=16.5,
        textColor=colors.HexColor('#2D3748'),
        leftIndent=15,
        spaceAfter=6
    )
    
    slide_subbullet_style = ParagraphStyle(
        'SlideSubBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#4A5568'),
        leftIndent=30,
        spaceAfter=4
    )
    
    slide_section_header = ParagraphStyle(
        'SlideSectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=17,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=6,
        spaceAfter=4
    )

    story = []
    
    # Read PPT Markdown
    with open(os.path.join(REPO_ROOT, 'Final_SmartInterview_PPT.md'), 'r', encoding='utf-8') as f:
        ppt_md = f.read()

    slides = ppt_md.split('---')
    for idx, slide_raw in enumerate(slides):
        slide_text = slide_raw.strip()
        if not slide_text:
            continue
        
        lines = [l.strip() for l in slide_text.split('\n') if l.strip()]
        if not lines:
            continue
            
        # Parse title
        title_line = lines[0]
        if title_line.startswith('## '):
            title = title_line[3:]
            content_lines = lines[1:]
        elif title_line.startswith('# '):
            title = title_line[2:]
            content_lines = lines[1:]
        else:
            title = f"Slide {idx + 1}"
            content_lines = lines
            
        story.append(Paragraph(title, slide_title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3182CE'), spaceAfter=14))
        
        def format_inline_md(text):
            if not text:
                return ""
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'`(.*?)`', r'<font face="Courier"><b>\1</b></font>', text)
            text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
            return text

        for line in content_lines:
            if line.startswith('**') and line.endswith('**'):
                story.append(Paragraph(line.replace('**', ''), slide_section_header))
            elif line.startswith('- ') or line.startswith('• '):
                story.append(Paragraph("• " + format_inline_md(line[2:]), slide_bullet_style))
            elif line.startswith('  * ') or line.startswith('   - ') or line.startswith('  - '):
                clean = re.sub(r'^\s*[-*]\s*', '', line)
                story.append(Paragraph("— " + format_inline_md(clean), slide_subbullet_style))
            else:
                story.append(Paragraph(format_inline_md(line), slide_body_style))
                
        if idx < len(slides) - 1:
            story.append(PageBreak())

    doc.build(story, canvasmaker=LandscapeSlideCanvas)
    print(f"[OK] Generated {pdf_path}")


# ==============================================================================
# 2. BUILD SRS PDF (Formal IEEE / Academic Specification PDF)
# ==============================================================================
def build_srs_pdf():
    pdf_path = os.path.join(REPO_ROOT, "SmartInterview_SRS_Final.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1A365D'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4A5568'),
        alignment=TA_CENTER,
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2D3748'),
        leftIndent=15,
        spaceAfter=4
    )
    
    caption_style = ParagraphStyle(
        'Caption',
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#4A5568'),
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=10
    )
    
    story = []
    
    # Title & Metadata
    story.append(Paragraph("SmartInterview: Personalized Technical Interview Preparation", title_style))
    story.append(Paragraph("Software Requirement Specification (SRS) | Team G-1392<br/>Department of CSE (AI & ML) — Keshav Memorial Institute of Technology (KMIT)", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=15))
    
    with open(os.path.join(REPO_ROOT, 'Final_SmartInterview_SRS.md'), 'r', encoding='utf-8') as f:
        srs_content = f.read()

    # Split mermaid vs text
    mermaid_pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
    parts = mermaid_pattern.split(srs_content)
    
    mermaid_img_idx = 0
    diagram_captions = [
        "Figure 1: High-Level System Use Case Diagram (Candidate & Core Services)",
        "Figure 2: Sequence Diagram of Adaptive Interview Session & Answer Evaluation",
        "Figure 3: System Class Diagram (Domain Models & Relational Entities)",
        "Figure 4: Finite State Machine Diagram for Bloom's Revised Taxonomy Progression",
        "Figure 5: Activity Diagram of Candidate End-to-End Interview Lifecycle",
        "Figure 6: Entity-Relationship Diagram (ERD: Users, Sessions, Transcripts)",
        "Figure 7: Physical Deployment Diagram (React SPA, FastAPI, MySQL, ChromaDB, Groq, Edge-TTS)"
    ]
    
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Mermaid diagram
            img_file = f"mermaid_diagram_{mermaid_img_idx}.png"
            full_img_path = os.path.join(REPO_ROOT, img_file)
            if os.path.exists(full_img_path):
                try:
                    pil_img = Image.open(full_img_path)
                    w, h = pil_img.size
                    aspect = h / float(w)
                    target_w = 480
                    target_h = target_w * aspect
                    if target_h > 350:
                        target_h = 350
                        target_w = target_h / aspect
                        
                    story.append(Spacer(1, 6))
                    story.append(RLImage(full_img_path, width=target_w, height=target_h))
                    cap = diagram_captions[mermaid_img_idx] if mermaid_img_idx < len(diagram_captions) else f"Figure: UML Diagram {mermaid_img_idx+1}"
                    story.append(Paragraph(f"<b>{cap}</b>", caption_style))
                except Exception as e:
                    story.append(Paragraph(f"<i>[Diagram: {img_file}]</i>", caption_style))
            mermaid_img_idx += 1
        else:
            # Normal markdown text
            lines = part.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('# Software Requirement Specification') or 'Team G-1392' in line:
                    continue
                if line.startswith('# '):
                    story.append(Paragraph(line[2:].replace('**', ''), h1_style))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:].replace('**', ''), h1_style))
                elif line.startswith('### '):
                    story.append(Paragraph(line[4:].replace('**', ''), h2_style))
                elif line.startswith('- ') or line.startswith('* '):
                    story.append(Paragraph("• " + format_inline_md(line[2:]), bullet_style))
                elif line.startswith('|') and '|' in line[1:]:
                    # Table row representation
                    cols = [c.strip() for c in line.split('|')[1:-1]]
                    if cols and not all(c.startswith('---') for c in cols):
                        row_text = " | ".join(cols)
                        story.append(Paragraph(f"<code>{row_text}</code>", body_style))
                else:
                    story.append(Paragraph(format_inline_md(line), body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated {pdf_path}")


# ==============================================================================
# 3. BUILD RESEARCH PAPER PDF (IEEE Conference Style)
# ==============================================================================
def build_research_paper_pdf():
    pdf_path = os.path.join(REPO_ROOT, "SmartInterview_Research_Paper_Final.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=48
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'PaperTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    author_style = ParagraphStyle(
        'Authors',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    abstract_heading = ParagraphStyle(
        'AbstractHeading',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=4
    )
    
    abstract_body = ParagraphStyle(
        'AbstractBody',
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_JUSTIFY,
        leftIndent=15,
        rightIndent=15,
        spaceAfter=10
    )
    
    sec_heading = ParagraphStyle(
        'SecHeading',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    subsec_heading = ParagraphStyle(
        'SubSecHeading',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    paper_body = ParagraphStyle(
        'PaperBody',
        fontName='Times-Roman',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )
    
    paper_bullet = ParagraphStyle(
        'PaperBullet',
        fontName='Times-Roman',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=12,
        spaceAfter=3
    )

    story = []
    
    story.append(Paragraph("Personalized Technical Interview Preparation in Higher Education Using Retrieval-Augmented Generation and Bloom's Taxonomy", title_style))
    story.append(Paragraph(
        "<b>Shamakura Saiteja Goud, Thodsam Srujan, Vasireddy Vignesh Reddy, Aelugu Ranith Kumar, Konduri Abhiram</b><br/>"
        "Faculty Mentor: <b>Dr. TVG Sridevi</b> (tvgsridevi@kmit.in)<br/>"
        "Department of Computer Science and Engineering (AI&ML), Keshav Memorial Institute of Technology (KMIT)<br/>"
        "Affiliated to Jawaharlal Nehru Technological University Hyderabad (JNTUH) | Team ID: Team G-1392",
        author_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94A3B8'), spaceAfter=10))

    # Read research paper markdown
    rp_file = os.path.join(REPO_ROOT, "SmartInterview_Progressive_Updates", "03_Research_Paper", "SmartInterview_Research_Paper_IEEE_v2.md")
    with open(rp_file, 'r', encoding='utf-8') as f:
        rp_lines = f.readlines()

    in_abstract = False
    for line in rp_lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith('# ') or 'Project Review Identifier' in s or 'Authors:' in s or 'Department of Computer Science' in s:
            continue
            
        if s.startswith('## Abstract'):
            in_abstract = True
            story.append(Paragraph("<b>Abstract</b>", abstract_heading))
            continue
            
        if s.startswith('**Index Terms'):
            in_abstract = False
            story.append(Paragraph(format_inline_md(s), abstract_body))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
            continue
            
        if in_abstract:
            story.append(Paragraph(format_inline_md(s), abstract_body))
            continue

        # Normal sections
        if s.startswith('## '):
            story.append(Paragraph(s[3:].replace('**', ''), sec_heading))
        elif s.startswith('### '):
            story.append(Paragraph(s[4:].replace('**', ''), subsec_heading))
        elif s.startswith('- ') or s.startswith('* '):
            story.append(Paragraph("• " + format_inline_md(s[2:]), paper_bullet))
        elif s.startswith('|') and '|' in s[1:]:
            cols = [c.strip() for c in s.split('|')[1:-1]]
            if cols and not all(c.startswith('---') for c in cols):
                story.append(Paragraph(f"<code>{' | '.join(cols)}</code>", paper_body))
        else:
            story.append(Paragraph(format_inline_md(s), paper_body))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated {pdf_path}")


# ==============================================================================
# 4. BUILD EXPLANATION PDF (Master Review & Defense Guide)
# ==============================================================================
def build_explanation_pdf():
    pdf_path = os.path.join(REPO_ROOT, "SmartInterview_Master_Explanation_and_Defense_Guide.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    cover_subtitle = ParagraphStyle(
        'CoverSubTitle',
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER,
        spaceAfter=25
    )
    
    sec_title = ParagraphStyle(
        'SecTitle',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    subsec_title = ParagraphStyle(
        'SubSecTitle',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#0284C7'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    bullet = ParagraphStyle(
        'Bullet',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=15,
        spaceAfter=4
    )
    
    code_box = ParagraphStyle(
        'CodeBox',
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0F172A'),
        leftIndent=10,
        spaceAfter=4
    )

    story = []
    
    # Title Page
    story.append(Paragraph("SmartInterview: Master Technical Explanation & Academic Review Guide", cover_title))
    story.append(Paragraph(
        "A Complete Spoken Defense, Mathematical Framework, Literature Survey, and Image Verification Reference<br/>"
        "<b>Team ID: Team G-1392</b> | Department of Computer Science & Engineering (AI & ML)<br/>"
        "Keshav Memorial Institute of Technology (KMIT) — Mentored by Dr. TVG Sridevi",
        cover_subtitle
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceAfter=15))

    # SECTION 1: Executive Overview
    story.append(Paragraph("1. Executive Overview & Core Problem Statement", sec_title))
    story.append(Paragraph(
        "Technical interviews for campus placement recruitment drives present a severe systemic barrier for engineering students. "
        "Graduating seniors struggle with severe interview anxiety, a lack of experience in verbalizing technical solutions, and a stark disconnect between standard university curricula and dynamic job descriptions. "
        "Traditional preparation tools (such as LeetCode or static question banks) test algorithmic code execution via unit tests but fail entirely to simulate conversational discourse. "
        "Conversely, human mock interviews are cost-prohibitive ($50–$150/hr) and unscalable for university cohorts exceeding hundreds of students.",
        body
    ))
    story.append(Paragraph(
        "<b>SmartInterview</b> bridges this gap by delivering an autonomous, context-aware technical mock interview platform that unifies: "
        "<br/>• <b>Domain-Filtered Retrieval-Augmented Generation (RAG)</b>: Grounded in 402 curated computer science chunks to eliminate hallucinations. "
        "<br/>• <b>Deterministic Cognitive Scaffolding</b>: Powered by Bloom's Revised Taxonomy (Remember through Create) to prevent unstructured topic-hopping. "
        "<br/>• <b>Multi-Signal 5-Factor Scoring</b>: Eliminates LLM 'vibe grading' with reproducible mathematical evaluation. "
        "<br/>• <b>Sub-1.2s Neural Voice Synthesis</b>: Streamed via in-memory byte buffers (io.BytesIO) to preserve natural conversational rhythm.",
        body
    ))

    # SECTION 2: Base Papers Deep Dive
    story.append(Paragraph("2. Foundational Research Papers Breakdown & Gap Analysis", sec_title))
    story.append(Paragraph("Base Paper 1: Nagarajan et al. (Feb 2026, IJMRR)", subsec_title))
    story.append(Paragraph(
        "• <b>Title:</b> <i>Development of an Autonomous AI Interview Engine Using Sentence-BERT and Large Language Models for End-to-End Candidate Evaluation</i><br/>"
        "• <b>Target Audience:</b> Enterprise recruiters, HR talent acquisition teams.<br/>"
        "• <b>Mechanism:</b> Extracts text from candidate resumes and target job descriptions; calculates dense semantic embeddings using Sentence-BERT (<code>all-MiniLM-L6-v2</code>); ranks profile relevance via cosine similarity; runs automated voice screening using Browser Web Speech STT, Cloud LLM, and Cloud TTS.<br/>"
        "• <b>Critical Gaps:</b> Designed exclusively as a recruiter gatekeeper to filter people out; provides zero candidate diagnostic reports or upskilling roadmaps; no live coding verification; volatile session state.",
        body
    ))
    story.append(Paragraph("Base Paper 2: Wahid et al. (March 2026, IJERT)", subsec_title))
    story.append(Paragraph(
        "• <b>Title:</b> <i>AI Mock Interview: An Intelligent Voice-Driven Interview Simulation System using Gemini AI and Whisper</i><br/>"
        "• <b>Target Audience:</b> University students and job seekers practicing for interviews.<br/>"
        "• <b>Mechanism:</b> Streamlit application + Gemini API; takes PDF resume via PyPDF2 and candidate selects 1 of 6 generic technical domains; captures audio at 16 kHz and transcribes via OpenAI Whisper base model; outputs structured evaluation to ReportLab PDF with radar charts.<br/>"
        "• <b>Critical Gaps:</b> Strictly one-way voice interaction (ASR input only; no TTS speech output—students must read text off the screen); rigid domain dropdowns without custom JD matching; Streamlit session volatility.",
        body
    ))

    # SECTION 3: Mathematical Metrics & Rationale
    story.append(Paragraph("3. Empirical Metrics & Why We Chose Them", sec_title))
    story.append(Paragraph("A. RAG Retrieval Metrics (33 Technical Domain Queries)", subsec_title))
    story.append(Paragraph(
        "• <b>Hit@1 = 96.97% (32/33):</b> Meaning the exact, single best ground-truth technical reference from our 402 curated CS topic summaries is retrieved as the #1 match nearly 97% of the time.<br/>"
        "• <b>Hit@3 = 100.00% (33/33):</b> In 100% of cases, the relevant reference text is contained within the top-3 retrieved chunks.<br/>"
        "• <b>Mean Reciprocal Rank (MRR) = 0.9798:</b> Measures the average reciprocal rank of the first relevant chunk ($1/rank$). A score of ~0.98 mathematically proves that the retriever almost never misplaces the target technical concept deep down in irrelevant context.<br/>"
        "• <b>Mean Retrieval Latency = 24.6 ms:</b> Sub-100ms vector search executed entirely locally via ChromaDB HNSW indexing.",
        body
    ))
    story.append(Paragraph("B. Objective 5-Signal Scoring Rubric (Eliminating 'Vibe Grading')", subsec_title))
    story.append(Paragraph(
        "Standard LLMs suffer from 'vibe grading'—giving inconsistent scores based on prompt temperature or superficial eloquence. SmartInterview enforces a strict mathematical formula: "
        "<br/><code>Score = 0.30 * Technical + 0.20 * Completeness + 0.20 * Relevance + 0.15 * SBERT_Cosine + 0.15 * Concept_Coverage</code><br/>"
        "• <b>30% Technical Correctness:</b> LLM logical reasoning and factual accuracy.<br/>"
        "• <b>20% Completeness:</b> Adherence to question constraints and addressing all sub-problems.<br/>"
        "• <b>20% Relevance:</b> Conciseness, directness, and lack of conversational filler.<br/>"
        "• <b>15% SBERT Cosine Similarity:</b> Local Sentence-BERT embedding similarity against the verified textbook answer key.<br/>"
        "• <b>15% Explicit Concept Coverage:</b> Deterministic extraction confirming key technical entities and keywords are articulated.",
        body
    ))
    story.append(Paragraph("C. Bloom's Taxonomy Progression Thresholds", subsec_title))
    story.append(Paragraph(
        "• <b>Score >= 80% (Mastery):</b> Advance to the next cognitive level (e.g., from Understand to Apply) or advance difficulty tier.<br/>"
        "• <b>Score 50% - 79% (Adequate):</b> Maintain the current Bloom level and difficulty tier.<br/>"
        "• <b>Score < 50% (Remediation):</b> Regress Bloom level (-1) to reinforce foundational principles.",
        body
    ))
    story.append(Paragraph("D. Latency Benchmarks", subsec_title))
    story.append(Paragraph(
        "• <b>Voice Synthesis Latency <= 1.2s:</b> Achieved via in-memory <code>io.BytesIO</code> streaming with Microsoft Edge-TTS, bypassing disk I/O bottlenecks.<br/>"
        "• <b>Total End-to-End Turnaround < 2.5s:</b> Groq Cloud LPU delivers a Time-to-First-Token (TTFT) of ~320ms, preventing awkward pauses during live mock interviews.",
        body
    ))

    # SECTION 4: Image Verification & Latest Commit Audit
    story.append(Paragraph("4. System Diagram & Image Verification (Latest Commit on Main)", sec_title))
    story.append(Paragraph(
        "Audit conducted against GitHub <code>main</code> branch latest commit (<code>b298c44db6326a42af5770ee354cbe1b664c6d0b</code>):",
        body
    ))
    
    diagram_table_data = [
        ["Diagram / Asset Name", "File Path", "Dimensions & Size", "Label & Deliverables Reference", "Verification Status"],
        ["System Architecture", "05_System_Diagrams/Architecture.png", "840x523 | 32.1 KB", "SRS Fig 2.1, PPT Slide 4, Paper Fig 1", "VERIFIED (100% Coherent)"],
        ["Entity Relationship (ERD)", "05_System_Diagrams/ERD.png", "462x1101 | 44.2 KB", "SRS Fig 2.2, Encyclopedia Part 5", "VERIFIED (100% Coherent)"],
        ["Interview Execution Workflow", "05_System_Diagrams/Workflow.png", "980x809 | 60.1 KB", "SRS Fig 2.3, PPT Slide 5, Paper Fig 2", "VERIFIED (100% Coherent)"],
        ["Frontend Hero Banner", "frontend/src/assets/hero.png", "343x361 | 13.0 KB", "Landing Page UI Illustration", "VERIFIED (100% Coherent)"],
        ["Favicon Icon", "frontend/public/favicon.svg", "Vector SVG | 9.5 KB", "Browser Tab Navigation Icon", "VERIFIED (100% Coherent)"],
        ["System Icons Sprite", "frontend/public/icons.svg", "Vector SVG | 5.0 KB", "Action Icons (Mic, Volume, Stats)", "VERIFIED (100% Coherent)"]
    ]
    t = Table(diagram_table_data, colWidths=[110, 140, 95, 120, 75])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('LEADING', (0,0), (-1,-1), 9.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Embed Architecture Image
    arch_path = os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "05_System_Diagrams", "Architecture.png")
    if os.path.exists(arch_path):
        story.append(RLImage(arch_path, width=420, height=261))
        story.append(Paragraph("<b>Figure: Decoupled 4-Tier Distributed System Architecture</b>", ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, alignment=TA_CENTER, spaceBefore=4, spaceAfter=10)))

    # SECTION 5: Spoken Presentation Script
    story.append(Paragraph("5. Spoken-Word Presentation Script for Academic Defense", sec_title))
    spoken_script_paras = [
        "Good morning, respected members of the panel. When engineering students prepare for campus placements, technical interviews are consistently the highest hurdle they face. While mock interviews are proven to reduce anxiety and build confidence, human mock interviews are expensive to scale, and static question banks simply cannot simulate a real, dynamic conversation. Today, I will be presenting a comparative review of two foundational 2026 research papers in this domain, and showing how our project, SmartInterview, directly overcomes their architectural limitations to build a grounded, adaptive, and deterministic interview coach.",
        "Let us begin with Paper 1, published by Nagarajan and colleagues in February 2026. Their work is built primarily for enterprise recruiters and HR talent acquisition teams looking to automate candidate screening. Their workflow begins with the candidate’s PDF resume and a specific job description. The system parses both documents and uses Sentence-BERT—specifically the all-MiniLM-L6-v2 model—to generate dense semantic vectors. By calculating the cosine similarity between the resume and the job description, it automatically measures how well an applicant’s profile matches the job requirements. A Flask backend then drives an autonomous, two-way voice interview using the browser’s Web Speech API for speech-to-text, a cloud LLM to generate adaptive questions, and cloud text-to-speech to speak to the candidate. When the interview ends, the LLM evaluates the transcript across technical proficiency, communication, and project depth, presenting the results on a recruiter web dashboard. While this is an impressive corporate pipeline, its limitations stem directly from its recruiter-first design. It functions as an exclusionary gatekeeper—designed to filter people out rather than help students improve. As a result, it provides no offline diagnostic reports or upskilling roadmaps for candidates. It lacks any live code execution sandbox to verify practical claims, and its session state is held in volatile memory, meaning any network hiccup drops the session entirely.",
        "Turning to Paper 2, published by Wahid and colleagues in March 2026, we see an approach centered on student preparation. Here, the candidate uploads a PDF resume using PyPDF2 and chooses one of six broad technical domains, such as Machine Learning or Cloud Computing. Built on Streamlit and powered by the Gemini API, the platform runs an adaptive loop of eight to twelve questions. For voice capture, it records audio at 16 kilohertz using SoundDevice and transcribes it using OpenAI’s Whisper base model. Whisper is a strong choice here because it handles diverse accents and technical jargon with exceptional accuracy. At the end of the session, Gemini generates a structured JSON evaluation scoring overall performance, technical depth, communication, and problem-solving. This feeds into ReportLab, which auto-generates a clean, downloadable multi-page PDF report complete with skill radar charts and tailored learning roadmaps. However, Paper 2 has two major flaws. First, the voice experience is strictly one-way. Whisper transcribes the candidate's speech, but the AI never speaks back—the student is forced to read questions off the screen, which breaks the realism of a spoken interview. Second, it lacks custom job description matching; students are restricted to rigid domain dropdowns, meaning they cannot tailor their practice to a specific company or job posting.",
        "When we place both papers side-by-side, we see a stark trade-off: Paper 1 offers custom job description matching and full two-way voice, but locks all feedback inside an HR dashboard designed to screen candidates out. Paper 2 puts the student first with accent-robust Whisper input and a downloadable PDF roadmap, but it removes audio output entirely and forces candidates into generic domain dropdowns. Moreover, both papers share critical vulnerabilities: they rely on volatile in-memory runtimes, their LLMs are prone to unverified hallucinations, and their scoring depends on single-prompt black-box LLM evaluation—what we call 'vibe grading.'",
        "This brings us to SmartInterview. We engineered our platform to bridge this exact divide by combining student-centered pedagogy with deterministic, low-latency AI. First, we attacked the problem of AI hallucinations at its foundation using Retrieval-Augmented Generation, or RAG, backed by ChromaDB over a curated knowledge base of 402 computer science topic summaries across eight domains. Our retrieval pipeline achieved a Hit at 1 of 96.97%, a Hit at 3 of 100%, and an MRR of 0.9798. In plain English, Hit at 1 means that nearly 97% of the time, the exact, verified textbook reference needed for a question is retrieved as the single top match. A Hit at 3 of 100% means the ground truth is guaranteed to be in the top three results. And an MRR of nearly 0.98 mathematically proves that relevant context consistently appears at the very top of the list.",
        "Second, we eliminated black-box 'vibe grading.' We replaced subjective marks with an objective, five-part scoring rubric: 30% Technical Correctness, 20% Completeness, 20% Relevance, 15% SBERT Cosine Similarity against our ground-truth reference, and 15% Explicit Concept Coverage. We chose this split because semantic similarity ensures the candidate explained the underlying concept correctly, while concept coverage verifies that critical technical keywords and mechanisms were explicitly articulated. Third, we resolved unstructured topic-hopping by implementing a stateful cognitive engine powered by Bloom’s Revised Taxonomy. Real interviewers don’t jump erratically between trivia and architectural design; they probe deeper. Our system scaffolds dynamically—starting from foundational recall and advancing up through Apply, Analyze, and Create when a candidate demonstrates mastery with scores of 80% or higher, while stepping back to reinforce fundamentals if a score dips below 50%. Fourth, to deliver true two-way conversational immersion without awkward pauses, we engineered an in-memory neural voice synthesis pipeline using io.BytesIO, achieving a voice latency of 1.2 seconds or less, and total end-to-end turnaround under 2.5 seconds. Finally, SmartInterview provides three targeted operational modes: Job-Specific Mode, Topic-Based Mode, and Semester Syllabus Mode with dynamic collection isolation. In conclusion, while previous research treats the AI interview either as an exclusionary corporate screening filter or a silent web form, SmartInterview transforms it into a grounded, low-latency, and pedagogically sound training ground that empowers students to succeed. Thank you, and I am now ready to take your questions."
    ]
    for p_text in spoken_script_paras:
        story.append(Paragraph(p_text, body))
        story.append(Spacer(1, 4))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Generated {pdf_path}")


if __name__ == "__main__":
    print("Building all 4 deliverable PDFs...")
    build_presentation_pdf()
    build_srs_pdf()
    build_research_paper_pdf()
    build_explanation_pdf()
    print("All PDFs generated successfully!")
