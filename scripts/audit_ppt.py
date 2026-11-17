"""Structural audit: slide bounds, rough text fit, and placeholder scan."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "deliverables" / "Admin-Panel-Firma-Hukum.pptx"
W_PX, H_PX = 1280, 720
EMU_PER_PX = 9525

prs = Presentation(DECK)
issues = []


def px(value):
    return round(Emu(value).emu / EMU_PER_PX, 1)


def est_lines(text, width_px, size_pt):
    if not text.strip():
        return 0
    char_px = size_pt * 0.56  # rough average for Latin body text
    per_line = max(1, int(width_px / max(char_px, 1)))
    lines = 0
    for raw in text.split("\n"):
        lines += max(1, -(-len(raw) // per_line))
    return lines


def check_text_frame(shape, slide_no, label):
    text = shape.text_frame.text
    if any(token in text.upper() for token in ("TBD", "TODO", "LOREM", "XX%")):
        issues.append(f"slide {slide_no}: placeholder text in {label}: {text[:60]!r}")
    total_h = 0
    for p in shape.text_frame.paragraphs:
        size = max((r.font.size.pt for r in p.runs if r.font.size), default=0)
        if size <= 0:
            continue
        lines = est_lines("".join(r.text for r in p.runs), px(shape.width), size)
        spacing = p.line_spacing or 1.0
        total_h += lines * size * 1.2 * spacing
        total_h += (p.space_after.pt if p.space_after else 0)
    box_h = px(shape.height)
    box_w = px(shape.width)
    if total_h > box_h * 1.08:
        issues.append(
            f"slide {slide_no}: possible vertical overflow in {label} "
            f"(need ~{total_h:.0f}px, box {box_h:.0f}px): {text[:70]!r}"
        )
    if box_w <= 0 or box_h <= 0:
        issues.append(f"slide {slide_no}: zero-size text box {label}")


for idx, slide in enumerate(prs.slides, start=1):
    for shape in slide.shapes:
        x, y = px(shape.left), px(shape.top)
        w, h = px(shape.width), px(shape.height)
        if x < -1 or y < -1 or x + w > W_PX + 1 or y + h > H_PX + 1:
            issues.append(f"slide {idx}: {shape.shape_type} out of bounds ({x},{y},{w},{h})")
        if shape.has_text_frame:
            check_text_frame(shape, idx, f"{shape.shape_type}@({x:.0f},{y:.0f})")
        if shape.has_table:
            table = shape.table
            for r_idx, row in enumerate(table.rows):
                for c_idx, cell in enumerate(row.cells):
                    col_w = px(table.columns[c_idx].width) - 22
                    row_h = px(row.height) - 8
                    size = 10
                    for p in cell.text_frame.paragraphs:
                        for run in p.runs:
                            if run.font.size:
                                size = run.font.size.pt
                    lines = est_lines(cell.text, col_w, size)
                    need = lines * size * 1.2
                    if need > row_h * 1.1:
                        issues.append(
                            f"slide {idx}: table cell {r_idx},{c_idx} may overflow "
                            f"(need ~{need:.0f}px, row {row_h:.0f}px): {cell.text[:40]!r}"
                        )

print(f"slides: {len(prs.slides)}")
print(f"issues: {len(issues)}")
for item in issues:
    print("-", item)
