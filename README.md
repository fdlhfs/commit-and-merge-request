# Commit Title Validator & Reference Extractor

> Tool Python untuk validasi format commit title dan ekstraksi referensi link sesuai standar perusahaan

## 📖 Tentang Project

Project ini adalah **validator otomatis** yang memastikan setiap commit message dan merge request mengikuti standar format yang telah ditetapkan perusahaan. Tool ini membantu tim development untuk:

- Menjaga konsistensi format commit message
- Memudahkan tracking perubahan code dengan referensi ticket
- Otomatis memberikan saran perbaikan jika format salah
- Ekstraksi link referensi (Taiga, Documentation, Testing) dari deskripsi

### Mengapa Perlu Validator Ini?

Dalam tim development, konsistensi format commit sangat penting untuk:
1. **Tracking & Audit** - Mudah melacak perubahan code ke ticket/issue tertentu
2. **Code Review** - Reviewer langsung tahu konteks perubahan
3. **Release Notes** - Generate changelog otomatis dari commit history
4. **Kolaborasi** - Semua anggota tim mengikuti standar yang sama

## 🎯 Format Standar Commit

### Format Wajib:
```
<tipe>: <ringkasan singkat> (Taiga #<NamaProject>-<NomorTicket>)
```

### Komponen:
- **`<tipe>`** - Jenis perubahan (feat, fix, refactor, dll)
- **`<ringkasan singkat>`** - Deskripsi jelas perubahan (minimal 5 karakter)
- **`(Taiga #<NamaProject>-<NomorTicket>)`** - Referensi ke ticket Taiga

### Contoh Valid:
```
feat: menambahkan fitur login dengan JWT (Taiga #DATB-10353)
fix: memperbaiki bug pada dashboard analytics (Taiga #PROJ-123)
refactor: restructure authentication module (Taiga #AUTH-456)
```

### Contoh Invalid:
```
❌ add login feature                          → Tidak ada tipe & referensi Taiga
❌ feature: add login (Taiga #DATB-10353)    → Tipe salah (harus 'feat' bukan 'feature')
❌ feat:add login (Taiga #DATB-10353)        → Tidak ada spasi setelah ':'
❌ feat: add (Taiga #DATB-10353)             → Ringkasan terlalu pendek
❌ feat: add login (Taiga #datb-10353)       → Project name harus uppercase
```

## ✨ Fitur Utama

### 1. Validasi Otomatis
- Cek format commit title sesuai standar
- Validasi tipe commit (11 tipe tersedia)
- Validasi format referensi Taiga
- Validasi panjang ringkasan (minimal 5 karakter)
- Validasi project name (harus uppercase)

### 2. Auto Suggestion
Jika format salah, tool akan memberikan saran perbaikan:
```python
Title: "add login feature DATB-10353"

Errors:
  - Format salah: Tidak ditemukan tanda ':' setelah tipe
  - Referensi Taiga tidak ditemukan

Suggestions:
  - Saran perbaikan: feat: add login feature (Taiga #DATB-10353)
```

### 3. Reference Extraction
Ekstrak link referensi dari deskripsi commit/MR:
- **Ticket Link** - Link ke Taiga ticket
- **Documentation Link** - Link ke Figma
- **Testing Link** - Link ke test scenarios

### 4. Comprehensive Testing
- 40+ unit tests dengan coverage tinggi
- Test untuk semua edge cases
- Integration tests untuk workflow lengkap

## 🚀 Instalasi & Setup

### Prerequisites
- Python 3.8 atau lebih baru
- Git

### Clone Repository
```bash
git clone https://github.com/fdlhfs/commit-and-merge-request.git
cd commit-and-merge-reques
```

### Tidak Perlu Install Dependencies
Tool ini **hanya menggunakan Python standard library**, tidak ada dependency eksternal yang perlu diinstall.

## 📝 Cara Penggunaan

### 1. Validasi Commit Title (Basic)

