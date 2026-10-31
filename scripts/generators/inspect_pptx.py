from pptx import Presentation
import sys

def inspect_template():
    try:
        prs = Presentation('PS_Project_Presentation_Template_1.0_01Sep2026(1).pptx')
    except Exception as e:
        print(f"Error opening PPTX: {e}")
        return

    print(f"Number of slide layouts: {len(prs.slide_layouts)}")
    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout {i}: {layout.name}")
        for j, shape in enumerate(layout.placeholders):
            print(f"  Placeholder {j} (idx={shape.placeholder_format.idx}): {shape.name} ({shape.placeholder_format.type})")

if __name__ == "__main__":
    inspect_template()
