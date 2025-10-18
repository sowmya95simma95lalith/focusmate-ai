from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pypandoc

def export_plan_pdf(plan_text, filename="plan.pdf"):
    """
    Save AI plan as PDF.
    """
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []

    for line in plan_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 10))
    doc.build(story)
    return filename

def export_plan_md(plan_text, filename="plan.md"):
    """
    Save AI plan as Markdown using pandoc.
    """
    output = pypandoc.convert_text(plan_text, "md", format="md", extra_args=['--standalone'])
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    return filename
