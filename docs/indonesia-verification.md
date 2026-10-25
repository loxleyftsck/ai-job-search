# Hasil penyesuaian pencarian kerja Indonesia

Tanggal: 24 Oktober 2026
Lokasi: D:\ai-job\ai-job-search
Branch: codex/indonesia-job-search
Status: implementasi selesai. Tujuan publikasi: [branch pembaruan di fork GitHub](https://github.com/loxleyftsck/ai-job-search/tree/codex/indonesia-job-search).

## Yang berubah

1. Lowongan dengan perusahaan/jabatan sama di kota berbeda yang diketahui tetap dapat disimpan. Riwayat dan kunci lama dipertahankan; tabrakan kunci baru mendapat pembeda dari URL.
2. Keputusan lokasi, bahasa, dan kelayakan yang tidak tersedia ditandai FLAG dengan alasan yang tersimpan, bukan dianggap lolos. FAIL/FLAG lama tidak hilang ketika penilaian baru tidak memberikan keputusan; PASS eksplisit dapat memperbaruinya.
3. Konflik syarat wajib seperti kontrak atau rentang gaji seluruhnya di bawah minimum yang benar-benar dikonfirmasi dapat mengecualikan lowongan meskipun skor kecocokannya tinggi, melalui eligibility_gate dan eligibility_note.
4. Satu panduan Indonesia dipakai oleh setup, pencarian, ranking, dan pembuatan lamaran: lokasi/relokasi/remote, jenjang pendidikan dan pengalaman, magang/fresh graduate, kontrak, bahasa, gaji IDR beserta periode/basis, informasi yang belum diketahui dan verifikasi rekruter.
5. Template pencarian JobStreet Indonesia, Glints, Dealls, Kalibrr Indonesia, LinkedIn, dan laman karier perusahaan tersedia. Portal tanpa CLI memakai pencarian web dan verifikasi halaman; Freehire dibatasi ke kebutuhan teknologi yang relevan.
6. Deteksi bahasa lamaran mencakup Bahasa Indonesia dan lowongan campuran, bukan hanya Denmark/Inggris. Instruksi bahasa dari pemberi kerja diutamakan; pilihan bahasa CV tetap milik kandidat.

## Bukti verifikasi

- 846 pengujian Python: 831 lulus, 15 dilewati, tanpa kegagalan/error.
- Pengujian regresi diamati gagal sebelum perbaikan untuk kasus antar-kota, keputusan kosong dan veto syarat wajib.
- Pemeriksaan versi framework, keamanan konfigurasi dan kebersihan diff lulus.
- Review independen dan uji ulang contoh perilaku selesai; temuan penting dan minor sudah ditangani.
- 15 pengujian dilewati: 6 membutuhkan PyYAML, 7 khusus template upstream, 2 membutuhkan hak symlink Windows. Lint khusus belum dijalankan karena PyYAML belum tersedia.

## Batas yang tetap perlu diketahui

- Integrasi portal lokal berupa pencarian web/fetch, bukan scraper/API baru yang telah diuji langsung. Akses portal bisa dibatasi; kegagalan sumber harus dilaporkan.
- CLI portal berbasis Bun belum diuji langsung di lingkungan ini. Uji LinkedIn sebelumnya mendapat HTTP 429.
- Deduplikasi lokasi belum melakukan geocoding/penyamaan alias. Tracker lama tetap mengecualikan perusahaan + jabatan lintas lokasi secara konservatif karena belum memiliki kolom lokasi terstruktur.
- Penilaian syarat wajib dan gaji berasal dari bukti posting + profil yang dibaca asisten; helper menegakkan verdict, bukan parser gaji otomatis atau model prediksi peluang diterima.
- Profil kandidat belum diisi. Sebelum pencarian pribadi, tentukan fungsi/jabatan, kota/remote, preferensi kontrak dan gaji, serta bahasa dari data yang kamu berikan.

Panduan utama: .claude/skills/job-application-assistant/10-indonesia-market.md
Rancangan dan rekam implementasi: docs/superpowers/

## Pengembangan lanjutan: generator rencana pencarian

Generator `tools/indonesia_search_plan.py` sudah terhubung ke tahap persiapan `/scrape`.

- Menerima jabatan/lokasi berulang, level, mode kerja dan pilihan sumber teknologi; menolak placeholder, input kosong, kontrol tak terlihat dan tanda baca tanpa istilah.
- Menghasilkan query JobStreet, Glints, Dealls, Kalibrr, LinkedIn dan Freehire opsional. Argumen CLI disediakan hanya bila Bun dan file CLI tersedia; tanpa itu memakai jalur WebSearch.
- Menghormati portal yang dinonaktifkan, membatasi jumlah pencarian, menampilkan sisa query dan offset lanjutan. Freehire memakai satu pencarian country ID per jabatan; lokasi yang diminta tetap diperiksa setelah fetching.
- Remote memakai cakupan Indonesia tanpa membatasi pada kota asal kandidat. Kelayakan Indonesia, level, kontrak, gaji dan tanggal tetap diverifikasi setelah hasil ditemukan.
- Generator hanya mencetak rencana JSON/teks. Ia tidak mengirim permintaan jaringan, menjalankan perintah portal atau mengubah profil/riwayat.

Verifikasi lanjutan: 14 pengujian generator lulus. Seluruh suite repo: 860 pengujian, 845 lulus, 15 dilewati, tanpa kegagalan/error. Pemeriksaan versi framework, keamanan dan diff lulus. Review ulang menyatakan kedua temuan sudah terselesaikan. Keterbatasan PyYAML dan pengujian portal langsung pada bagian sebelumnya tetap berlaku.

Contoh pemakaian dan parameter ada di README.md serta panduan pasar Indonesia. Perubahan dikembangkan pada branch `codex/indonesia-job-search`.

## Publikasi GitHub — 25 Oktober 2026

Repo asal `ai-job-search-dev/ai-job-search` memberi akun yang terhubung akses baca. Hasil pembaruan diarahkan ke fork `loxleyftsck/ai-job-search`; repo asal dipertahankan sebagai `upstream`. Branch pembaruan adalah `codex/indonesia-job-search`.
