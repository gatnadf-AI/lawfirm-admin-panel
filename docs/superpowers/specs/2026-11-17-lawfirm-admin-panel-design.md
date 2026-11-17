# Sistem Admin Panel Manajemen Firma Hukum — Design Spec

- **Tanggal:** 2026-11-17
- **Status:** Desain disetujui (bagian 1 & 2); spec menunggu review akhir sebelum rencana implementasi
- **Cakupan dokumen:** tech stack + fitur (poin 1 & 2 permintaan)
- **Deliverable terkait:** slide PPT highlight per role (poin 3, dibuat setelah spec disetujui)

---

## 1. Ringkasan

Sistem admin panel untuk firma hukum dengan empat peran: **Direktur**, **CS/Admin Staff**, **Finance/Accounting**, dan **Lawyer**. Sistem mengelola data attorney, klien, kasus, invoice & pembayaran, akun pengguna, serta dashboard dengan angka ringkasan yang menyesuaikan peran.

Tujuan utama:

1. Satu tempat untuk data operasional firma (attorney, klien, kasus).
2. Kontrol akses berbasis peran yang tegas, dicek di server.
3. Visibilitas finansial (tagihan, pembayaran, outstanding) bagi Finance dan Direktur.
4. Biaya infrastruktur dan perawatan serendah mungkin untuk firma kecil.

### Keputusan hasil klarifikasi

| Topik | Keputusan |
|---|---|
| Scope Finance | Fee kasus dikelola lewat invoice + pembayaran, plus laporan/ringkasan finance |
| Admin sistem | Direktur adalah super admin, satu-satunya yang mengelola akun & role |
| Akses Lawyer | Melihat dan mengedit semua kasus; "assigned" menjadi penanda PIC dan filter "Kasus Saya", bukan pembatas akses |
| Batas pengaman Lawyer | Tidak boleh menghapus kasus; tidak melihat data invoice/fee |
| Akses CS ke invoice | Read-only |
| Audiens PPT | Stakeholder internal (pemilik firma/dosen/penguji), Bahasa Indonesia |

---

## 2. Tech Stack & Biaya

### 2.1 Stack

