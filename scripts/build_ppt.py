"""Build the law-firm admin panel highlight deck (Indonesian, 14 slides)."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "Admin-Panel-Firma-Hukum.pptx"

# Palette: one primary (gold) + one secondary (steel) accent.
NAVY_DARK = "0B1622"
NAVY = "0F1E2E"
NAVY_DATA = "122436"
CARD = "17293B"
CARD_ALT = "1C3146"
BORDER = "2B4258"
TEXT = "F4EFE6"
MUTED = "A9B7C5"
GOLD = "C9A45C"
GOLD_DARK = "7A5F32"
STEEL = "6E93A8"

TITLE_FONT = "Georgia"
BODY_FONT = "Segoe UI"


def px(v):
    return Pt(v * 0.75)  # 1 px at 96 dpi = 0.75 pt


def rgb(value):
    return RGBColor.from_string(value)


prs = Presentation()
prs.slide_width = px(1280)
prs.slide_height = px(720)
BLANK = prs.slide_layouts[6]


def new_slide(bg):
    slide = prs.slides.add_slide(BLANK)
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(bg)
    return slide


def add_rect(slide, x, y, w, h, fill=None, line=None, lw=1.0,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06, dash=None):
    shape_obj = slide.shapes.add_shape(shape, px(x), px(y), px(w), px(h))
    if fill:
        shape_obj.fill.solid()
        shape_obj.fill.fore_color.rgb = rgb(fill)
    else:
        shape_obj.fill.background()
    if line:
        shape_obj.line.color.rgb = rgb(line)
        shape_obj.line.width = Pt(lw)
        if dash is not None:
            shape_obj.line.dash_style = dash
    else:
        shape_obj.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            shape_obj.adjustments[0] = radius
        except (IndexError, ValueError):
            pass
    shape_obj.shadow.inherit = False
    return shape_obj


def add_text(slide, x, y, w, h, text, size=14, color=TEXT, bold=False,
             font=BODY_FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             italic=False, line_spacing=1.1):
    box = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    run.font.color.rgb = rgb(color)
    return box


def add_lines(slide, x, y, w, h, lines, size=13, color=MUTED, font=BODY_FONT,
              line_spacing=1.14, space_after=8, anchor=MSO_ANCHOR.TOP,
              bullet=None, bullet_color=GOLD, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for idx, line in enumerate(lines):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        if bullet:
            rb = p.add_run()
            rb.text = bullet + "  "
            rb.font.size = Pt(size)
            rb.font.bold = True
            rb.font.name = font
            rb.font.color.rgb = rgb(bullet_color)
        segments = line if isinstance(line, list) else [(line, {})]
        for text, opts in segments:
            run = p.add_run()
            run.text = text
            run.font.size = Pt(opts.get("size", size))
            run.font.bold = opts.get("bold", False)
            run.font.italic = opts.get("italic", False)
            run.font.name = opts.get("font", font)
            run.font.color.rgb = rgb(opts.get("color", color))
    return box


def add_header(slide, title, subtitle, number, kicker=None):
    if kicker:
        add_text(slide, 72, 40, 500, 18, kicker, size=9.5, color=GOLD, bold=True)
    add_text(slide, 72, 62, 1040, 56, title, size=30, color=TEXT, font=TITLE_FONT)
    add_text(slide, 72, 118, 1080, 40, subtitle, size=13.5, color=MUTED)
    add_text(slide, 1090, 40, 118, 18, "RANCANGAN", size=9.5, color=GOLD,
             bold=True, align=PP_ALIGN.RIGHT)


def add_footer(slide, number):
    add_text(slide, 72, 690, 700, 16,
             "Sistem Admin Panel Firma Hukum  ·  Rancangan 2026",
             size=8.5, color=MUTED)
    add_text(slide, 1160, 690, 48, 16, f"{number:02d}", size=8.5, color=GOLD,
             align=PP_ALIGN.RIGHT)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def card(slide, x, y, w, h, fill=CARD, line=BORDER, radius=0.06):
    return add_rect(slide, x, y, w, h, fill=fill, line=line, lw=0.75,
                    radius=radius)


# ---------------------------------------------------------------- slide 1
s = new_slide(NAVY_DARK)
add_rect(s, 880, 100, 340, 340, fill=None, line=GOLD, lw=1.1, shape=MSO_SHAPE.OVAL)
add_text(s, 930, 120, 240, 330, "4", size=200, color=GOLD,
         font=TITLE_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 72, 72, 600, 20, "RANCANGAN SISTEM  ·  2026", size=10, color=GOLD, bold=True)
add_text(s, 72, 150, 740, 190, "Admin Panel\nFirma Hukum", size=54, color=TEXT,
         font=TITLE_FONT, line_spacing=0.98)
add_text(s, 72, 356, 640, 100,
         "Satu sistem untuk attorney, klien, kasus, dan finance — dengan akses "
         "berbeda untuk empat peran.",
         size=15, color=MUTED, line_spacing=1.2)
add_text(s, 72, 596, 700, 20, "Go + MySQL + React  ·  Satu VPS  ·  Backup harian",
         size=11, color=GOLD, bold=True)
add_text(s, 72, 626, 760, 44,
         "Dokumen rancangan — bukan screenshot sistem yang sudah berjalan. "
         "Angka biaya bersifat estimasi indikatif.",
         size=9, color=MUTED, line_spacing=1.25)
add_text(s, 900, 470, 300, 20, "EMPAT PERAN", size=12, color=GOLD,
         bold=True, align=PP_ALIGN.CENTER)
add_text(s, 860, 494, 380, 20, "Direktur · CS/Admin · Finance · Lawyer",
         size=10, color=MUTED, align=PP_ALIGN.CENTER)
add_notes(s, "Deck ini merangkum tech stack, biaya, dan fitur per peran dari design spec. "
             "Semua tampilan dan angka adalah rancangan, bukan sistem produksi.")

# ---------------------------------------------------------------- slide 2
s = new_slide(NAVY)
add_header(s, "Masalah yang ingin diselesaikan",
           "Data operasional tersebar dan akses tidak berjenjang membuat pekerjaan lambat serta fee rawan bocor.",
           2, "LATAR")
card(s, 72, 190, 556, 360)
add_text(s, 108, 222, 300, 24, "Hari ini", size=16, color=GOLD, bold=True)
add_lines(s, 108, 268, 480, 250, [
    "Data attorney, klien, dan kasus tersebar di file serta percakapan.",
    "Hampir semua orang bisa melihat semua data, termasuk fee.",
    "Tagihan dan pembayaran tidak terpantau dalam satu tempat.",
], size=13, bullet="—", space_after=16)
card(s, 652, 190, 556, 360, fill=CARD_ALT)
add_text(s, 688, 222, 440, 24, "Target sistem", size=16, color=GOLD, bold=True)
add_lines(s, 688, 268, 480, 260, [
    "Satu sumber data operasional untuk seluruh firma.",
    "Empat peran dengan hak akses tegas, dicek di server.",
    "Outstanding dan pendapatan terlihat bagi Finance & Direktur.",
    "Biaya infrastruktur rendah dan perawatan sederhana.",
], size=13, bullet="—", space_after=12)
add_text(s, 108, 480, 480, 40,
         "Dampak: pencarian lambat dan risiko data sensitif.",
         size=10, color=STEEL, italic=True)
add_text(s, 688, 480, 480, 40,
         "Batasan MVP: data inti dulu, bukan dokumen atau portal klien.",
         size=10, color=STEEL, italic=True)
add_rect(s, 72, 584, 1136, 64, fill=GOLD_DARK, line=None, radius=0.08)
add_text(s, 104, 604, 1080, 24,
         "Ukuran keberhasilan  ·  4 peran  ·  1 VPS  ·  backup harian  ·  tanpa layanan berbayar wajib",
         size=12, color=TEXT, bold=True)
add_footer(s, 2)
add_notes(s, "Masalah utama bukan sekadar pencatatan, tetapi kontrol akses dan visibilitas finance. "
             "Target MVP menjaga biaya tetap rendah: satu VPS dan tanpa layanan wajib berbayar.")

# ---------------------------------------------------------------- slide 3
s = new_slide(NAVY)
add_header(s, "Empat modul inti",
           "Fitur poin 1–2 dipetakan ke modul yang dipakai harian oleh setiap peran.",
           3, "SOLUSI")
mods = [
    ("01", "Attorney", "Direktori, CRUD, status aktif/nonaktif, dan assignment ke kasus. Lawyer tetap bisa dicatat tanpa akun login."),
    ("02", "Klien & Kasus", "CRUD klien, nomor kasus otomatis, tim lead/member, deadline, pencarian, dan filter status."),
    ("03", "Finance", "Invoice + item, pembayaran, status bayar, outstanding, serta ringkasan pendapatan."),
    ("04", "Dashboard", "Counts dan grafik berbeda per peran; angka mengikuti data terbaru."),
]
positions = [(72, 190), (652, 190), (72, 406), (652, 406)]
outputs = [
    "Output: direktori rapi dan PIC kasus jelas.",
    "Output: riwayat kasus per klien.",
    "Output: tagihan dan sisa terpantau.",
    "Output: keputusan berbasis angka.",
]
for (num, name, desc), out, (x, y) in zip(mods, outputs, positions):
    card(s, x, y, 556, 192)
    add_text(s, x + 32, y + 26, 60, 24, num, size=12, color=GOLD, bold=True)
    add_text(s, x + 82, y + 20, 420, 32, name, size=18, color=TEXT, font=TITLE_FONT)
    add_text(s, x + 32, y + 68, 490, 100, desc, size=11.5, color=MUTED, line_spacing=1.25)
    add_text(s, x + 32, y + 150, 490, 22, out, size=9.5, color=STEEL, italic=True)
add_text(s, 72, 626, 1136, 24,
         "Semua modul memakai satu login dan matriks akses yang sama.",
         size=10.5, color=STEEL, italic=True)
add_footer(s, 3)
add_notes(s, "Empat modul ini menutup fitur yang diminta: login, attorney, klien & kasus, dan dashboard. "
             "Finance ditambahkan sesuai klarifikasi: fee dikelola lewat invoice dan pembayaran.")

# ---------------------------------------------------------------- slide 4
s = new_slide(NAVY_DATA)
add_header(s, "Stack hemat biaya",
           "Satu binary Go menyajikan API dan React; MySQL berjalan di VPS yang sama.",
           4, "TEKNOLOGI")
stack = [
    ("Go 1.22+", "API + React ter-embed dalam satu binary. Dependency minimal, deploy sederhana."),
    ("MySQL 8", "InnoDB, utf8mb4. Backup mysqldump harian; tanpa managed database."),
    ("React 18 + Vite", "TypeScript, Tailwind, TanStack Query, Recharts. Satu SPA, build cepat."),
    ("Docker + Caddy", "Compose: app + MySQL + Caddy. TLS otomatis, satu perintah deploy."),
]
xs = [72, 360, 648, 936]
for (name, desc), x in zip(stack, xs):
    card(s, x, 190, 272, 200, fill=CARD)
    add_text(s, x + 26, 216, 220, 26, name, size=15.5, color=GOLD, bold=True)
    add_text(s, x + 26, 258, 220, 110, desc, size=11, color=MUTED, line_spacing=1.28)
add_rect(s, 72, 424, 1136, 130, fill=CARD_ALT, line=GOLD_DARK, lw=1.0, radius=0.07)
add_text(s, 108, 448, 360, 44, "± Rp 1,1–2,2 juta", size=27, color=GOLD,
         font=TITLE_FONT, bold=False)
add_text(s, 108, 500, 360, 24, "per tahun, estimasi infrastruktur", size=10.5, color=MUTED)
add_text(s, 500, 452, 660, 70,
         "VPS 1–2 GB  ·  domain  ·  TLS gratis  ·  backup lokal  ·  tanpa managed DB/Redis",
         size=12, color=TEXT, line_spacing=1.35)
add_text(s, 72, 580, 900, 20, "Estimasi indikatif, bukan penawaran harga.",
         size=9, color=MUTED, italic=True)
add_footer(s, 4)
add_notes(s, "Stack dipilih untuk biaya rendah: tanpa Redis, queue, atau managed database. "
             "Estimasi biaya adalah kisaran indikatif, bukan penawaran.")

# ---------------------------------------------------------------- slide 5
s = new_slide(NAVY)
add_header(s, "Arsitektur satu VPS",
           "Modular monolith: frontend di-embed, API dan database berjalan sebagai kontainer terpisah.",
           5, "ARSITEKTUR")
nodes = [
    ("Browser", "SPA React", 72),
    ("Caddy", "HTTPS · TLS otomatis", 372),
    ("Go App", "REST /api/v1 + React embed", 672),
    ("MySQL 8", "InnoDB · backup harian", 972),
]
for name, desc, x in nodes:
    card(s, x, 238, 220, 118)
    add_text(s, x + 22, 262, 176, 28, name, size=16, color=TEXT, bold=True)
    add_text(s, x + 22, 298, 176, 40, desc, size=10, color=MUTED, line_spacing=1.2)
for x in (300, 600, 900):
    add_rect(s, x, 281, 64, 32, fill=STEEL, line=None, shape=MSO_SHAPE.RIGHT_ARROW)
pills = ["Migrasi saat startup", "Health check /healthz", "Log JSON", "Graceful shutdown"]
pxs = [72, 372, 672, 972]
for label, x in zip(pills, pxs):
    add_rect(s, x, 404, 220, 44, fill=CARD_ALT, line=BORDER, radius=0.5)
    add_text(s, x + 12, 417, 196, 20, label, size=9.5, color=TEXT, align=PP_ALIGN.CENTER)
add_text(s, 72, 500, 1136, 56,
         "Tanpa Redis, message queue, atau managed service. Semua komponen berjalan di satu mesin "
         "dan dipindahkan hanya dengan Compose.",
         size=12, color=MUTED, line_spacing=1.35)
add_text(s, 72, 574, 600, 20, "Deploy: docker compose up  ·  TLS otomatis oleh Caddy",
         size=10, color=GOLD, bold=True)
add_text(s, 72, 616, 1136, 22,
         "Data: volume MySQL persisten  ·  backup 7 harian + 4 mingguan  ·  restore diuji sebelum go-live.",
         size=10, color=MUTED)
add_footer(s, 5)
add_notes(s, "Permintaan browser dilayani Caddy, diteruskan ke aplikasi Go yang menyajikan API dan aset React. "
             "Database berada di kontainer terpisah dengan volume persisten dan backup harian.")

# ---------------------------------------------------------------- slide 6
s = new_slide(NAVY)
add_header(s, "Siapa boleh apa",
           "Hak akses dicek di server; UI hanya menyembunyikan menu yang tidak relevan.",
           6, "KONTROL AKSES")
rows_data = [
    ("Modul", "Direktur", "CS/Admin", "Finance", "Lawyer"),
    ("Dashboard", "Semua metrik", "Operasional", "Finance", "Kasus & deadline"),
    ("Attorneys", "CRUD", "CRUD", "Lihat", "Lihat"),
    ("Clients", "CRUD", "CRUD", "Lihat", "Lihat"),
    ("Cases", "CRUD", "CRUD", "Lihat", "C/R/U, tanpa hapus"),
    ("Invoice & pembayaran", "Kelola + void", "Lihat", "Kelola + void", "—"),
    ("User & role", "Kelola akun", "—", "—", "—"),
]
table_shape = s.shapes.add_table(len(rows_data), 5, px(72), px(190), px(1136), px(392))
table = table_shape.table
table.first_row = False
table.horz_banding = False
col_widths = [316, 220, 200, 200, 200]
for idx, width in enumerate(col_widths):
    table.columns[idx].width = px(width)
for r_idx, row in enumerate(rows_data):
    table.rows[r_idx].height = px(56 if r_idx == 0 else 48)
    for c_idx, value in enumerate(row):
        cell = table.cell(r_idx, c_idx)
        cell.margin_left = px(12)
        cell.margin_right = px(10)
        cell.margin_top = px(4)
        cell.margin_bottom = px(4)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        if r_idx == 0:
            cell.fill.fore_color.rgb = rgb(CARD_ALT)
            color = GOLD
            bold = True
            size = 10.5
        else:
            if c_idx == 0:
                cell.fill.fore_color.rgb = rgb(CARD)
                color = TEXT
                bold = True
            elif c_idx == 1:
                cell.fill.fore_color.rgb = rgb("2A2316")
                color = GOLD
                bold = False
            else:
                cell.fill.fore_color.rgb = rgb(CARD if r_idx % 2 else NAVY_DATA)
                color = MUTED
                bold = False
            size = 10
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER
        run = p.add_run()
        run.text = value
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = BODY_FONT
        run.font.color.rgb = rgb(color)
add_text(s, 72, 604, 546, 18,
         "Lawyer tidak menerima data invoice/fee di response kasus.",
         size=9, color=MUTED)
add_text(s, 650, 604, 558, 18,
         "Hapus kasus hanya Direktur/CS; akun dinonaktifkan, bukan dihapus.",
         size=9, color=MUTED, align=PP_ALIGN.RIGHT)
add_footer(s, 6)
add_notes(s, "Matriks ini menjadi sumber kebenaran untuk middleware RBAC. "
             "Pembatasan penting: Lawyer tidak menerima data invoice, CS hanya membaca invoice, "
             "dan hanya Direktur yang mengelola akun.")

# ---------------------------------------------------------------- slide 7
s = new_slide(NAVY_DATA)
add_header(s, "Direktur: kendali penuh",
           "Satu-satunya peran yang mengelola akun dan melihat seluruh metrik operasional serta finance.",
           7, "DIREKTUR")
add_text(s, 72, 220, 400, 96, "100%", size=64, color=GOLD, font=TITLE_FONT)
add_text(s, 72, 316, 360, 24, "akses data & keuangan", size=13, color=TEXT, bold=True)
add_text(s, 72, 360, 390, 120,
         "Direktur adalah super admin: dapat membuat akun, mengubah role, mereset password, "
         "dan menonaktifkan akun.",
         size=12, color=MUTED, line_spacing=1.35)
add_text(s, 72, 500, 390, 80,
         "Pagar pengaman: akun sendiri tidak bisa dinonaktifkan; role dibaca ulang dari database "
         "pada setiap request.",
         size=11, color=STEEL, line_spacing=1.3)
add_text(s, 72, 592, 390, 24, "Satu akun untuk mengatur seluruh sistem.",
         size=12, color=GOLD, bold=True)
items = [
    ("01", "Dashboard lengkap", "Attorney, klien, kasus aktif/selesai, revenue bulan ini, outstanding, grafik status/jenis, top lawyer."),
    ("02", "Kelola akun & role", "Tambah user, ubah role, reset password, dan nonaktifkan akun."),
    ("03", "Semua modul", "CRUD attorney, klien, kasus, invoice; void serta pencatatan pembayaran."),
    ("04", "Visibilitas finance", "Outstanding, overdue, dan pendapatan enam bulan terakhir."),
]
for idx, (num, name, desc) in enumerate(items):
    y = 196 + idx * 112
    card(s, 528, y, 680, 96)
    add_text(s, 556, y + 16, 44, 20, num, size=10.5, color=GOLD, bold=True)
    add_text(s, 600, y + 12, 560, 24, name, size=14.5, color=TEXT, bold=True)
    add_text(s, 600, y + 42, 570, 46, desc, size=10.5, color=MUTED, line_spacing=1.25)
add_footer(s, 7)
add_notes(s, "Peran Direktur menggabungkan fungsi pengawas dan super admin. "
             "Dua pagar penting: tidak bisa menonaktifkan akun sendiri dan role selalu dibaca dari database.")

# ---------------------------------------------------------------- slide 8
s = new_slide(NAVY)
add_header(s, "CS/Admin: mesin operasional",
           "Menjaga data harian tetap rapi, kasus berjalan, dan tim attorney terhubung.",
           8, "CS / ADMIN")
card(s, 72, 190, 620, 386)
add_text(s, 108, 222, 400, 26, "Tugas utama", size=16, color=GOLD, bold=True)
add_lines(s, 108, 270, 540, 280, [
    "CRUD attorney, klien, dan kasus, termasuk assignment tim lead/member.",
    "Dashboard operasional: kasus aktif, deadline 30 hari, update terbaru.",
    "Pencarian, filter status, dan pagination di semua tabel.",
    "Menyiapkan data agar Finance bisa menerbitkan invoice.",
], size=12.5, bullet="—", space_after=18)
add_text(s, 108, 520, 540, 22,
         "Output: data siap dipakai Finance dan Lawyer.",
         size=10, color=STEEL, italic=True)
card(s, 716, 190, 492, 180)
add_text(s, 750, 216, 380, 24, "Batas akses", size=14.5, color=GOLD, bold=True)
add_text(s, 750, 254, 420, 90,
         "Invoice read-only  ·  tidak mengelola akun  ·  hapus kasus hanya jika belum ada invoice.",
         size=11.5, color=MUTED, line_spacing=1.35)
card(s, 716, 396, 492, 180, fill=CARD_ALT)
add_text(s, 750, 422, 380, 24, "Praktis", size=14.5, color=GOLD, bold=True)
add_text(s, 750, 460, 420, 90,
         "Attorney tanpa akun login tetap bisa dicatat, di-assign ke kasus, dan dinonaktifkan.",
         size=11.5, color=MUTED, line_spacing=1.35)
add_footer(s, 8)
add_notes(s, "CS/Admin adalah pengguna harian utama untuk master data dan kasus. "
             "Mereka bisa melihat invoice untuk koordinasi, tetapi tidak mengubah data finance.")

# ---------------------------------------------------------------- slide 9
s = new_slide(NAVY_DATA)
add_header(s, "Finance: tagihan terkendali",
           "Invoice dan pembayaran dihitung server agar total, sisa, dan status tidak melenceng.",
           9, "FINANCE")
steps = [("Draft", "Item & total"), ("Sent", "Siap ditagih"),
         ("Partial", "Dibayar sebagian"), ("Paid", "Sisa = 0")]
for idx, (name, desc) in enumerate(steps):
    x = 72 + idx * 296
    card(s, x, 190, 260, 96)
    add_text(s, x + 22, 208, 210, 24, name, size=15, color=GOLD, bold=True)
    add_text(s, x + 22, 240, 210, 22, desc, size=10, color=MUTED)
    if idx < 3:
        add_rect(s, x + 266, 226, 26, 24, fill=STEEL, line=None, shape=MSO_SHAPE.RIGHT_ARROW)
add_text(s, 72, 302, 1136, 48,
         "Overdue otomatis saat melewati jatuh tempo  ·  Void hanya jika belum ada pembayaran  ·  "
         "Pembayaran tidak boleh melebihi sisa",
         size=10.5, color=STEEL, line_spacing=1.3)
fin_cards = [
    ("Item & total", "Qty × harga satuan dihitung server. Item hanya bisa diubah saat draft.",
     "Total = jumlah seluruh item."),
    ("Pembayaran", "Tanggal, nominal, metode, referensi. Nominal dibatasi sisa tagihan.",
     "Hanya untuk invoice berstatus sent."),
    ("Ringkasan", "Outstanding, overdue, pendapatan 6 bulan, dan daftar invoice jatuh tempo.",
     "Termasuk 10 invoice jatuh tempo teratas."),
]
for idx, (name, desc, note) in enumerate(fin_cards):
    x = 72 + idx * 388
    card(s, x, 362, 360, 178)
    add_text(s, x + 26, 388, 300, 24, name, size=14, color=TEXT, bold=True)
    add_text(s, x + 26, 424, 304, 100, desc, size=11, color=MUTED, line_spacing=1.3)
    add_text(s, x + 26, 498, 304, 22, note, size=9.5, color=STEEL, italic=True)
add_text(s, 72, 574, 1136, 24,
         "Finance melihat kasus untuk menagih, tetapi tidak mengubah data kasus atau klien.",
         size=10.5, color=STEEL, italic=True)
add_footer(s, 9)
add_notes(s, "Status bayar dihitung dari total item dikurangi pembayaran. "
             "Aturan pengaman: item hanya bisa diubah saat draft, pembayaran tidak melebihi sisa, "
             "dan invoice yang sudah dibayar tidak bisa di-void.")

# ---------------------------------------------------------------- slide 10
s = new_slide(NAVY)
add_header(s, "Lawyer: fokus pada kasus",
           "Akses lapangan luas, dengan pagar tegas pada data sensitif.",
           10, "LAWYER")
card(s, 72, 190, 556, 340)
add_text(s, 108, 220, 400, 26, "Bisa", size=16, color=GOLD, bold=True)
add_lines(s, 108, 266, 480, 240, [
    "Melihat semua kasus dan detailnya.",
    "Menambah dan mengedit kasus.",
    "Update status, catatan, dan deadline.",
    "Filter “Kasus Saya” dari assignment.",
], size=13, bullet="—", space_after=16)
card(s, 652, 190, 556, 340, fill=CARD_ALT)
add_text(s, 688, 220, 400, 26, "Tidak", size=16, color=STEEL, bold=True)
add_lines(s, 688, 266, 480, 240, [
    "Menghapus kasus.",
    "Melihat invoice, fee, dan pembayaran.",
    "Mencatat atau mengubah pembayaran.",
    "Mengelola akun pengguna.",
], size=13, bullet="—", bullet_color=STEEL, space_after=16)
add_rect(s, 72, 558, 1136, 62, fill=GOLD_DARK, line=None, radius=0.08)
add_text(s, 104, 577, 1080, 24,
         "Assignment = penanda PIC + filter “Kasus Saya”, bukan pembatas akses.",
         size=12, color=TEXT, bold=True, align=PP_ALIGN.CENTER)
add_footer(s, 10)
add_notes(s, "Sesuai klarifikasi, Lawyer dapat melihat dan mengedit semua kasus, tetapi tetap tidak boleh menghapus "
             "dan tidak menerima data invoice/fee. Assignment dipakai sebagai penanda PIC dan filter.")

# ---------------------------------------------------------------- slide 11
s = new_slide(NAVY_DATA)
add_header(s, "Dashboard: angka yang relevan",
           "Satu endpoint ringkasan, empat bentuk payload sesuai peran.",
           11, "DASHBOARD")
dash = [
    ("Direktur", "Total attorney & klien  ·  kasus aktif/selesai  ·  revenue bulan ini  ·  outstanding  ·  grafik status & jenis  ·  top lawyer."),
    ("CS/Admin", "Total attorney & klien  ·  kasus aktif  ·  deadline 30 hari  ·  10 kasus terbaru."),
    ("Finance", "Total tagihan  ·  terbayar  ·  outstanding  ·  overdue  ·  revenue 6 bulan  ·  invoice jatuh tempo."),
    ("Lawyer", "Kasus saya per status  ·  deadline terdekat  ·  update terakhir."),
]
positions = [(72, 190), (652, 190), (72, 408), (652, 408)]
focus = ["Fokus: kontrol dan keputusan.", "Fokus: kelancaran operasional.",
         "Fokus: arus kas.", "Fokus: progres kasus."]
for (role, desc), note, (x, y) in zip(dash, focus, positions):
    card(s, x, y, 556, 198)
    add_text(s, x + 30, y + 22, 300, 26, role, size=16, color=GOLD, bold=True)
    add_text(s, x + 30, y + 60, 492, 118, desc, size=11.5, color=MUTED, line_spacing=1.3)
    add_text(s, x + 30, y + 160, 492, 22, note, size=9.5, color=STEEL, italic=True)
add_text(s, 72, 626, 1136, 24,
         "Definisi: kasus aktif = open + in_progress; outstanding = sisa invoice sent; overdue = lewat jatuh tempo dan belum lunas.",
         size=9.5, color=STEEL, italic=True)
add_footer(s, 11)
add_notes(s, "Dashboard bukan sekadar hitungan, tetapi bentuknya berbeda per peran: "
             "Direktur melihat semua, CS fokus operasional, Finance fokus tagihan, Lawyer fokus kasusnya.")

# ---------------------------------------------------------------- slide 12
s = new_slide(NAVY)
add_header(s, "Aman dan mudah dirawat",
           "Kontrol akses, backup, dan operasi harian tanpa layanan tambahan.",
           12, "KEAMANAN & OPS")
sec = [
    ("Sesi", "JWT HttpOnly 8 jam; password bcrypt cost 12.",
     "Cookie tidak dapat dibaca JavaScript."),
    ("Otorisasi", "Role dari database, default deny; 403 dicek di server.",
     "UI hanya lapisan kedua."),
    ("Login", "Rate limit 5/menit/IP; pesan tidak membocorkan email.",
     "Percobaan berlebih ditolak sementara."),
    ("Data", "Query parameterized; secret hanya dari environment.",
     "Tidak ada string SQL dari input."),
    ("Backup", "mysqldump harian; 7 harian + 4 mingguan; restore diuji.",
     "Uji restore sebelum go-live."),
    ("Operasional", "TLS Caddy, health check, log JSON, graceful shutdown.",
     "Restart aman tanpa kehilangan data."),
]
positions = [(72, 190), (460, 190), (848, 190), (72, 402), (460, 402), (848, 402)]
for (name, desc, note), (x, y) in zip(sec, positions):
    card(s, x, y, 360, 184)
    add_text(s, x + 26, y + 22, 300, 24, name, size=14, color=GOLD, bold=True)
    add_text(s, x + 26, y + 60, 308, 100, desc, size=11, color=MUTED, line_spacing=1.3)
    add_text(s, x + 26, y + 136, 308, 22, note, size=9.5, color=STEEL, italic=True)
add_text(s, 72, 618, 1136, 24,
         "Tanpa Redis, queue, atau managed service; semua konfigurasi lewat environment variable.",
         size=10, color=STEEL, italic=True)
add_footer(s, 12)
add_notes(s, "Keamanan utama ada di server: sesi HttpOnly, role dari database, rate limit login, "
             "dan query parameterized. Backup harian wajib diuji restore sebelum go-live.")

# ---------------------------------------------------------------- slide 13
s = new_slide(NAVY_DATA)
add_header(s, "Dari rancangan ke rilis",
           "Enam milestone, satu VPS, tanpa layanan berbayar wajib.",
           13, "TAHAPAN")
for idx, (num, label) in enumerate([("6", "milestone"), ("4", "peran"), ("1", "VPS")]):
    x = 72 + idx * 180
    add_text(s, x, 160, 54, 34, num, size=26, color=GOLD, font=TITLE_FONT)
    add_text(s, x + 32, 172, 130, 20, label, size=9.5, color=MUTED)
add_rect(s, 120, 330, 1000, 2, fill=BORDER, line=None, shape=MSO_SHAPE.RECTANGLE)
milestones = [
    ("M1", "Fondasi & auth"), ("M2", "Master data"), ("M3", "Kasus & assignment"),
    ("M4", "Finance"), ("M5", "Dashboard"), ("M6", "Deploy & hardening"),
]
for idx, (code, label) in enumerate(milestones):
    x = 120 + idx * 200
    add_text(s, x - 30, 286, 60, 22, code, size=12, color=GOLD, bold=True, align=PP_ALIGN.CENTER)
    add_rect(s, x - 12, 318, 24, 24, fill=GOLD if idx < 3 else CARD,
             line=GOLD, lw=1.0, shape=MSO_SHAPE.OVAL)
    add_text(s, x - 82, 360, 164, 52, label, size=10.5, color=TEXT if idx < 3 else MUTED,
             align=PP_ALIGN.CENTER, line_spacing=1.2)
add_text(s, 72, 438, 1136, 22,
         "Setiap milestone ditutup dengan pengujian role dan acceptance criteria.",
         size=10, color=STEEL, italic=True)
add_rect(s, 72, 500, 1136, 96, fill=CARD_ALT, line=GOLD_DARK, lw=1.0, radius=0.08)
add_text(s, 104, 522, 1080, 26,
         "Langkah berikutnya: rencana implementasi rinci sebelum menulis kode.",
         size=15, color=TEXT, bold=True)
add_text(s, 104, 556, 1080, 22,
         "Spec lengkap sudah tersedia di repository GitHub: gatnadf-AI/lawfirm-admin-panel",
         size=10.5, color=MUTED)
add_footer(s, 13)
add_notes(s, "Urutan milestone menjaga fokus: fondasi dan auth dulu, master data, kasus, finance, dashboard, "
             "lalu deploy dan hardening. Rencana implementasi akan memecah ini menjadi tugas yang dapat diuji.")

# ---------------------------------------------------------------- slide 14
s = new_slide(NAVY_DARK)
add_rect(s, 900, 140, 300, 300, fill=None, line=GOLD, lw=1.1, shape=MSO_SHAPE.OVAL)
add_text(s, 930, 200, 240, 180, "✓", size=110, color=GOLD, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 72, 180, 760, 100, "Terima kasih", size=58, color=TEXT, font=TITLE_FONT)
add_text(s, 72, 300, 700, 90,
         "Rancangan siap ditinjau. Langkah berikutnya adalah rencana implementasi rinci, "
         "lalu pembangunan bertahap.",
         size=15, color=MUTED, line_spacing=1.3)
add_text(s, 72, 430, 760, 24, "github.com/gatnadf-AI/lawfirm-admin-panel",
         size=12, color=GOLD, bold=True)
add_text(s, 72, 620, 900, 40,
         "Dokumen rancangan · 2026 · Go + MySQL + React",
         size=9.5, color=MUTED)
add_notes(s, "Penutup: tekankan bahwa deck dan spec adalah rancangan yang sudah disetujui arahnya, "
             "dan langkah berikutnya adalah rencana implementasi sebelum coding.")

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(f"saved {OUT} ({len(prs.slides)} slides)")
