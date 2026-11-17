from pathlib import Path
import win32com.client

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "deliverables" / "Admin-Panel-Firma-Hukum.pptx"
OUTDIR = ROOT / "deliverables" / "preview"
OUTDIR.mkdir(parents=True, exist_ok=True)

app = win32com.client.Dispatch("PowerPoint.Application")
try:
    pres = app.Presentations.Open(str(DECK), ReadOnly=True, Untitled=False, WithWindow=False)
    try:
        for i in range(1, pres.Slides.Count + 1):
            pres.Slides(i).Export(str(OUTDIR / f"slide{i:02d}.png"), "PNG", 1280, 720)
        print(f"exported {pres.Slides.Count} slides")
    finally:
        pres.Close()
finally:
    app.Quit()