| Lapisan | Pilihan | Alasan |
|---|---|---|
| Bahasa backend | Go 1.22+ (stdlib `net/http`, `log/slog`) | Binary tunggal, dependency sedikit, mudah deploy |
| Database | MySQL 8 (InnoDB, utf8mb4) | Sesuai permintaan; gratis, umum, mudah backup |
| Frontend | React 18 + TypeScript + Vite | Sesuai permintaan; build cepat |
| Styling | Tailwind CSS | Tanpa file CSS besar, konsisten |
| Routing | React Router | Route guard per role |
| Data fetching | TanStack Query | Cache, loading/error state, invalidasi setelah mutasi |
| Form & validasi | React Hook Form + Zod | Validasi klien yang ringkas dan konsisten |
| Grafik | Recharts | Grafik dashboard tanpa layanan tambahan |
| Auth | JWT HS256 di cookie `HttpOnly` + bcrypt | Stateless, tanpa Redis/session store |
| Migrasi | Runner SQL kecil dengan tabel `schema_migrations` | Tanpa tool tambahan di runtime |
| Reverse proxy/TLS | Caddy | TLS otomatis (Let's Encrypt), konfigurasi minimal |
| Kontainer | Docker + Docker Compose | Satu perintah deploy, mudah dipindah VPS |
| Test backend | `testing`, `httptest`, `go-sqlmock` | Standar Go, tanpa layanan eksternal |
| Test frontend | Vitest + React Testing Library | Cepat, terintegrasi Vite |

Prinsip biaya rendah: **tanpa Redis, tanpa message queue, tanpa managed database, tanpa layanan berbayar wajib**. Semua berjalan di satu VPS.

### 2.2 Estimasi biaya (indikatif, bukan penawaran)

| Item | Estimasi |
|---|---|
| VPS 1–2 vCPU / 1–2 GB RAM | Rp 80.000–160.000 / bulan |
| Domain (`.com` atau `.id`) | Rp 150.000–250.000 / tahun |
| TLS (Let's Encrypt via Caddy) | Gratis |
| Managed DB | Tidak dipakai (MySQL di VPS yang sama) |
| Backup | Gratis (file lokal) atau object storage free tier |
| **Total infrastruktur** | **± Rp 1,1–2,2 juta / tahun** |

---

## 3. Arsitektur

**Modular monolith**: satu service Go berisi seluruh API, dengan build React di-embed ke binary menggunakan `go:embed`.

```
Browser ──HTTPS──> Caddy ──> app (Go + React embed) ──> MySQL 8
                              │
                              └─ /api/v1/*  (JSON)
                              └─ /*          (SPA fallback ke index.html)
```

Komponen backend (package Go):

- `auth` — login, logout, JWT, middleware role
- `users` — pengelolaan akun & role (Direktur)
- `attorneys` — data attorney
- `clients` — data klien
- `cases` — kasus + assignment attorney
- `finance` — invoice, item, pembayaran, status bayar
- `dashboard` — agregasi ringkasan per role
- `store` — akses MySQL (query parameterized)
- `httpx` — helper JSON, error, pagination, validasi
- `migrate` — runner migrasi SQL
- `cmd/server` — wiring, routing, graceful shutdown

Struktur proyek:

```
lawfirm-admin/
  cmd/server/main.go
  internal/{auth,users,attorneys,clients,cases,finance,dashboard,store,httpx,migrate}/
  migrations/*.sql
  web/                  # React + Vite
  deploy/{Dockerfile,docker-compose.yml,Caddyfile}
  docs/superpowers/specs/
```

---

## 4. Peran & Matriks Akses

| Modul | Direktur | CS/Admin | Finance | Lawyer |
|---|---|---|---|---|
| Dashboard | semua metrik | operasional | finance | kasus & deadline |
| Attorneys | C R U D | C R U D | R | R |
| Clients | C R U D | C R U D | R | R |
| Cases | C R U D | C R U D | R | R + C + U (semua kasus), tanpa D |
| Invoice & pembayaran | C R U, void, pembayaran | R | C R U, void, pembayaran | — |
| User & role | C R U (nonaktifkan) | — | — | — |

Aturan tambahan:

- Semua pengecekan role dilakukan di server; UI hanya menyembunyikan menu.
- Lawyer tidak menerima data invoice/fee pada response kasus.
- Direktur tidak dapat menonaktifkan atau menghapus akunnya sendiri.
- Akun nonaktif tidak bisa login dan token-nya ditolak pada request berikutnya.

---

## 5. Fitur

### F1 — Login & pengelolaan akun

- Login dengan email + password; pesan error generik "Email atau password salah".
- Setelah login diarahkan ke `/dashboard`.
- Logout menghapus cookie sesi.
- Ganti password sendiri (wajib password lama).
- Direktur: daftar user, tambah user (nama, email, role, password awal), edit (nama, role, status aktif), reset password, nonaktifkan.
- Seed akun Direktur pertama dari environment variable saat database masih kosong.
- Rate limit login: maksimal 5 percobaan/menit per IP (in-memory).

### F2 — Manage attorneys

- Daftar dengan pencarian (nama/no. izin), filter status, pagination.
- Tambah/edit: nama lengkap, spesialisasi, no. izin PERADI, telepon, email, status (`active`/`inactive`), tanggal bergabung, catatan, tautan opsional ke akun user ber-role Lawyer.
- Hapus hanya jika tidak memiliki assignment kasus dan tidak tertaut akun; jika terkait, arahkan ke status `inactive` (HTTP 409 dengan pesan jelas).
- Lawyer melihat direktori (read-only).

### F3 — Manage clients & cases

**Klien**

- CRUD: tipe (`individu`/`perusahaan`), nama, nama perusahaan, email, telepon, alamat, no. identitas (KTP/NPWP), catatan.
- Hapus hanya jika belum punya kasus (409 jika ada kasus).
- Finance & Lawyer read-only.

**Kasus**

- Nomor otomatis `CASE-YYYY-#####` (berbasis ID, dibuat dalam transaksi).
- CRUD: judul, klien, jenis (`litigasi`/`non_litigasi`/`konsultasi`), status (`open`/`in_progress`/`on_hold`/`closed`), deadline, pengadilan, pihak lawan, deskripsi.
- Assignment tim: satu `lead` + nol/lebih `member` (attorney).
- Filter: status, jenis, pencarian nomor/judul/nama klien, dan toggle **"Kasus Saya"** (berdasarkan assignment lawyer yang login).
- Detail kasus: info, tim, daftar invoice (hanya bila role berhak).
- Hapus kasus hanya Direktur/CS dan hanya jika belum punya invoice (409).

### F4 — Finance (invoice & pembayaran)

- Invoice terhubung ke satu kasus; klien terisi otomatis dari kasus.
- Item invoice: deskripsi, qty, harga satuan; subtotal dihitung server. Total = jumlah seluruh item. Item hanya boleh diubah selama invoice masih `draft`; setelah `sent`, yang bisa diubah hanya catatan dan tanggal jatuh tempo (tidak boleh lebih awal dari pembayaran terakhir).
- Status dasar: `draft` → `sent` → `void`. Status bayar dihitung: `unpaid`, `partial`, `paid`, `overdue` (jatuh tempo lewat dan belum lunas).
- Pembayaran dicatat per invoice (tanggal, nominal, metode, no. referensi). Pembayaran hanya boleh pada invoice `sent`; nominal tidak boleh melebihi sisa tagihan (422).
- Invoice `void` hanya jika belum ada pembayaran.
- Nomor otomatis `INV-YYYY-#####`.
- Daftar invoice: filter status, pencarian nomor/nama klien, filter jatuh tempo.
- Ringkasan finance: total tagihan, terbayar, outstanding, overdue, pendapatan 6 bulan.

### F5 — Dashboard dengan counts

Payload `GET /api/v1/dashboard/summary` menyesuaikan role (lihat bagian 9).

---

## 6. Data Model

Konvensi: InnoDB, `utf8mb4`, waktu UTC, uang `DECIMAL(15,2)`, semua tabel punya `created_at`/`updated_at` (kecuali yang disebut lain), semua FK memakai `RESTRICT` kecuali dinyatakan lain.

```sql
CREATE TABLE users (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(120) NOT NULL,
  email         VARCHAR(160) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('direktur','cs_admin','finance','lawyer') NOT NULL,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE attorneys (
  id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id        BIGINT UNSIGNED NULL UNIQUE,
  full_name      VARCHAR(150) NOT NULL,
  specialization VARCHAR(120) NULL,
  license_no     VARCHAR(60) NULL UNIQUE,
  phone          VARCHAR(40) NULL,
  email          VARCHAR(160) NULL,
  status         ENUM('active','inactive') NOT NULL DEFAULT 'active',
  joined_at      DATE NULL,
  notes          TEXT NULL,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_attorney_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE clients (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  type         ENUM('individu','perusahaan') NOT NULL,
  name         VARCHAR(150) NOT NULL,
  company_name VARCHAR(150) NULL,
  email        VARCHAR(160) NULL,
  phone        VARCHAR(40) NULL,
  address      TEXT NULL,
  id_number    VARCHAR(60) NULL,
  notes        TEXT NULL,
  created_by   BIGINT UNSIGNED NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_client_creator FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE cases (
  id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  case_number    VARCHAR(30) NOT NULL UNIQUE,
  title          VARCHAR(200) NOT NULL,
  client_id      BIGINT UNSIGNED NOT NULL,
  case_type      ENUM('litigasi','non_litigasi','konsultasi') NOT NULL,
  status         ENUM('open','in_progress','on_hold','closed') NOT NULL DEFAULT 'open',
  deadline       DATE NULL,
  court          VARCHAR(150) NULL,
  opposing_party VARCHAR(150) NULL,
  description    TEXT NULL,
  created_by     BIGINT UNSIGNED NOT NULL,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_case_client FOREIGN KEY (client_id) REFERENCES clients(id),
  CONSTRAINT fk_case_creator FOREIGN KEY (created_by) REFERENCES users(id),
  INDEX idx_cases_status (status),
  INDEX idx_cases_client (client_id),
  INDEX idx_cases_deadline (deadline)
);

CREATE TABLE case_assignments (
  case_id     BIGINT UNSIGNED NOT NULL,
  attorney_id BIGINT UNSIGNED NOT NULL,
  role_in_case ENUM('lead','member') NOT NULL DEFAULT 'member',
  PRIMARY KEY (case_id, attorney_id),
  CONSTRAINT fk_assign_case FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
  CONSTRAINT fk_assign_attorney FOREIGN KEY (attorney_id) REFERENCES attorneys(id),
  INDEX idx_assign_attorney (attorney_id)
);

CREATE TABLE invoices (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  invoice_no  VARCHAR(30) NOT NULL UNIQUE,
  case_id     BIGINT UNSIGNED NOT NULL,
  client_id   BIGINT UNSIGNED NOT NULL,
  issue_date  DATE NOT NULL,
  due_date    DATE NOT NULL,
  status      ENUM('draft','sent','void') NOT NULL DEFAULT 'draft',
  notes       TEXT NULL,
  created_by  BIGINT UNSIGNED NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_invoice_case FOREIGN KEY (case_id) REFERENCES cases(id),
  CONSTRAINT fk_invoice_client FOREIGN KEY (client_id) REFERENCES clients(id),
  CONSTRAINT fk_invoice_creator FOREIGN KEY (created_by) REFERENCES users(id),
  INDEX idx_invoices_case (case_id),
  INDEX idx_invoices_status (status),
  INDEX idx_invoices_due (due_date)
);

CREATE TABLE invoice_items (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  invoice_id  BIGINT UNSIGNED NOT NULL,
  description VARCHAR(255) NOT NULL,
  qty         DECIMAL(10,2) NOT NULL,
  unit_price  DECIMAL(15,2) NOT NULL,
  amount      DECIMAL(15,2) AS (qty * unit_price) STORED,
  CONSTRAINT fk_item_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
  INDEX idx_items_invoice (invoice_id)
);

CREATE TABLE payments (
  id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  invoice_id   BIGINT UNSIGNED NOT NULL,
  paid_at      DATE NOT NULL,
  amount       DECIMAL(15,2) NOT NULL,
  method       ENUM('transfer','cash','kartu','lain') NOT NULL,
  reference_no VARCHAR(100) NULL,
  notes        TEXT NULL,
  recorded_by  BIGINT UNSIGNED NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_payment_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
  CONSTRAINT fk_payment_recorder FOREIGN KEY (recorded_by) REFERENCES users(id),
  INDEX idx_payments_invoice (invoice_id)
);
```

Relasi:

```
users 1 ── 0..1 attorneys
users 1 ── * clients (created_by)
clients 1 ── * cases
cases * ── * attorneys (case_assignments)
cases 1 ── * invoices
invoices 1 ── * invoice_items
invoices 1 ── * payments
```

Aturan turunan (dihitung server, tidak disimpan agar tidak drift):

- Total invoice = `SUM(invoice_items.amount)`.
- Total terbayar = `SUM(payments.amount)`.
- Sisa = total − terbayar.
- Status bayar dievaluasi berurutan: `paid` bila sisa = 0; `overdue` bila sisa > 0 dan `due_date` < hari ini dan status dasar `sent`; `partial` bila 0 < terbayar < total; selain itu `unpaid`.

Penomoran: insert baris lalu `UPDATE ... SET case_number = CONCAT('CASE-', YEAR(NOW()), '-', LPAD(id,5,'0'))` (dan analog untuk invoice) dalam satu transaksi.

---

## 7. API

Base: `/api/v1`. Semua response JSON. Autentikasi lewat cookie `HttpOnly`.

### 7.1 Endpoint

| Method & path | Akses | Keterangan |
|---|---|---|
| `POST /auth/login` | publik | `{email,password}` → set cookie, user info |
| `POST /auth/logout` | login | hapus cookie |
| `GET /auth/me` | login | profil + role |
| `POST /auth/change-password` | login | `{old_password,new_password}` |
| `GET /users` | Direktur | list + pagination |
| `POST /users` | Direktur | buat akun |
| `PUT /users/{id}` | Direktur | edit nama/role/status |
| `POST /users/{id}/reset-password` | Direktur | set password baru |
| `GET /attorneys` | semua | search, filter status, pagination |
| `GET /attorneys/{id}` | semua | detail |
| `POST /attorneys` | Direktur, CS | create |
| `PUT /attorneys/{id}` | Direktur, CS | update |
| `DELETE /attorneys/{id}` | Direktur, CS | 409 bila terikat kasus/user |
| `GET /clients` | semua | search, pagination |
| `GET /clients/{id}` | semua | detail + kasus terkait |
| `POST /clients` | Direktur, CS | create |
| `PUT /clients/{id}` | Direktur, CS | update |
| `DELETE /clients/{id}` | Direktur, CS | 409 bila punya kasus |
| `GET /cases` | semua | filter status/jenis/q; `mine=1` untuk lawyer |
| `GET /cases/{id}` | semua | detail + tim + invoice (bila berhak) |
| `POST /cases` | Direktur, CS, Lawyer | create + assignment |
| `PUT /cases/{id}` | Direktur, CS, Lawyer | update |
| `DELETE /cases/{id}` | Direktur, CS | 409 bila punya invoice |
| `PUT /cases/{id}/assignments` | Direktur, CS | ganti tim |
| `GET /invoices` | Direktur, Finance, CS | filter status/q |
| `GET /invoices/{id}` | Direktur, Finance, CS | detail + item + pembayaran |
| `POST /invoices` | Direktur, Finance | create dengan item |
| `PUT /invoices/{id}` | Direktur, Finance | edit; item hanya saat `draft`, setelah `sent` hanya catatan/jatuh tempo |
| `POST /invoices/{id}/send` | Direktur, Finance | draft → sent |
| `POST /invoices/{id}/void` | Direktur, Finance | hanya jika tanpa pembayaran |
| `POST /invoices/{id}/payments` | Direktur, Finance | catat pembayaran |
| `DELETE /invoices/{id}/payments/{paymentId}` | Direktur, Finance | hapus pembayaran |
| `GET /dashboard/summary` | semua | payload per role |
| `GET /healthz` | publik | health check |

### 7.2 Format

Pagination: `?page=1&per_page=20` (maks 100). Response list:

```json
{ "data": [ ... ], "meta": { "page": 1, "per_page": 20, "total": 137 } }
```

Error konsisten:

```json
{ "error": { "code": "validation_failed", "message": "Data tidak valid",
             "fields": { "email": "Format email tidak valid" } } }
```

Kode HTTP: 400 (malformed), 401 (belum login/token invalid), 403 (role tidak berhak), 404, 409 (konflik/relasi), 422 (validasi), 429 (rate limit), 500.

Validasi wajib di server: email format & unik, password minimal 8 karakter, nominal > 0, tanggal jatuh tempo ≥ tanggal terbit, item invoice minimal 1, assignment maksimal 1 lead, status enum valid.

---

## 8. Frontend

Routes:

| Route | Akses | Isi |
|---|---|---|
| `/login` | publik | form login |
| `/dashboard` | semua | kartu & grafik sesuai role |
| `/attorneys` | semua | tabel + aksi sesuai role |
| `/attorneys/new`, `/attorneys/:id/edit` | Direktur, CS | form |
| `/clients` | semua | tabel |
| `/clients/:id` | semua | detail + kasus |
| `/clients/new`, `/clients/:id/edit` | Direktur, CS | form |
| `/cases` | semua | tabel + filter + toggle "Kasus Saya" |
| `/cases/:id` | semua | tab Info / Tim / Invoice (conditional) |
| `/cases/new`, `/cases/:id/edit` | Direktur, CS, Lawyer | form |
| `/invoices` | Direktur, Finance, CS | tabel |
| `/invoices/:id` | Direktur, Finance, CS | detail + pembayaran (aksi jika berhak) |
| `/invoices/new`, `/invoices/:id/edit` | Direktur, Finance | form |
| `/users` | Direktur | tabel akun |
| `/profile` | semua | ganti password |

Komponen bersama: `RoleGuard`, `DataTable` (search, sort, pagination), `StatusBadge`, `ConfirmDialog`, `MoneyInput`, `DateInput`, `Toast`, `EmptyState`, `PageHeader`.

Perilaku UI:

- Menu sidebar difilter berdasarkan role.
- 403 menampilkan halaman "Akses ditolak", bukan redirect diam-diam.
- Setelah mutasi, query terkait di-invalidate (angka dashboard ikut segar).
- Format Rupiah `Rp 1.250.000` dan tanggal `17 Nov 2026`.
- Form menampilkan error per field dari response 422.
- Konfirmasi sebelum hapus/void.

---

## 9. Dashboard

`GET /dashboard/summary` mengembalikan bentuk berbeda per role:

**Direktur**

- `attorneys_total`, `clients_total`, `cases_active`, `cases_closed`
- `revenue_this_month`, `outstanding_total`
- `cases_by_status` (chart), `cases_by_type` (chart)
- `top_lawyers` (nama + jumlah kasus), `recent_cases`

**CS/Admin**

- `attorneys_total`, `clients_total`, `cases_active`
- `deadlines_next_30_days`
- `recent_cases` (10 terakhir diperbarui)

**Finance**

- `invoiced_total`, `paid_total`, `outstanding_total`, `overdue_count`
- `revenue_last_6_months` (chart)
- `overdue_invoices` (10 teratas)

**Lawyer**

- `my_cases_by_status` (chart)
- `my_upcoming_deadlines`
- `my_recently_updated`

Definisi: `cases_active` = status `open` + `in_progress`; `outstanding_total` = sisa tagihan invoice `sent` (bukan void); `overdue` = `due_date` < hari ini dan sisa > 0.

---

## 10. Auth & Keamanan

- Password di-hash bcrypt (cost 12).
- JWT HS256, klaim `sub` (user id), `role`, `iat`, `exp` (8 jam); disimpan di cookie `session`, `HttpOnly`, `SameSite=Lax`, `Secure` di produksi.
- Secret JWT minimal 32 byte dari environment; aplikasi menolak start bila kosong/terlalu pendek.
- Middleware auth memuat ulang user dari DB: akun nonaktif → 401; role diambil dari DB (bukan hanya klaim).
- Otorisasi per endpoint dengan daftar role eksplisit; default deny.
- Query parameterized; tidak ada string SQL dari input.
- Rate limit login in-memory (5/menit/IP).
- Pesan login tidak membocorkan keberadaan email.
- Tidak ada rahasia di repo; `.env.example` tanpa nilai asli.
- Log auth gagal & perubahan akun (slog, tanpa password).
- CSRF dimitigasi dengan `SameSite=Lax` + API JSON same-origin (frontend di-embed, tanpa CORS lintas domain).

---

## 11. Deployment & Operasional

- `Dockerfile` multi-stage: `node:20` build React → `golang:1.22` build + embed `web/dist` → image runtime kecil (alpine/distroless).
- `docker-compose.yml`: `app`, `db` (mysql:8), `caddy`.
- Caddy mengarahkan domain ke `app:8080`, TLS otomatis.
- Volume MySQL persisten; `healthcheck` untuk db dan app.
- Migrasi SQL dijalankan saat startup dengan `GET_LOCK` agar aman dari race; idempoten.
- Seed Direktur bila tabel `users` kosong: `SEED_DIRECTOR_EMAIL`, `SEED_DIRECTOR_PASSWORD`.
- `.env`: `DB_DSN`, `JWT_SECRET`, `APP_ENV`, `SEED_DIRECTOR_*`, `COOKIE_SECURE`.
- Backup: skrip `mysqldump` harian via cron host, retensi 7 harian + 4 mingguan; uji restore sebelum go-live.
- Log JSON ke stdout; rotasi ditangani Docker/host.
- `/healthz` mengecek koneksi DB.
- Graceful shutdown (SIGTERM), koneksi DB ditutup rapi.
- Monitoring gratis opsional (UptimeRobot) ke `/healthz`.

---

## 12. Testing

Backend:

- Unit test middleware RBAC (setiap role × endpoint contoh).
- Unit test perhitungan status invoice & sisa tagihan.
- Handler test dengan `httptest` + store tiruan: validasi, 401/403/409/422.
- Integration test dengan MySQL container (`docker compose` profil test): migrasi, login, CRUD kasus, pembayaran, dan agregasi dashboard.
- `go vet ./...` dan `go test ./...` wajib hijau.

Frontend:

- Vitest + RTL: route guard per role, validasi form, render tabel & empty state, format Rupiah/tanggal.
- `npm run build` tanpa TypeScript error.
- Checklist manual per role (login, hak menu, CRUD, dashboard, invoice) sebelum rilis.

Kriteria rilis: seluruh test hijau, checklist per role lulus, backup & restore teruji, akun seed diganti password.

---

## 13. Acceptance Criteria (ringkas)

1. Empat role bisa login; menu & data sesuai matriks akses; akses langsung ke URL terlarang mendapat 403.
2. Direktur bisa menambah/mengubah/menonaktifkan user dan reset password; akun nonaktif tidak bisa login.
3. Attorney, klien, dan kasus mendukung CRUD sesuai role, pencarian, filter, pagination, dan aturan hapus (409 bila terikat).
4. Kasus punya nomor unik, tim assignment (1 lead), filter "Kasus Saya" untuk Lawyer.
5. Invoice punya item, total dihitung server, status bayar benar (unpaid/partial/paid/overdue), pembayaran tidak melebihi sisa, void hanya tanpa pembayaran.
6. Dashboard menampilkan angka yang benar dan berbeda per role.
7. Semua endpoint menolak akses tidak sah di server, bukan hanya UI.
8. Deploy satu perintah Compose; TLS aktif; backup harian berjalan.

---

## 14. Di Luar Scope (MVP)

Manajemen dokumen, kalender sidang tersinkron, notifikasi email/WhatsApp, portal klien, multi-firma/multi-tenant, time tracking, akuntansi penuh, pajak otomatis, mobile app, audit trail lengkap (hanya log aplikasi), integrasi pembayaran online.

---

## 15. Deliverable & Tahapan

1. **Spec ini** — markdown untuk tech stack & fitur (poin 4).
2. **Slide PPT** 10–14 halaman, Bahasa Indonesia, untuk stakeholder internal (poin 3):
   - Judul; latar & tujuan; ringkasan solusi
   - Tech stack & estimasi biaya; arsitektur
   - Matriks akses
   - Highlight per role: Direktur, CS/Admin, Finance, Lawyer
   - Dashboard & counts; keamanan & operasional
   - Tahapan berikutnya
   - Catatan: PPT memakai diagram/mockup berlabel "rancangan", bukan screenshot sistem yang sudah berjalan.
3. **Rencana implementasi** (writing-plans) setelah spec disetujui.
4. **Implementasi kode** bertahap: fondasi + auth → attorney/klien/kasus → finance → dashboard & polish → deploy.

Perkiraan urutan milestone: M1 fondasi & auth; M2 master data; M3 kasus & assignment; M4 finance; M5 dashboard; M6 deploy & hardening.
