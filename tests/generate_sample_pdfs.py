"""
Generates test_samples/<Category>/sample_XX.pdf for all four contract
categories from the synthetic text bank in sample_texts.py.

Usage:
    pip install reportlab   # if not already installed
    python tests/generate_sample_pdfs.py

Produces ~15 PDFs per category (60 total) under test_samples/, which
evaluate_categories.py then runs through the pipeline's PDF extraction
and document-category classifier to measure accuracy.
"""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from sample_texts import get_all_samples

OUT_ROOT = Path(__file__).resolve().parent.parent / "test_samples"


def _write_pdf(text: str, out_path: Path) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    story = []
    for para in re.split(r"\n\s*\n", text.strip()):
        clean = para.strip().replace("\n", "<br/>")
        if not clean:
            continue
        story.append(Paragraph(clean, styles["Normal"]))
        story.append(Spacer(1, 10))
    doc.build(story)


def main() -> None:
    samples = get_all_samples()
    total = 0
    for category, texts in samples.items():
        folder = OUT_ROOT / category.replace(" ", "_")
        folder.mkdir(parents=True, exist_ok=True)
        for idx, text in enumerate(texts, 1):
            out_path = folder / f"sample_{idx:02d}.pdf"
            _write_pdf(text, out_path)
            total += 1
        print(f"{category}: {len(texts)} PDFs -> {folder}")
    print(f"Done. Wrote {total} PDFs total under {OUT_ROOT}")


if __name__ == "__main__":
    main()
