import os
import sys
import re
import shutil
from PIL import Image

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PDF_DELIV_DIR = os.path.join(REPO_ROOT, "PDF_Deliverables")
PDF_DELIV_DIR_ALT = os.path.join(REPO_ROOT, "SmartInterview_PDF_Deliverables")

os.makedirs(PDF_DELIV_DIR, exist_ok=True)
os.makedirs(PDF_DELIV_DIR_ALT, exist_ok=True)


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
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SmartInterview — Academic Review & Technical Defense")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            self.drawString(54, 36, "Keshav Memorial Institute of Technology (KMIT) — Team G-1392")
            self.drawRightString(558, 36, f"Page {self._pageNumber} of {page_count}")
            self.line(54, 48, 558, 48)
        self.restoreState()


def md_to_reportlab(text):
    if not text:
        return ""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.*?)`", r'<font face="Courier" color="#1E293B"><b>\1</b></font>', text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def convert_md_to_pdf(md_file, pdf_file, doc_title):
    print(f"Compiling PDF: {pdf_file} from {os.path.basename(md_file)}...")
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TStyle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=TA_CENTER,
        spaceAfter=8
    )
    h1 = ParagraphStyle(
        'H1Style',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    h2 = ParagraphStyle(
        'H2Style',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor('#0284C7'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    body = ParagraphStyle(
        'BStyle',
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    bullet = ParagraphStyle(
        'BulStyle',
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=12,
        spaceAfter=2
    )
    caption = ParagraphStyle(
        'CapStyle',
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER,
        spaceAfter=6
    )

    story = [
        Paragraph(doc_title, title_style),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284C7'), spaceAfter=12)
    ]

    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", s)
            if m:
                img_p = m.group(2).strip()
                if img_p.startswith("file:///"):
                    img_p = img_p[8:]
                img_p = os.path.normpath(img_p)
                if os.path.exists(img_p):
                    try:
                        pimg = Image.open(img_p)
                        w, h = pimg.size
                        asp = h / float(w)
                        tw = 460
                        th = min(260, tw * asp)
                        tw = th / asp
                        story.append(Spacer(1, 4))
                        story.append(RLImage(img_p, width=tw, height=th))
                        story.append(Paragraph(f"<b>{m.group(1)}</b>", caption))
                        story.append(Spacer(1, 4))
                    except Exception as e:
                        print("Error adding image:", e)
            continue
        if s.startswith("## "):
            story.append(Paragraph(md_to_reportlab(s[3:]), h1))
        elif s.startswith("### "):
            story.append(Paragraph(md_to_reportlab(s[4:]), h2))
        elif s.startswith("# "):
            story.append(Paragraph(md_to_reportlab(s[2:]), h1))
        elif s.startswith("- ") or s.startswith("* "):
            story.append(Paragraph("• " + md_to_reportlab(s[2:]), bullet))
        elif s.startswith("*Fig"):
            story.append(Paragraph(md_to_reportlab(s), caption))
        elif s.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=8, spaceBefore=4))
        else:
            story.append(Paragraph(md_to_reportlab(s), body))

    os.makedirs(os.path.dirname(pdf_file), exist_ok=True)
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Saved: {pdf_file} ({os.path.getsize(pdf_file)} bytes)")


def main():
    # 1. First run the existing generator for SRS, Presentation, Paper, and Guide
    import subprocess
    gen_script = os.path.join(REPO_ROOT, "scripts", "generators", "generate_all_final_pdfs.py")
    subprocess.run([sys.executable, gen_script], check=True)

    # 2. Build Cheatsheet PDF
    md_cheat = os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "01_Documentation_and_Viva", "SmartInterview_Quick_Revision_Cheatsheet.md")
    pdf_cheat = os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "01_Documentation_and_Viva", "SmartInterview_Quick_Revision_Cheatsheet.pdf")
    convert_md_to_pdf(md_cheat, pdf_cheat, "SmartInterview: Quick-Revision Cheatsheet & Viva Defense Card")

    # 3. Build 5-Member Plan PDF
    md_plan = os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "04_Presentation_and_Defense", "SmartInterview_5_Member_Presentation_Plan.md")
    pdf_plan = os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "04_Presentation_and_Defense", "SmartInterview_5_Member_Presentation_Plan.pdf")
    convert_md_to_pdf(md_plan, pdf_plan, "SmartInterview: 5-Member Presentation & Defense Plan")

    # 4. Map of all master deliverables to copy into the dedicated PDF_Deliverables folders
    pdf_map = {
        "01_SmartInterview_Software_Requirements_Specification_SRS.pdf": os.path.join(REPO_ROOT, "docs", "final_deliverables", "SmartInterview_SRS_Final.pdf"),
        "02_SmartInterview_Project_Presentation_Slides.pdf": os.path.join(REPO_ROOT, "docs", "final_deliverables", "SmartInterview_Presentation_Final.pdf"),
        "03_SmartInterview_IEEE_Research_Paper.pdf": os.path.join(REPO_ROOT, "docs", "final_deliverables", "SmartInterview_Research_Paper_Final.pdf"),
        "04_SmartInterview_Master_Explanation_and_Defense_Guide.pdf": os.path.join(REPO_ROOT, "docs", "final_deliverables", "SmartInterview_Master_Explanation_and_Defense_Guide.pdf"),
        "05_SmartInterview_Quick_Revision_Cheatsheet.pdf": pdf_cheat,
        "06_SmartInterview_5_Member_Presentation_Plan.pdf": pdf_plan,
        "07_SmartInterview_Master_Encyclopedia_and_Viva_Defense.pdf": os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "01_Documentation_and_Viva", "SmartInterview_Master_Encyclopedia_and_Viva_Defense.pdf")
    }

    print("\n--- Synchronizing all PDFs into dedicated folders: 'PDF_Deliverables' & 'SmartInterview_PDF_Deliverables' ---")
    for clean_name, src_path in pdf_map.items():
        if os.path.exists(src_path):
            dst1 = os.path.join(PDF_DELIV_DIR, clean_name)
            dst2 = os.path.join(PDF_DELIV_DIR_ALT, clean_name)
            shutil.copyfile(src_path, dst1)
            shutil.copyfile(src_path, dst2)
            print(f"  [OK] Copied: {clean_name} ({os.path.getsize(dst1)} bytes)")
        else:
            print(f"  [MISSING] Missing source: {src_path}")

    print("\n[ALL PDF DELIVERABLES SUCCESSFULLY COMPILED AND STORED!]")


if __name__ == "__main__":
    main()