```python
from commit_validator import validate_commit_title

# Contoh title yang akan divalidasi
title = "feat: menambahkan fitur login user (Taiga #DATB-10353)"

# Jalankan validasi
result = validate_commit_title(title)

# Cek hasilnya
if result.is_valid:
    print("✅ Title valid!")
    print(f"Tipe: {result.parsed_data['type']}")
    print(f"Ringkasan: {result.parsed_data['summary']}")
    print(f"Project: {result.parsed_data['project']}")
    print(f"Ticket: #{result.parsed_data['ticket_number']}")
else:
    print("❌ Title tidak valid!")
    print("\nErrors:")
    for error in result.errors:
        print(f"  - {error}")
    print("\nSuggestions:")
    for suggestion in result.suggestions:
        print(f"  💡 {suggestion}")
```

### 2. Ekstraksi Referensi dari Deskripsi

```python
from commit_validator import extract_reference_data

# Contoh deskripsi dengan referensi
description = """
Implementasi sistem autentikasi user dengan JWT token

Ticket Link: [(Taiga #DATB-10353)] (https://projects.digitaltelkom.id/project/DATB/us/10353)
Documentation Link: [Figma Design] (https://www.figma.com/design/abc123)
Testing Link: [Test Scenarios] (https://docs.google.com/spreadsheets/test)
"""

# Ekstrak referensi
result = extract_reference_data(description)

# Tampilkan hasil
if result.ticket_link:
    print(f" Ticket: {result.ticket_link['display']}")
    print(f"   URL: {result.ticket_link['url']}")

if result.documentation_link:
    print(f" Documentation: {result.documentation_link['name']}")
    print(f"   URL: {result.documentation_link['url']}")

if result.testing_link:
    print(f" Testing: {result.testing_link['name']}")
    print(f"   URL: {result.testing_link['url']}")
```

### 3. Workflow Lengkap (Validasi + Ekstraksi)

```python
from commit_validator import validate_commit_title, extract_reference_data

# Data commit/merge request
title = "feat: implementasi JWT authentication (Taiga #AUTH-555)"
description = """
Menambahkan sistem autentikasi menggunakan JWT token

Ticket Link: [(Taiga #AUTH-555)] (https://projects.digitaltelkom.id/project/AUTH/us/555)
Documentation Link: [API Specs] (https://swagger.io/docs/auth)
Testing Link: [Test Cases] (https://docs.google.com/spreadsheets/auth-tests)
"""

# 1. Validasi title
title_result = validate_commit_title(title)

if title_result.is_valid:
    print("✅ Title valid!")
    
    # 2. Ekstrak referensi
    ref_result = extract_reference_data(description)
    
    # 3. Tampilkan summary lengkap
    print(f"\n Project: {title_result.parsed_data['project']}")
    print(f" Ticket: #{title_result.parsed_data['ticket_number']}")
    print(f" Ticket URL: {ref_result.ticket_link['url']}")
    print(f" Documentation: {ref_result.documentation_link['url']}")
    print(f" Testing: {ref_result.testing_link['url']}")
else:
    print("❌ Title tidak valid, perbaiki terlebih dahulu:")
    for error in title_result.errors:
        print(f"  - {error}")
```
## 🌐 Web Dashboard

Buka `index.html` di browser untuk menggunakan dashboard interaktif:
```bash
# Buka di browser
open index.html  # Mac
start index.html # Windows
```

**Live Demo:** https://fdlhfs.github.io/commit-and-merge-request/

Dashboard menyediakan:
- Validasi commit title real-time
- Ekstraksi referensi
- Contoh-contoh
- Daftar tipe yang diperbolehkan
  
## 🎮 Demo Interaktif

Jalankan demo untuk melihat berbagai scenario:

```bash
demo.py
```

Demo akan menampilkan:
1. **Valid Titles** - Contoh title yang benar
2. **Invalid Titles** - Contoh title salah + saran perbaikan
3. **Reference Extraction** - Ekstraksi link dari deskripsi
4. **Complete Workflow** - Workflow lengkap validasi + ekstraksi
5. **All Allowed Types** - Daftar semua tipe yang diperbolehkan
6. **Interactive Mode** - Test title Anda sendiri secara interaktif

## 🔎 Testing

### Menjalankan Unit Tests

```bash
# Run semua tests (29 test cases)
python commit_validator_tests.py
```

