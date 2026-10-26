import sys
import os
import re
import base64
import requests
import time

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("python-docx not installed.")
    sys.exit(1)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIAGRAM_DIR = os.path.join(REPO_ROOT, "docs", "diagrams", "mermaid")
OUT_DIR = os.path.join(REPO_ROOT, "docs", "final_deliverables")
DELIV_DIR = os.path.join(REPO_ROOT, "SmartInterview_Deliverables", "02_SRS_Specification")
os.makedirs(DIAGRAM_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DELIV_DIR, exist_ok=True)


def encode_mermaid(mermaid_text):
    return base64.b64encode(mermaid_text.encode('utf8')).decode('ascii')


def download_mermaid_image(mermaid_text, filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        return True
    b64 = encode_mermaid(mermaid_text)
    url = f'https://mermaid.ink/img/{b64}'
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
        else:
            print(f"Failed to download image from mermaid.ink: {r.status_code}")
    except Exception as e:
        print(f"Exception downloading image: {e}")
    return False


def generate_docx():
    doc = Document()
    doc.add_heading('Software Requirement Specification (SRS)', 0)

    srs_file = os.path.join(REPO_ROOT, 'Final_SmartInterview_SRS.md')
    try:
        with open(srs_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"{srs_file} not found.")
        return

    # Extract mermaid blocks
    mermaid_pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
    parts = mermaid_pattern.split(content)
    img_counter = 0

    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Mermaid block
            mermaid_text = part.strip()
            filename = os.path.join(DIAGRAM_DIR, f'mermaid_diagram_{img_counter}.png')
            if download_mermaid_image(mermaid_text, filename):
                try:
                    doc.add_picture(filename, width=Inches(5.5))
                    doc.add_paragraph()
                except Exception as e:
                    print(f"Error adding picture {filename}: {e}")
            else:
                doc.add_paragraph("[Failed to render UML diagram as image. Source code below:]")
                doc.add_paragraph(mermaid_text)
            img_counter += 1
        else:
            # Standard markdown
            lines = part.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('!['):
                    m = re.match(r'!\[(.*?)\]\((.*?)\)', line)
                    if m:
                        img_path = m.group(2).strip()
                        if img_path.startswith('file:///'):
                            img_path = img_path[8:]
                        # On Windows, path might be c:/Users/...
                        img_path = os.path.normpath(img_path)
                        if os.path.exists(img_path):
                            try:
                                doc.add_picture(img_path, width=Inches(5.5))
                                cap = doc.add_paragraph(m.group(1))
                                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            except Exception as e:
                                print(f"Error embedding picture {img_path}: {e}")
                        continue

                if line.startswith('### '):
                    doc.add_heading(line[4:].replace('**', ''), level=3)
                elif line.startswith('## '):
                    doc.add_heading(line[3:].replace('**', ''), level=2)
                elif line.startswith('# '):
                    doc.add_heading(line[2:].replace('**', ''), level=1)
                elif line.startswith('- '):
                    doc.add_paragraph(line[2:].replace('**', ''), style='List Bullet')
                elif line.startswith('*Fig'):
                    p = doc.add_paragraph(line.replace('*', ''))
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif line.startswith('|'):
                    doc.add_paragraph(line.replace('**', ''))
                else:
                    doc.add_paragraph(line.replace('**', ''))

    out_file1 = os.path.join(OUT_DIR, 'SmartInterview_SRS_Final.docx')
    out_file2 = os.path.join(DELIV_DIR, 'SmartInterview_SRS_Template_Format.docx')
    try:
        doc.save(out_file1)
        doc.save(out_file2)
        print(f"[SUCCESS] Saved DOCX to:\n  1. {out_file1}\n  2. {out_file2}")
    except PermissionError as e:
        print(f"PERMISSION DENIED: Please close DOCX before running: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Generating perfect DOCX with native UML images and UI screenshots...")
    generate_docx()
    print("Done.")
