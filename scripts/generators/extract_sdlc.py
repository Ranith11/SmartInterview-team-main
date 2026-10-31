from docx import Document

doc = Document('SmartInterview_SRS_Final_Template.docx')
in_sdlc = False

print("--- SDLC TEXT ---")
for p in doc.paragraphs:
    if p.style and p.style.name and p.style.name.startswith('Heading 1'):
        if 'Life Cycle' in p.text:
            in_sdlc = True
            print(f"[{p.style.name}] {p.text}")
            continue
        elif in_sdlc:
            # We reached the next Heading 1
            break
            
    if in_sdlc:
        if p.text.strip():
            print(p.text)