Output:
```
test_valid_title_feat ... ok
test_valid_title_fix ... ok
test_invalid_empty_title ... ok
test_invalid_type ... ok
...

----------------------------------------------------------------------
Ran 29 tests in 0.075s

OK

================================================================================
TEST SUMMARY
================================================================================
✅ Tests run: 29
✅ Successes: 29
❌ Failures: 0
❌ Errors: 0
================================================================================
```

### Test Coverage

Tests mencakup:
- Validasi format title (8 tests)
- Validasi tipe commit (3 tests)
- Validasi referensi Taiga (4 tests)
- Ekstraksi referensi (11 tests)
- Auto suggestion & edge cases (1 test)
- Integration tests (2 tests)
- **Total: 29 unit tests**
- Edge cases & error handling

## 📋 Tipe Commit yang Diperbolehkan

| Tipe | Deskripsi | Kapan Digunakan | Contoh |
|------|-----------|-----------------|--------|
| **feat** | Fitur baru | Menambahkan fitur/fungsionalitas baru | `feat: menambahkan fitur login (Taiga #DATB-10353)` |
| **fix** | Bug fix | Memperbaiki bug/error | `fix: memperbaiki bug dashboard (Taiga #PROJ-123)` |
| **refactor** | Refactoring | Restructure code tanpa ubah behavior | `refactor: restructure auth module (Taiga #AUTH-456)` |
| **docs** | Dokumentasi | Update dokumentasi/comments | `docs: update API documentation (Taiga #DOC-789)` |
| **style** | Styling | Format code, whitespace, semicolons | `style: format code with prettier (Taiga #STY-111)` |
| **test** | Testing | Menambahkan atau update tests | `test: add unit tests for validator (Taiga #TEST-222)` |
| **chore** | Maintenance | Update dependencies, config, dll | `chore: update package dependencies (Taiga #CHR-333)` |
| **perf** | Performance | Optimasi performance | `perf: optimize database queries (Taiga #PERF-444)` |
| **ci** | CI/CD | Update CI/CD pipeline/workflow | `ci: update GitHub Actions config (Taiga #CI-555)` |
| **build** | Build System | Update build config/tools | `build: update webpack configuration (Taiga #BLD-666)` |
| **revert** | Revert | Revert commit sebelumnya | `revert: revert feature X (Taiga #REV-777)` |

## 📂 Struktur Project

```
commit-validator/
├── README.md                     # Dokumentasi
├── commit_validator.py           # Core validator & extractor
├── commit_validator_tests.py     # Unit tests (29 tests)
└── demo.py                       # Demo & examples interaktif
```

## ❓ FAQ (Frequently Asked Questions)

**Q: Apakah wajib menggunakan format ini?**  
A: Tergantung kebijakan tim/perusahaan. Tool ini membantu enforce standar jika tim memutuskan menggunakannya.

**Q: Bagaimana jika ticket belum ada di Taiga?**  
A: Sebaiknya buat ticket terlebih dahulu sebelum coding. Jika urgent, gunakan placeholder ticket dan update nanti.

**Q: Apakah case sensitive?**  
A: Ya. Tipe harus lowercase (`feat` bukan `Feat`), project name harus uppercase (`DATB` bukan `datb`).

**Q: Bagaimana jika commit untuk multiple tickets?**  
A: Gunakan ticket utama di title. Mention ticket lain di description/body commit message.

## 🤝 Contributing

Kontribusi sangat diterima! Berikut cara berkontribusi:

1. Fork repository ini
2. Buat branch untuk fitur baru (`git checkout -b feature/NewFeature`)
3. Commit perubahan (`git commit -m 'feat: add new feature (Taiga #PROJ-123)'`)
4. Push ke branch (`git push origin feature/NewFeature`)
5. Buat Pull Request

### Guidelines:
- Pastikan semua tests passed: `python commit_validator_tests.py`
- Tambahkan tests untuk fitur baru
- Update dokumentasi jika perlu
- Follow format commit yang sudah ditentukan

## 👥 Author

**Your Name**
- GitHub: [@fdlhfs](https://github.com/fdlhfs)
- Email: fadillah.fajrisani01@gmail.com

---

**Made with ❤️ for better commit messages and cleaner Git history**
